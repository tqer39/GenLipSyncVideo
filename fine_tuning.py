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
        "--create-semantic-token-only",
        action="store_true",
        help="[OPTION] create_semantic_token の処理のみを実行します。",
    )
    parser.add_argument(
        "--create-protobuf-only",
        action="store_true",
        help="[OPTION] create_protobuf の処理のみを実行します。",
    )
    parser.add_argument(
        "--training-only",
        action="store_true",
        help="[OPTION] training の処理のみを実行します。",
    )
    parser.add_argument(
        "--force-create-semantic-token",
        action="store_true",
        help="[OPTION] 既存の npy ファイルがある場合に強制的に上書きします。",
    )
    parser.add_argument(
        "--force-create-protobuf",
        action="store_true",
        help="[OPTION] 既存の protos ファイルがある場合に強制的に上書きします。",
    )
    parser.add_argument(
        "--override-path",
        help="[OPTION] 処理対象のディレクトリを指定します。デフォルトは './data/{model_name}/before_text_reformatting' です。",
    )
    return parser.parse_args()


def create_semantic_token(finetune_dir: str, force: bool) -> None:
    """
    create_semantic_token フォルダ内で処理を実行します。
    """
    if force:
        for file in os.listdir(finetune_dir):
            if file.endswith(".npy"):
                os.remove(os.path.join(finetune_dir, file))
                print(f"削除されたファイル: {file}")

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


def create_protobuf(input_dir: str, output_dir: str, force: bool) -> None:
    """
    データセットを構築します。
    """
    if force:
        for file in os.listdir(output_dir):
            if file.endswith(".protos"):
                os.remove(os.path.join(output_dir, file))
                print(f"削除されたファイル: {file}")

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


def training(project: str) -> None:
    """
    モデルをトレーニングします。
    """
    command = [
        "python",
        "fish_speech/train.py",
        "--config-name",
        "text2semantic_finetune",
        f"project={project}",
        "+lora@model.model.lora_config=r_8_alpha_16",
    ]
    subprocess.run(command, check=True)


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。コマンドライン引数を解析し、fine tuning の処理を実行します。
    """
    if args is None:
        args = parse_arguments()

    target_dir = (
        args.override_path or f"./data/{args.model_name}/before_text_reformatting"
    )
    output_dir = f"./data/{args.model_name}/protobuf"

    # セマンティックトークンの作成のみを実行
    if args.create_semantic_token_only:
        create_semantic_token(target_dir, args.force_create_semantic_token)
        sys.exit(0)

    # protobuf の作成のみを実行
    if args.create_protobuf_only:
        create_protobuf(target_dir, output_dir, args.force_create_protobuf)
        sys.exit(0)

    # training のみを実行
    if args.training_only:
        training(args.model_name)
        sys.exit(0)

    # すべての処理を実行
    create_semantic_token(target_dir, args.force_create_semantic_token)
    create_protobuf(target_dir, output_dir, args.force_create_protobuf)
    training(args.model_name)


if __name__ == "__main__":
    main()
