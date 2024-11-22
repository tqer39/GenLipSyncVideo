import os
import argparse
import subprocess
from argparse import Namespace
from typing import Optional
from datetime import timedelta


def parse_arguments() -> Namespace:
    parser = argparse.ArgumentParser(
        description="音声ファイルを指定の間隔で分割します。"
    )
    parser.add_argument("--input", required=True, help="入力音声ファイルのパス")
    parser.add_argument("--start", type=int, default=0, help="分割開始時間（秒）")
    parser.add_argument("--interval", type=int, default=30, help="分割間隔（秒）")
    parser.add_argument("--overlay", type=int, default=5, help="分割の重なり（秒）")
    parser.add_argument(
        "--force", action="store_true", help="既存ファイルを強制的に上書きします。"
    )
    return parser.parse_args()


def format_time(seconds: int) -> str:
    td = timedelta(seconds=seconds)
    return str(td)


def generate_output_filename(base_filename: str, segment_number: int, start_time: int, end_time: int, file_extension: str) -> str:
    start_time_str: str = format_time(start_time).replace(":", "-")
    end_time_str: str = format_time(end_time).replace(":", "-")
    return f"{base_filename}_{segment_number:05d}_{start_time_str}~{end_time_str}{file_extension}"


def main(args: Optional[Namespace] = None) -> None:
    if args is None:
        args = parse_arguments()

    input_file: str = args.input
    output_dir: str = os.path.dirname(input_file)
    start_time: int = args.start
    interval: int = args.interval
    overlay: int = args.overlay
    duration: int = interval + overlay
    force: bool = args.force

    # 出力ディレクトリの存在確認
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # 入力ファイルの存在確認
    if not os.path.isfile(input_file):
        print(f"入力ファイルが見つかりません: {input_file}")
        return

    segment_number: int = 1
    current_time: int = start_time

    while True:
        base_filename: str = os.path.splitext(os.path.basename(input_file))[0]
        file_extension: str = os.path.splitext(input_file)[1]
        output_filename: str = generate_output_filename(base_filename, segment_number, current_time, current_time + duration, file_extension)
        output_filepath: str = os.path.join(output_dir, output_filename)

        if os.path.exists(output_filepath):
            if force:
                os.remove(output_filepath)
            else:
                print(f"スキップされたファイル: {output_filepath}（既に存在します）")
                segment_number += 1
                current_time += interval
                continue

        command: list[str] = [
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
