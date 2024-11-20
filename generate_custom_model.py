import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="カスタムモデルを生成します。\n\n"
        "このスクリプトは指定された音声ファイルを分割し、"
        "指定されたディレクトリにコピーします。\n"
        "オプション:\n"
        "  --model-name: モデル名を指定します。\n"
        "  --copy-source-raw-directory: 元になる音声ファイル（mp3, wav など）のパスを指定するディレクトリを指定します。\n"
    )
    parser.add_argument("arg", nargs="?", help="引数")
    parser.add_argument("--model-name", required=True, help="モデル名")
    parser.add_argument(
        "--copy-source-raw-directory",
        help="元になる音声ファイル（mp3, wav など）のパスを指定するディレクトリ",
    )
    return parser


if __name__ == "__main__":
    parser = parse_arguments()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    create_and_copy_data.main(
        [
            "--model-name",
            args.model_name,
            "--copy-source-raw-directory",
            args.copy_source_raw_directory,
        ]
    )
