import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse
import subprocess
import os

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="カスタムモデルを生成します。\n\n"
        "このスクリプトは指定された音声ファイルを分割し、"
        "指定されたディレクトリにコピーします。"
    )
    parser.add_argument("arg", nargs="?", help="引数")
    parser.add_argument(
        "--model-name", required=True, help="[REQUIRED] モデル名を指定します。"
    )
    parser.add_argument(
        "--copy-source-raw-directory",
        help="[OPTION] 元になる音声ファイル（mp3, wav など）のパスを指定するディレクトリを指定します。",
    )
    parser.add_argument(
        "--file-copy-only",
        action="store_true",
        help="[OPTION] ファイルコピーのみを実行します。",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="[OPTION] 分割の開始位置（秒）。デフォルトは 0 です。",
    )
    parser.add_argument(
        "--term",
        type=int,
        default=30,
        help="[OPTION] 分割の間隔（秒）。デフォルトは 30 です。",
    )
    parser.add_argument(
        "--overlay",
        type=int,
        default=5,
        help="[OPTION] 分割の重なり（秒）。デフォルトは 5 です。",
    )
    return parser


if __name__ == "__main__":
    parser = parse_arguments()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    create_and_copy_data.main(args)
    if args.file_copy_only:
        sys.exit(0)

    # separate.py を実行して音声データを分割
    raw_dir = f"./data/raw/{args.model_name}"
    separate_dir = os.path.join(raw_dir, "separate")
    os.makedirs(separate_dir, exist_ok=True)

    for file in sorted(os.listdir(raw_dir)):
        if file.endswith((".mp3", ".wav")):
            input_file = os.path.join(raw_dir, file)
            subprocess.run([
                "python", "scripts/separate.py",
                "--input", input_file,
                "--output", separate_dir,
                "--start", str(args.start),
                "--interval", str(args.term),
                "--duration", str(args.term + args.overlay)
            ])
