import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse


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
    # ...additional processing code...
