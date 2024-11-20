import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="カスタムモデルを生成します。")
    parser.add_argument("arg", help="引数")
    parser.add_argument("--model-name", required=True, help="モデル名")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    create_and_copy_data.main(["--model-name", args.model_name])
