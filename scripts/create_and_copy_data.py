import os
import argparse
import shutil
from argparse import Namespace


def parse_arguments() -> Namespace:
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="音声ファイルを指定のディレクトリにコピーします。"
    )
    # [REQUIRED] 引数
    parser.add_argument(
        "--model-name", required=True, help="[REQUIRED] コピー先のディレクトリ名"
    )

    # [OPTION] 引数
    parser.add_argument(
        "--copy-source-raw-directory",
        help="[OPTION] 元になる音声ファイル（mp3, wav など）のパスを指定するディレクトリ",
    )
    parser.add_argument(
        "--force-file-copy",
        action="store_true",
        help="[OPTION] 同名のファイルがある場合に強制的に上書きします。",
    )
    return parser.parse_args()


def main(args=None):
    """
    メイン関数。音声ファイルを指定のディレクトリにコピーします。
    """
    if args is None:
        args = parse_arguments()

    if args.copy_source_raw_directory:
        raw_dir = os.path.join(f"./data/{args.model_name}", "raw")
        os.makedirs(raw_dir, exist_ok=True)
        for file in os.listdir(args.copy_source_raw_directory):
            if file.endswith((".mp3", ".wav")):
                dest_file = os.path.join(raw_dir, file)
                if os.path.exists(dest_file) and not args.force_file_copy:
                    print(f"スキップされたファイル: {dest_file}（既に存在します）")
                else:
                    shutil.copy(
                        os.path.join(args.copy_source_raw_directory, file), dest_file
                    )
                    print(f"コピーされたファイル: {dest_file}")


if __name__ == "__main__":
    main()
