import os
import argparse
import subprocess
from argparse import Namespace


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(
        description="音声ファイルを指定の間隔で分割します。"
    )
    parser.add_argument("--start", type=int, default=0, help="分割開始時間（秒）")
    parser.add_argument("--interval", type=int, default=30, help="分割間隔（秒）")
    parser.add_argument(
        "--duration", type=int, default=35, help="各分割ファイルの長さ（秒）"
    )
    return parser.parse_args()


def main(args=None):
    if args is None:
        args = parse_arguments()

    input_file = args.input
    output_dir = os.path.dirname(input_file)
    start_time = args.start
    interval = args.interval
    duration = args.duration

    # 出力ディレクトリの存在確認
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 入力ファイルの存在確認
    if not os.path.isfile(input_file):
        print(f"入力ファイルが見つかりません: {input_file}")
        return

    segment_number = 1
    current_time = start_time

    while True:
        output_filename = f"{os.path.splitext(os.path.basename(input_file))[0]}_track_{segment_number:03d}.wav"
        output_filepath = os.path.join(output_dir, output_filename)
        command = [
            "ffmpeg",
            "-i",
            input_file,
            "-ss",
            str(current_time),
            "-t",
            str(duration),
            "-c",
            "copy",
            output_filepath,
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            break
        print(f"出力ファイル: {output_filepath}")
        segment_number += 1
        current_time += interval


if __name__ == "__main__":
    main()
