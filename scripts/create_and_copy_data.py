import os
import argparse
from pydub import AudioSegment
from argparse import Namespace


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(
        description="WAVファイルを指定の間隔で分割します。"
    )
    parser.add_argument("--input", help="入力する単一のWAVファイルのパス")
    parser.add_argument(
        "--directory", help="入力する複数のWAVファイルが存在するディレクトリのパス"
    )
    parser.add_argument("--output", required=True, help="出力するディレクトリのパス")
    parser.add_argument("--dmm-id", help="DMM ID（例: d_208302）")
    parser.add_argument("--start", type=int, required=True, help="分割開始時間（秒）")
    parser.add_argument("--interval", type=int, required=True, help="分割間隔（秒）")
    parser.add_argument(
        "--duration", type=int, required=True, help="各分割ファイルの長さ（秒）"
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if not args.input and not args.directory:
        print("エラー: --input または --directory のいずれかを指定してください。")
        return

    input_files = []
    if args.input:
        input_files.append(args.input)
    if args.directory:
        for file in os.listdir(args.directory):
            if file.endswith(".wav"):
                input_files.append(os.path.join(args.directory, file))

    output_dir = args.output
    dmm_id = args.dmm_id
    start_time = args.start * 1000  # ミリ秒に変換
    interval = args.interval * 1000  # ミリ秒に変換
    duration = args.duration * 1000  # ミリ秒に変換

    # 出力ディレクトリの存在確認
    if not os.path.isdir(output_dir):
        print(f"出力ディレクトリが見つかりません: {output_dir}")
        return

    for input_file in input_files:
        # 入力ファイルの存在確認
        if not os.path.isfile(input_file):
            print(f"入力ファイルが見つかりません: {input_file}")
            continue

        # 出力ディレクトリの作成
        output_path = os.path.join(output_dir, dmm_id) if dmm_id else output_dir
        os.makedirs(output_path, exist_ok=True)

        # オーディオファイルの読み込み
        audio = AudioSegment.from_wav(input_file)
        audio_length = len(audio)

        segment_number = 1
        current_time = start_time

        while current_time + duration <= audio_length:
            segment = audio[current_time : current_time + duration]
            output_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_track_{segment_number:03d}.wav"
            output_filepath = os.path.join(output_path, output_filename)
            segment.export(output_filepath, format="wav")
            print(f"出力ファイル: {output_filepath}")
            segment_number += 1
            current_time += interval


if __name__ == "__main__":
    main()
