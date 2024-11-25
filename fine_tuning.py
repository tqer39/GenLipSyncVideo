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
        "--model-name", type=str, required=True, help="Name of the model to fine-tune"
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


def build_dataset(input_dir: str, output_dir: str) -> None:
    """
    データセットを構築します。
    """
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "python",
        "tools/llama/build_dataset.py",
        "--input",
        input_dir,
        "--output",
        output_dir,
        "--text-extension",
        ".lab",
        "--num-workers",
        "16",
    ]
    subprocess.run(command, check=True)


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。コマンドライン引数を解析し、fine tuning の処理を実行します。
    """
    if args is None:
        args = parse_arguments()

    target_dir = args.override_path or f"./data/{args.model_name}/before_text_reformatting"
    output_dir = f"./data/{args.model_name}/protobuf"
    finetune(target_dir)
    build_dataset(target_dir, output_dir)


if __name__ == "__main__":
    main()
