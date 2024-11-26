import scripts.create_and_copy_data as create_and_copy_data
import scripts.separate as separate
import scripts.speech_to_text as speech_to_text
import scripts.prepare_before_text_reformatting as prepare_before_text_reformatting
import sys
import argparse
import subprocess
import os
from argparse import Namespace
from typing import Optional
import shutil


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
        "--copy-only",
        action="store_true",
        help="[OPTION] ファイルコピーのみを実行します。",
    )
    parser.add_argument(
        "--separate-only",
        action="store_true",
        help="[OPTION] ファイル分割のみを実行します。",
    )
    parser.add_argument(
        "--normalize-only",
        action="store_true",
        help="[OPTION] ファイル正規化のみを実行します。",
    )
    parser.add_argument(
        "--transcribe-only",
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
        "--force-copy",
        action="store_true",
        help="[OPTION] ファイルコピーを強制します。",
    )
    parser.add_argument(
        "--force-separate",
        action="store_true",
        help="[OPTION] ファイル分割を強制します。",
    )
    parser.add_argument(
        "--force-normalize",
        action="store_true",
        help="[OPTION] ラウドネス正規化を強制します。",
    )
    parser.add_argument(
        "--before-text-reformatting-only",
        action="store_true",
        help="[OPTION] before_text_reformatting のみを実行します。",
    )
    parser.add_argument(
        "--force-before-text-reformatting",
        action="store_true",
        help="[OPTION] before_text_reformatting を強制します。",
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
        "--clean",
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
            if os.path.exists(output_file):
                if force:
                    os.remove(output_file)
                else:
                    print(f"スキップされたファイル: {output_file}（既に存在します）")
                    continue
            speech_to_text.main(
                Namespace(
                    input_dir=input_dir,
                    output_dir=output_dir,
                    extension=extension,
                    whisper_model_name=model_name,
                )
            )
            print(f"テキストデータを保存しました: {output_file}")


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

    # ファイルコピーのみを実行
    if args.copy_only:
        if args.copy_source_raw_directory is None:
            print("コピー元のディレクトリが指定されていません。")
            sys.exit(1)
        if not os.path.isdir(args.copy_source_raw_directory):
            print(
                f"指定されたディレクトリが存在しません: {args.copy_source_raw_directory}"
            )
            sys.exit(1)
        if not any(
            os.path.isfile(os.path.join(args.copy_source_raw_directory, f))
            for f in os.listdir(args.copy_source_raw_directory)
        ):
            print(
                f"指定されたディレクトリにファイルが存在しません: {args.copy_source_raw_directory}"
            )
            sys.exit(1)
        create_and_copy_data.main(args)
        sys.exit(0)

    # ファイル分割のみを実行
    if args.separate_only:
        for file in sorted(os.listdir(raw_dir)):
            if file.endswith((".mp3", ".wav")):
                input_file: str = os.path.join(raw_dir, file)
                separate_args = Namespace(
                    input=input_file,
                    output_dir=separate_dir,
                    start=args.start,
                    interval=args.term,
                    overlay=args.overlay,
                    force=args.separate_only,
                )
                separate.main(separate_args)
        sys.exit(0)

    # ファイル正規化のみを実行
    if args.normalize_only:
        if os.path.exists(normalize_flag_file) and not args.force_normalize:
            print("ラウドネス正規化は既に適用されています。")
        else:
            # ラウドネス正規化を適用
            normalize_loudness(separate_dir, normalize_dir, args.loudness_target)
            with open(normalize_flag_file, "w") as f:
                f.write("normalized")
        sys.exit(0)

    # 音声ファイルからテキストデータの抽出のみを実行
    if args.transcribe_only:
        # 音声ファイルからテキストデータを抽出
        transcribe_audio(
            normalize_dir,
            transcribe_dir,
            args.transcription_extension,
            args.force_transcribe,
            args.whisper_model_name,
        )
        sys.exit(0)

    # セマンティックトークンを払い出す前の前処理のみを実行
    if args.before_text_reformatting_only:
        prepare_before_text_reformatting.main(
            Namespace(
                model_name=args.model_name,
                force_before_text_reformatting=args.force_before_text_reformatting,
            )
        )
        sys.exit(0)

    # ファイルコピーから実行
    if args.copy_source_raw_directory is None:
        print("コピー元のディレクトリが指定されていません。")
        sys.exit(1)
    if not os.path.isdir(args.copy_source_raw_directory):
        print(f"指定されたディレクトリが存在しません: {args.copy_source_raw_directory}")
        sys.exit(1)
    if not any(
        os.path.isfile(os.path.join(args.copy_source_raw_directory, f))
        for f in os.listdir(args.copy_source_raw_directory)
    ):
        print(
            f"指定されたディレクトリにファイルが存在しません: {args.copy_source_raw_directory}"
        )
        sys.exit(1)

    # ファイルを分割
    for file in sorted(os.listdir(raw_dir)):
        if file.endswith((".mp3", ".wav")):
            input_file2: str = os.path.join(raw_dir, file)
            separate_args = Namespace(
                input=input_file2,
                output_dir=separate_dir,
                start=args.start,
                interval=args.term,
                overlay=args.overlay,
                force=args.separate_only,
            )
            separate.main(separate_args)

    # ラウドネス正規化を適用
    if os.path.exists(normalize_flag_file) and not args.force_normalize:
        print("ラウドネス正規化は既に適用されています。")
    else:
        normalize_loudness(separate_dir, normalize_dir, args.loudness_target)
        with open(normalize_flag_file, "w") as f:
            f.write("normalized")
            print("ラウドネス正規化を適用しました。")

    # 音声ファイルからテキストデータを抽出
    transcribe_audio(
        normalize_dir,
        transcribe_dir,
        args.transcription_extension,
        args.force_transcribe,
        args.whisper_model_name,
    )

    # before_text_reformatting の準備
    prepare_before_text_reformatting.main(
        Namespace(
            model_name=args.model_name,
            force_before_text_reformatting=args.force_before_text_reformatting,
        )
    )


if __name__ == "__main__":
    main()
