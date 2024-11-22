import os
import argparse
from argparse import Namespace
from typing import Optional
import whisper


def parse_arguments() -> Namespace:
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="音声ファイルからテキストデータを抽出し、同名の .lab ファイルに保存します。"
    )
    parser.add_argument(
        "--input-dir", required=True, help="[REQUIRED] 入力音声ファイルのディレクトリ"
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="[REQUIRED] 出力テキストファイルのディレクトリ",
    )
    return parser.parse_args()


def speech_to_text(input_file: str) -> str:
    """
    音声ファイルからテキストデータを抽出します。
    """
    model = whisper.load_model("base")
    result = model.transcribe(input_file, language="ja")
    return result["text"]


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。音声ファイルからテキストデータを抽出し、同名の .lab ファイルに保存します。
    """
    if args is None:
        args = parse_arguments()

    os.makedirs(args.output_dir, exist_ok=True)

    for file in sorted(os.listdir(args.input_dir)):
        if file.endswith((".mp3", ".wav")):
            input_file: str = os.path.join(args.input_dir, file)
            output_file: str = os.path.join(
                args.output_dir, os.path.splitext(file)[0] + ".lab"
            )
            text: str = speech_to_text(input_file)
            with open(output_file, "w") as f:
                f.write(text)
            print(f"テキストデータを保存しました: {output_file}")


if __name__ == "__main__":
    main()
