import scripts.create_and_copy_data as create_and_copy_data
import sys
import argparse
import subprocess
import os
from argparse import Namespace
from typing import Optional


def parse_arguments() -> argparse.ArgumentParser:
    """
    コマンドライン引数を解析します。
    """
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
    parser.add_argument(
        "--file-separate-only",
        action="store_true",
        help="[OPTION] ファイル分割のみを実行します。",
    )
    parser.add_argument(
        "--file-normalize-only",
        action="store_true",
        help="[OPTION] ファイル正規化のみを実行します。",
    )
    parser.add_argument(
        "--file-transcribe-only",
        action="store_true",
        help="[OPTION] 音声ファイルからテキストデータを抽出するのみを実行します。",
    )
    parser.add_argument(
        "--force-transcribe",
        action="store_true",
        help="[OPTION] 既存のテキストファイルがある場合に強制的に上書きします。",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="[OPTION] 分割の開始位置（秒）。デフォルトは 0 です。",
    )
    parser.add_argument(
        "--term",
        type=int,
        default=30,
        help="[OPTION] 分割の間隔（秒）。デフォルトは 30 です。",
    )
    parser.add_argument(
        "--overlay",
        type=int,
        default=5,
        help="[OPTION] 分割の重なり（秒）。デフォルトは 5 です。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="[OPTION] 同名のファイルがある場合に強制的に上書きします。",
    )
    parser.add_argument(
        "--loudness-target",
        type=float,
        default=-23.0,
        help="[OPTION] ラウドネス正規化のターゲット値（dB LUFS）。デフォルトは -23.0 dB LUFS です。"
        "ターゲット値を上げると音量が大きくなり、下げると音量が小さくなります。",
    )
    parser.add_argument(
        "--transcription-extension",
        type=str,
        default="lab",
        help="[OPTION] 出力テキストファイルの拡張子。デフォルトは 'lab' です。",
    )
    parser.add_argument(
        "--whisper-model-name",
        type=str,
        default="base",
        help="[OPTION] Whisper で使用するモデル。デフォルトは 'base' です。",
    )
    parser.add_argument(
        "--force-file-copy",
        action="store_true",
        help="[OPTION] ファイルコピーを強制します。",
    )
    parser.add_argument(
        "--force-file-separate",
        action="store_true",
        help="[OPTION] ファイル分割を強制します。",
    )
    parser.add_argument(
        "--force-normalize-loudness",
        action="store_true",
        help="[OPTION] ラウドネス正規化を強制します。",
    )
    parser.add_argument(
        "--finetune-only",
        action="store_true",
        help="[OPTION] finetune の処理のみを実行します。",
    )
    return parser


def normalize_loudness(input_dir: str, output_dir: str, loudness_target: float) -> None:
    """
    ディレクトリ内の音声ファイルにラウドネス正規化を適用します。
    """
    command = [
        "fap",
        "loudness-norm",
        input_dir,
        output_dir,
        "--overwrite",
        "--loudness",
        str(loudness_target),
    ]
    subprocess.run(command, check=True)


def transcribe_audio(
    input_dir: str, output_dir: str, extension: str, force: bool, model_name: str
) -> None:
    """
    音声ファイルからテキストデータを抽出し、同名のファイルに保存します。
    """
    for file in sorted(os.listdir(input_dir)):
        if file.endswith((".mp3", ".wav")):
            output_file: str = os.path.join(
                output_dir, os.path.splitext(file)[0] + f".{extension}"
            )
            if os.path.exists(output_file) and not force:
                print(f"スキップされたファイル: {output_file}（既に存在します）")
                continue
            command = [
                "python",
                "scripts/speech_to_text.py",
                "--input-dir",
                input_dir,
                "--output-dir",
                output_dir,
                "--extension",
                extension,
                "--whisper-model-name",
                model_name,
            ]
            subprocess.run(command, check=True)


