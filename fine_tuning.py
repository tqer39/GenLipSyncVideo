import subprocess
import os
from typing import Optional
import sys
import argparse
from argparse import Namespace


def parse_arguments() -> argparse.Namespace:
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="Fine-tuning script for GenLipSyncVideo"
    )
    parser.add_argument(
        "--model_name", type=str, required=True, help="Name of the model to fine-tune"
    )
    parser.add_argument(
        "--finetune-only",
        action="store_true",
        help="[OPTION] finetune の処理のみを実行します。",
    )
    parser.add_argument(
        "--override-path",
        help="[OPTION] 処理対象のディレクトリを指定します。デフォルトは './data/{model_name}/before_text_reformatting' です。",
    )
    return parser.parse_args()


def finetune(finetune_dir: str) -> None:
    """
    finetune フォルダ内で処理を実行します。
    """
    command = [
        "python",
        "tools/vqgan/extract_vq.py",
        finetune_dir,
        "--num-workers",
        "1",
        "--batch-size",
        "16",
        "--config-name",
        "firefly_gan_vq",
        "--checkpoint-path",
        "checkpoints/fish-speech-1.4/firefly-gan-vq-fsq-8x1024-21hz-generator.pth",
    ]
    subprocess.run(command, check=True)


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。コマンドライン引数を解析し、音声ファイルのコピーと分割を実行します。
    """
    if args is None:
        args = parse_arguments()
    finetune_dir: str = os.path.join(
        f"./data/{args.model_name}", "before_text_reformatting"
    )
    os.makedirs(finetune_dir, exist_ok=True)

    if args.finetune_only:
        finetune(finetune_dir)

        sys.exit(0)

    target_dir = (
        args.override_path or f"./data/{args.model_name}/before_text_reformatting"
    )
    finetune(target_dir)
