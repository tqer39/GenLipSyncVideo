import argparse
import os
import shutil
from pathlib import Path
from typing import Optional


def create_and_copy_data(
    model_name: str,
    input_model_name: str,
    copy_source_raw_directory: Optional[str] = None
) -> None:
    """
    ディレクトリを作成し、必要に応じてデータをコピーします。

    Args:
        model_name (str): モデル名。`./data/raw/model_name` 内でディレクトリを構成します。
        input_model_name (str): コピー先のサブディレクトリ名。
                                `--copy-source-raw-directory` が指定されている場合にのみ、データのコピー先となります。
        copy_source_raw_directory (Optional[str]): コピー元のサブディレクトリ名。
    """
    # ベースディレクトリの設定
    base_path = Path(f"./data/raw/{model_name}")
    destination_path = base_path / input_model_name

    # 必要なディレクトリを作成
    destination_path.mkdir(parents=True, exist_ok=True)
    print(f"ディレクトリを作成しました: {destination_path}")

    # コピー元が指定されている場合
    if copy_source_raw_directory:
        source_path = base_path / copy_source_raw_directory

        # コピー元ディレクトリが存在するか確認
        if not source_path.exists():
            raise FileNotFoundError(f"コピー元ディレクトリが存在しません: {source_path}")

        # コピー処理
        for item in source_path.iterdir():
            destination = destination_path / item.name
            if item.is_dir():
                shutil.copytree(item, destination, dirs_exist_ok=True)
            else:
                shutil.copy2(item, destination)
        print(f"{source_path} の内容を {destination_path} にコピーしました")


def main():
    """
    引数を受け取り、データディレクトリの作成とコピー処理を実行します。
    """
    parser = argparse.ArgumentParser(description="カスタムモデルのデータ構造を生成します。")
    parser.add_argument(
        "--copy-source-raw-directory",
        type=str,
        help=(
            "コピー元のフォルダ名（オプション）。"
            "`./data/raw/model_name` 内のフォルダ名を指定します。このオプションが指定されている場合のみデータをコピーします。"
        ),
    )
    parser.add_argument(
        "--model-name",
        type=str,
        required=True,
        help=(
            "コピー先のサブディレクトリ名。`./data/raw/model_name` 内に作成されます。"
            "`--copy-source-raw-directory` が指定されている場合、このディレクトリにデータがコピーされます。"
        ),
    )
    parser.add_argument(
        "model_name",
        type=str,
        help="モデル名。`./data/raw/model_name` の構造を設定します。",
    )

    args = parser.parse_args()

    try:
        # ディレクトリ作成とデータコピーを実行
        create_and_copy_data(
            model_name=args.model_name,
            input_model_name=args.model_name,
            copy_source_raw_directory=args.copy_source_raw_directory,
        )
        print("データ構造の生成が完了しました！")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()
