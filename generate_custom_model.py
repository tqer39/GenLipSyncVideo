import argparse
from pathlib import Path
from typing import Optional
import shutil
import subprocess


def create_and_copy_data(
    model_name: str,
    copy_source_raw_directory: Optional[str] = None,
    force: bool = False
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
            raise FileNotFoundError(f"コピー元ディレクトリが存在しません: {source_path}")

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
    model_name: str,
    start: int,
    term: int,
    overlay: int,
    force: bool = False
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

    # 音声ファイルの処理
    for audio_file in base_path.glob("*.wav"):
        print(f"処理中のファイル: {audio_file}")
        duration = start
        file_counter = 1

        while True:
            output_filename = f"{audio_file.stem}_{duration // 3600:02d}-{(duration % 3600) // 60:02d}-{duration % 60:02d}" \
                              f"-{(duration + term) // 3600:02d}-{((duration + term) % 3600) // 60:02d}-{(duration + term) % 60:02d}" \
                              f"_{file_counter:05d}{audio_file.suffix}"
            output_file = separate_dir / output_filename

            if not force and output_file.exists():
                print(f"スキップ: ファイルが既に存在します: {output_file}")
            else:
                # ffmpeg を使用して分割
                cmd = [
                    "ffmpeg", "-i", str(audio_file),
                    "-ss", str(duration), "-t", str(term),
                    str(output_file)
                ]
                subprocess.run(cmd, check=True)
                print(f"生成されたファイル: {output_file}")

            file_counter += 1
            duration += term - overlay

            # 仮の終了条件（ファイル全体長に応じて調整する必要あり）
            if duration >= 3600:  # 例: 最大1時間で終了
                break


def main():
    """
    引数を受け取り、データディレクトリの作成とコピー処理、音声分割を実行します。
    """
    parser = argparse.ArgumentParser(description="カスタムモデルのデータ構造を生成し、音声データを分割します。")
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
        help="既存のファイルや分割済みファイルを上書きします。",
    )

    args = parser.parse_args()

    try:
        # ディレクトリ作成とデータコピーを実行
        if args.copy_source_raw_directory:
            create_and_copy_data(
                model_name=args.model_name,
                copy_source_raw_directory=args.copy_source_raw_directory,
                force=args.force,
            )

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
