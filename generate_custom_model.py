import argparse
from pathlib import Path
import subprocess
import whisper


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


def transcribe_with_whisper(file_path: Path, output_dir: Path) -> Path:
    """
    OpenAI Whisper を使用して音声ファイルを文字起こしします。

    Args:
        file_path (Path): 音声データファイルのパス。
        output_dir (Path): テキストデータの保存先ディレクトリ。

    Returns:
        Path: 生成されたテキストデータファイルのパス（.lab）。
    """
    text_file = output_dir / f"{file_path.stem}.lab"
    print(f"Whisper で文字起こし中: {file_path}")
    model = whisper.load_model(
        "base"
    )  # 必要に応じて "tiny", "small", "medium", "large" を選択
    result = model.transcribe(str(file_path))
    text_content = result["text"]

    # テキストを保存
    with text_file.open("w", encoding="utf-8") as f:
        f.write(text_content)
    print(f"テキストデータ（.lab）を生成しました: {text_file}")
    return text_file


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
        print(f"音声ファイルの長さ: {audio_duration} 秒")

        while duration < audio_duration:
            output_filename = (
                f"{audio_file.stem}_{duration // 3600:02d}-{(duration % 3600) // 60:02d}-{duration % 60:02d}"
                f"-{(duration + term) // 3600:02d}-{((duration + term) % 3600) // 60:02d}-{(duration + term) % 60:02d}"
                f"_{file_counter:05d}.wav"
            )
            output_file = separate_dir / output_filename

            if not force and output_file.exists():
                print(f"スキップ: ファイルが既に存在します: {output_file}")
                file_counter += 1
                duration += term - overlay
                continue

            # ffmpeg を使用して分割
            cmd = [
                "ffmpeg",
                "-y",  # 上書きを許可
                "-i",
                str(audio_file),
                "-ss",
                str(duration),
                "-t",
                str(term),
                str(output_file),
            ]
            print(f"実行コマンド: {' '.join(cmd)}")

            try:
                subprocess.run(cmd, check=True, timeout=60)  # タイムアウトを60秒に設定
                print(f"生成されたファイル: {output_file}")
            except subprocess.TimeoutExpired:
                print(f"エラー: タイムアウトしました: {audio_file} の分割処理")
                break
            except subprocess.CalledProcessError as e:
                print(f"エラー: ffmpeg の実行に失敗しました: {e}")
                break

            # Whisper を使用して文字起こし
            try:
                transcribe_with_whisper(output_file, separate_dir)
            except Exception as e:
                print(f"エラー: Whisper での文字起こしに失敗しました: {e}")
                break

            file_counter += 1
            duration += term - overlay

    print(f"全ての音声ファイルの処理が完了しました: {model_name}")


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
        split_audio_files(
            model_name=args.model_name,
            start=args.start,
            term=args.term,
            overlay=args.overlay,
            force=args.force,
        )
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
