import os
import shutil
import argparse
from argparse import Namespace
from typing import Optional


def parse_arguments() -> Namespace:
    """
    コマンドライン引数を解析します。
    """
    parser = argparse.ArgumentParser(
        description="fine tuning 前のデータセットを作成します。"
    )
    parser.add_argument(
        "--model-name", required=True, help="[REQUIRED] モデル名を指定します。"
    )
    parser.add_argument(
        "--force-before-text-reformatting",
        action="store_true",
        help="[OPTION] before_text_reformatting を強制します。",
    )
    return parser.parse_args()


def prepare_before_text_reformatting(model_name: str, force: bool) -> None:
    """
    fine tuning 前のデータセットを作成します。
    """
    before_text_reformatting_dir = os.path.join(
        f"./data/{model_name}", "before_text_reformatting"
    )
    normalize_dir = os.path.join(f"./data/{model_name}", "normalize_loudness")
    transcribe_dir = os.path.join(f"./data/{model_name}", "transcriptions")
    os.makedirs(before_text_reformatting_dir, exist_ok=True)

    for file in sorted(os.listdir(normalize_dir)):
        if file.endswith((".mp3", ".wav")):
            base_name, ext = os.path.splitext(file)
            segment_number = base_name.split("_")[-2]
            time_part = base_name.split("_")[-1]
            segment_dir = os.path.join(
                before_text_reformatting_dir, f"{segment_number}_{time_part}"
            )
            os.makedirs(segment_dir, exist_ok=True)

            audio_src = os.path.join(normalize_dir, file)
            audio_dest = os.path.join(segment_dir, file)
            text_src = os.path.join(transcribe_dir, f"{base_name}.lab")
            text_dest = os.path.join(segment_dir, f"{base_name}.lab")

            if os.path.exists(audio_dest) and not force:
                print(f"スキップされた音声ファイル: {audio_dest}（既に存在します）")
            else:
                shutil.copy(audio_src, audio_dest)
                print(f"コピーされた音声ファイル: {audio_dest}")

            if os.path.exists(text_dest) and not force:
                print(f"スキップされたテキストファイル: {text_dest}（既に存在します）")
            else:
                shutil.copy(text_src, text_dest)
                print(f"コピーされたテキストファイル: {text_dest}")


def main(args: Optional[Namespace] = None) -> None:
    """
    メイン関数。コマンドライン引数を解析し、fine tuning 前のデータセットを作成します。
    """
    if args is None:
        args = parse_arguments()

    prepare_before_text_reformatting(
        args.model_name, args.force_before_text_reformatting
    )


if __name__ == "__main__":
    main()
