import argparse
from pathlib import Path
from typing import Optional
import shutil
import subprocess


def get_audio_duration(file_path: Path) -> int:
    """
    ffmpeg を使用して音声ファイルの長さを取得します。

    Args:
        file_path (Path): 音声ファイルのパス。

    Returns:
        int: 音声ファイルの長さ（秒単位）。
    """
    result = subprocess.run(
        [
            "ffprobe",
            "-i",
            str(file_path),
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    duration = result.stdout.strip()
    return int(float(duration)) if duration else 0


def clean_audio(file_path: Path, output_path: Path) -> None:
    """
    fap を使用して音声データをクリーンアップします。

    Args:
        file_path (Path): 元の音声データファイル。
        output_path (Path): クリーンアップされた音声データの保存先。
    """
    cmd = ["fap", "clean", str(file_path), "-o", str(output_path)]
    subprocess.run(cmd, check=True)
    print(f"クリーンアップされた音声データを生成しました: {output_path}")


def generate_text(file_path: Path) -> Path:
    """
    音声データからテキストデータを生成します。

    Args:
        file_path (Path): 音声データファイルのパス。

    Returns:
        Path: 生成されたテキストデータファイルのパス。
    """
    text_file = file_path.with_suffix(".txt")
    cmd = ["fap", "transcribe", str(file_path), "-o", str(text_file)]
    subprocess.run(cmd, check=True)
    print(f"テキストデータを生成しました: {text_file}")
    return text_file


def validate_generated_text(file_path: Path) -> bool:
    """
    生成されたテキストデータの内容を確認します。

    Args:
        file_path (Path): テキストデータファイルのパス。

    Returns:
        bool: テキストデータが正しい場合は True、問題がある場合は False。
    """
    with file_path.open("r", encoding="utf-8") as f:
        content = f.read()
        if not content.strip():  # 空のテキストデータは無効とみなす
            print(f"警告: テキストデータが空です: {file_path}")
            return False
    print(f"テキストデータは有効です: {file_path}")
    return True


def split_audio_files(
    model_name: str, start: int, term: int, overlay: int, force: bool = False
) -> None:
    """
    音声データを指定の条件で分割し、保存します。

    Args:
        model_name (str): モデル名。
                          `./data/raw/model_name/{model_name}` 配下の音声データを対象とします。
        start (int): 分割の開始時間（秒）。
        term (int): 分割するデータの長さ（秒）。
        overlay (int): 分割の重なり間隔（秒）。
        force (bool): 分割済みファイルの上書きを許可するか。
    """
    base_path = Path(f"./data/raw/model_name/{model_name}")
    separate_dir = base_path / "separate"
    separate_dir.mkdir(parents=True, exist_ok=True)

    # 音声ファイルの処理（wav と mp3 を対象にファイル名で昇順ソート）
    audio_files = sorted(
        file for ext in ("*.wav", "*.mp3") for file in base_path.glob(ext)
    )

    for audio_file in audio_files:
        print(f"処理中のファイル: {audio_file}")
        duration = start
        file_counter = 1

        # 元の音声ファイルの長さを取得
        audio_duration = get_audio_duration(audio_file)

        while duration < audio_duration:
            output_filename = (
                f"{audio_file.stem}_{duration // 3600:02d}-{(duration % 3600) // 60:02d}-{duration % 60:02d}"
                f"-{(duration + term) // 3600:02d}-{((duration + term) % 3600) // 60:02d}-{(duration + term) % 60:02d}"
                f"_{file_counter:05d}{audio_file.suffix}"
            )
            output_file = separate_dir / output_filename

            if not force and output_file.exists():
                print(f"スキップ: ファイルが既に存在します: {output_file}")
            else:
                # ffmpeg を使用して分割
                cmd = [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(audio_file),
                    "-ss",
                    str(duration),
                    "-t",
                    str(term),
                    str(output_file),
                ]
                subprocess.run(cmd, check=True)
                print(f"生成されたファイル: {output_file}")

                # 音声をクリーンアップ
                cleaned_file = output_file.with_name(f"cleaned_{output_file.name}")
                clean_audio(output_file, cleaned_file)

                # テキストデータを生成
                text_file = generate_text(cleaned_file)

                # テキストデータの確認
                if not validate_generated_text(text_file):
                    print(
                        f"エラー: テキストデータが無効です。再生成が必要です: {text_file}"
                    )

            file_counter += 1
            duration += term - overlay


def main():
    """
    引数を受け取り、データディレクトリの作成とコピー処理、音声分割を実行します。
    """
    parser = argparse.ArgumentParser(
        description="カスタムモデルのデータ構造を生成し、音声データを分割します。"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help="コピー先のサブディレクトリ名。`./data/raw/model_name` 内に作成されます。",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="分割の開始時間（秒）。デフォルトは 0。",
    )
    parser.add_argument(
        "--term",
        type=int,
        default=30,
        help="分割するデータの長さ（秒）。デフォルトは 30 秒。",
    )
    parser.add_argument(
        "--overlay",
        type=int,
        default=5,
        help="分割の重なり間隔（秒）。デフォルトは 5 秒。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="既存のファイルや分割済みファイルを上書きします。",
    )

    args = parser.parse_args()

    try:
        # 音声分割を実行
        split_audio_files(
            model_name=args.model_name,
            start=args.start,
            term=args.term,
            overlay=args.overlay,
            force=args.force,
        )
        print("処理が完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
