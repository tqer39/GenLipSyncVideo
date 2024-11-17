import argparse
from pathlib import Path
from typing import Optional
import shutil
import subprocess
import re


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


def create_and_copy_data(
    model_name: str,
    copy_source_raw_directory: Optional[str] = None,
    force: bool = False,
) -> None:
    """
    ディレクトリを作成し、必要に応じてデータをコピーします。

    Args:
        model_name (str): コピー先のサブディレクトリ名。
                          `./data/raw/model_name` 内に作成されます。
        copy_source_raw_directory (Optional[str]): コピー元ディレクトリのパス（相対パスまたは絶対パス）。
        force (bool): 同名ファイルが存在する場合に上書きするか。
    """
    base_path = Path("./data/raw/model_name")
    destination_path = base_path / model_name

    # 必要なディレクトリを作成
    destination_path.mkdir(parents=True, exist_ok=True)
    print(f"ディレクトリを作成しました: {destination_path}")

    if copy_source_raw_directory:
        source_path = Path(copy_source_raw_directory)

        if not source_path.exists():
            raise FileNotFoundError(
                f"コピー元ディレクトリが存在しません: {source_path}"
            )

        for item in source_path.iterdir():
            destination = destination_path / item.name
            if destination.exists() and not force:
                print(f"スキップ: ファイルが既に存在します: {destination}")
                continue

            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=force)
            else:
                shutil.copy2(item, destination)
        print(f"{source_path} の内容を {destination_path} にコピーしました")


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

            file_counter += 1
            duration += term - overlay


def normalize_audio_files(model_name: str, force: bool = False) -> None:
    """
    fap loudness-norm を使用して音声データを正規化します。

    Args:
        model_name (str): モデル名。
                          `./data/raw/model_name/{model_name}/separate` 配下の音声データを対象とします。
        force (bool): 既存の正規化済みファイルを上書きするか。
    """
    base_path = Path(f"./data/raw/model_name/{model_name}")
    separate_dir = base_path / "separate"
    normalized_dir = base_path / "normalized"
    normalized_dir.mkdir(parents=True, exist_ok=True)

    # 音声ファイルの処理
    for audio_file in separate_dir.glob("*.wav"):
        normalized_file = normalized_dir / audio_file.name

        if normalized_file.exists() and not force:
            print(f"スキップ: ファイルが既に存在します: {normalized_file}")
            continue

        # fap loudness-norm を使用して正規化
        cmd = ["fap", "loudness-norm", str(audio_file), "-o", str(normalized_file)]
        try:
            subprocess.run(cmd, check=True)
            print(f"正規化完了: {normalized_file}")
        except subprocess.CalledProcessError as e:
            print(f"エラー: 正規化に失敗しました: {audio_file}, {e}")


def transcribe_audio_files(model_name: str, force: bool = False) -> None:
    """
    音声ファイルを文字起こししてテキストデータを生成します。

    Args:
        model_name (str): モデル名。
                          `./data/raw/model_name/{model_name}/separate` 配下の音声データを対象とします。
        force (bool): 既存のテキストデータを上書きするか。
    """
    base_path = Path(f"./data/raw/model_name/{model_name}")
    separate_dir = base_path / "separate"
    transcribed_dir = base_path / "transcribed"
    transcribed_dir.mkdir(parents=True, exist_ok=True)

    # 音声ファイルの処理
    for audio_file in separate_dir.glob("*.wav"):
        text_file = transcribed_dir / f"{audio_file.stem}.lab"

        if text_file.exists() and not force:
            print(f"スキップ: テキストデータが既に存在します: {text_file}")
            continue

        cmd = ["fap", "transcribe", str(audio_file), "-o", str(text_file)]
        try:
            subprocess.run(cmd, check=True)
            print(f"文字起こし完了: {text_file}")
        except subprocess.CalledProcessError as e:
            print(f"エラー: 文字起こしに失敗しました: {audio_file}, {e}")


def main():
    """
    引数を受け取り、データコピー、音声分割、クリーンアップ、文字起こしを順次処理します。
    """
    parser = argparse.ArgumentParser(
        description="カスタムモデルのデータ構造を生成し、音声データを分割・クリーンアップ・文字起こしします。"
    )
    parser.add_argument(
        "--copy-source-raw-directory",
        type=str,
        help="コピー元のディレクトリパス（相対パスまたは絶対パス）。指定されている場合のみデータをコピーします。",
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
        help="既存のファイルやテキストデータを上書きします。",
    )
    parser.add_argument(
        "--split-only",
        action="store_true",
        help="音声分割のみ実行します。",
    )
    parser.add_argument(
        "--transcribe-only",
        action="store_true",
        help="文字起こしのみ実行します。",
    )

    args = parser.parse_args()

    try:
        if args.copy_source_raw_directory:
            create_and_copy_data(
                model_name=args.model_name,
                copy_source_raw_directory=args.copy_source_raw_directory,
                force=args.force,
            )

        if not args.transcribe_only:
            split_audio_files(
                model_name=args.model_name,
                start=args.start,
                term=args.term,
                overlay=args.overlay,
                force=args.force,
            )

        if not args.split_only:
            transcribe_audio_files(
                model_name=args.model_name,
                force=args.force,
            )

        print("すべての処理が完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