def run_finetune_processing(finetune_dir: str) -> None:
    """
    finetune フォルダ内で処理を実行します。
    """
    command = [
        "python",
        "tools/vqgan/extract_vq.py",
        finetune_dir,
        "--num-workers",
        "1",
        "--batch-size",
        "16",
        "--config-name",
        "firefly_gan_vq",
        "--checkpoint-path",
        "checkpoints/fish-speech-1.4/firefly-gan-vq-fsq-8x1024-21hz-generator.pth",
    ]
    subprocess.run(command, check=True)


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。コマンドライン引数を解析し、音声ファイルのコピーと分割を実行します。
    """
    parser = parse_arguments()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()

    raw_dir: str = f"./data/{args.model_name}/raw"
    separate_dir: str = os.path.join(raw_dir, "separate")
    normalize_dir: str = os.path.join(f"./data/{args.model_name}", "normalize_loudness")
    transcribe_dir: str = os.path.join(f"./data/{args.model_name}", "transcriptions")
    finetune_dir: str = os.path.join(f"./data/{args.model_name}", "finetune")
    os.makedirs(separate_dir, exist_ok=True)
    os.makedirs(normalize_dir, exist_ok=True)
    os.makedirs(transcribe_dir, exist_ok=True)
    os.makedirs(finetune_dir, exist_ok=True)
    normalize_flag_file: str = os.path.join(normalize_dir, ".normalized")

    if args.file_normalize_only:
        if os.path.exists(normalize_flag_file) and not args.force_normalize_loudness:
            print("ラウドネス正規化は既に適用されています。")
        else:
            # ラウドネス正規化を適用
            normalize_loudness(separate_dir, normalize_dir, args.loudness_target)
            with open(normalize_flag_file, "w") as f:
                f.write("normalized")
        sys.exit(0)

    if args.file_transcribe_only:
        # 音声ファイルからテキストデータを抽出
        transcribe_audio(
            normalize_dir,
            transcribe_dir,
            args.transcription_extension,
            args.force_transcribe,
            args.whisper_model_name,
        )
        sys.exit(0)

    if args.finetune_only:
        run_finetune_processing(finetune_dir)
        sys.exit(0)

    if not args.file_separate_only:
        if args.file_copy_only:
            args.force = args.force_file_copy
        create_and_copy_data.main(args)
    if args.file_copy_only:
        sys.exit(0)

    # separate.py を実行して音声データを分割
    for file in sorted(os.listdir(raw_dir)):
        if file.endswith((".mp3", ".wav")):
            input_file: str = os.path.join(raw_dir, file)
            command: list[str] = [
                "python",
                "scripts/separate.py",
                "--input",
                input_file,
                "--output-dir",
                separate_dir,
                "--start",
                str(args.start),
                "--interval",
                str(args.term),
                "--overlay",
                str(args.overlay),
            ]
            if args.force or args.file_separate_only:
                command.append("--force")
            subprocess.run(command)

    if not os.path.exists(normalize_flag_file):
        # ラウドネス正規化を適用
        normalize_loudness(separate_dir, normalize_dir, args.loudness_target)
        with open(normalize_flag_file, "w") as f:
            f.write("normalized")

    # 音声ファイルからテキストデータを抽出
    transcribe_audio(
        normalize_dir,
        transcribe_dir,
        args.transcription_extension,
        args.force_transcribe,
        args.whisper_model_name,
    )

    # 処理継続の確認
    while True:
        user_input = (
            input(
                "処理を継続しますか？ (y/N): finetune フォルダに音声データとテキストデータのセットを保存してから y キーを押してください。"
            )
            .strip()
            .lower()
        )
        if user_input == "y":
            break
        elif user_input == "n" or user_input == "":
            print("処理を中断しました。")
            sys.exit(0)

    # finetune フォルダ内で処理を実行
    run_finetune_processing(finetune_dir)


if __name__ == "__main__":
    main()
