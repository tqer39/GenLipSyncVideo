import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description="カスタムモデルを生成します。")
    parser.add_argument("arg", nargs="?", help="引数")
    parser.add_argument("--model-name", required=True, help="モデル名")
    return parser


if __name__ == "__main__":
    parser = parse_arguments()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    create_and_copy_data.main(["--model-name", args.model_name])
