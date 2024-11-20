import os
import argparse
import shutil
from argparse import Namespace


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(
        description="音声ファイルを指定のディレクトリにコピーします。"
    )
    parser.add_argument(
        "--copy-source-raw-directory",
        help="元になる音声ファイル（mp3, wav など）のパスを指定するディレクトリ",
    )
    parser.add_argument("--model-name", required=True, help="コピー先のディレクトリ名")
    return parser.parse_args()


def main(args=None):
    if args is None:
        args = parse_arguments()

    if args.copy_source_raw_directory:
        raw_dir = os.path.join("./data/raw", args.model_name)
        os.makedirs(raw_dir, exist_ok=True)
        for file in os.listdir(args.copy_source_raw_directory):
            if file.endswith((".mp3", ".wav")):
                shutil.copy(os.path.join(args.copy_source_raw_directory, file), raw_dir)
                print(f"コピーされたファイル: {os.path.join(raw_dir, file)}")


if __name__ == "__main__":
    main()
