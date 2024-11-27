# 使い方

## インストール

```shell
git clone https://github.com/GenLipSyncVideo
cd ./GenLipSyncVideo
shell install
```

## セットアップ

```shell
cd "$HOME/workspace/fish-speech"
shell setup
```

## 1. 前処理

セマンティックトークンを生成ために必要なデータの前処理まで行います。

```shell
python preparation_before_fine_tuning.py --model-name model_name \
    --copy-source-raw-directory ./data/tmp
```

何が実行されるのか？

1. `--model-name` で指定されたモデル名が `data` フォルダ配下に作成され、ディレクトリ（`./data/${--model-name}`）を作成します。
2. `--copy-source-raw-directory` オプションで指定されたディレクトリ（`./data/tmp`）にある音声データファイル（`*.wav`, `*.mp3`）を `./data/${--model-name}/raw` にコピーします。
3. `scripts/separate.py` でファイルを分割して `./data/${--model-name}/raw/separate/${分割元ファイル名_NNNNN.(wav|mp3)}` に保存します。
   1. `--start` オプションで指定された秒数から開始します。デフォルトは `0` です。
   2. `--term` オプションで指定された秒数で終了します。デフォルトは `30` です。
   3. `--overlay` オプションで指定された秒数でオーバーラップします。デフォルトは `5` です。
4. `scripts/normalize_loudness.py` を使用して、分割された音声データ（`./data/${--model-name}/raw/separate/${分割元ファイル名_NNNNN.(wav|mp3)}`）を正規化します。
   1. 保存先: `./data/${--model-name}/normalize_loudness/${分割元ファイル名_NNNNN.(wav|mp3)}`
5. `scripts/speech_to_text.py` を使用して音声データ（`./data/${--model-name}/raw/separate/${分割元ファイル名_NNNNN.(wav|mp3)}`）からテキストデータを生成します。
   1. 保存先: `./data/${--model-name}/transcriptions/${分割後ファイル名_NNNNN}.lab`
   2. 文字起こしのときのモデルは `--whisper-model-name` で指定できます。デフォルトは `base` です。

以下は前処理を個別に実施していくオプションの例です。

### 1.1. ファイルコピーのみ実行

```shell
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-copy-only

# bad: モデル指定がない場合はエラー
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --file-copy-only

# bad: コピー元のディレクトリを指定するオプションがない場合はエラー
python preparation_before_fine_tuning.py \
    --model-name model_name --file-copy-only

# bad: コピー元のディレクトリが存在しない場合はエラー
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/null \
     --model-name model_name --file-copy-only

# ファイルコピーのみ: コピー元のディレクトリが存在するが、ファイルが存在しない場合はエラー
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/empty \
    --model-name model_name --file-copy-only
```

### 1.2. ファイルコピーとファイル分割まで

```shell
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name

: 分割するファイルの位置を指定した場合。e.g. 00:05:00~00:05:20, 00:05:17~00:05:37, 00:05:34~00:05:54, ...
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 300 --term 20 --overlay 3

: 分割するファイルの位置を指定した場合。e.g. 00:07:00~00:07:40, 00:07:37~00:08:17, 00:08:14~00:08:54, ...
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 420 --term 40 --overlay 10
```

### 1.3. ファイル分割のみ

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-separate-only
```

### 1.4.1. ファイル正規化のみ

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-normalize-only
```

### 1.4.2. ファイル正規化のみ（上書き）

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-normalize-only --force-normalize-loudness
```

### 1.5.1. 音声データからテキストデータを生成するのみ

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only
```

### 1.5.2. 音声データからテキストデータを生成するのみ（上書き）

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only --force-transcribe
```

### 1.5.3. 音声データからテキストデータを生成するのみ（モデルを指定）

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only --whisper-model-name whisper_model_name
```

### 1.6.1. セマンティックトークンを生成する前処理のみ

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-before-text-reformatting-only
```

### 1.6.2. セマンティックトークンを生成する前処理のみ（上書き）

```shell
python preparation_before_fine_tuning.py --model-name model_name --file-before-text-reformatting-only --force-before-text-reformatting
```

## 2. ファインチューニング

基本このコマンドでファインチューニングは完了します。前処理で準備したデータを元に、指定されたモデルをファインチューニングします。

```shell
python fine_tuning.py --model-name model_name

# パスを上書きする場合
python fine_tuning.py --model-name model_name --overwrite-path ./data/tmp2
```

以下は前処理を個別に実施していくオプションの例です。

### 2.1.1. セマンティックトークンを生成するのみ

```shell
python fine_tuning.py --model-name model_name --create-semantic-token-only
```

### 2.1.2. セマンティックトークンを生成するのみ（上書き）

```shell
python fine_tuning.py --model-name model_name --create-semantic-token-only --force-create-semantic-token
```

### 2.2.1. protobuf ファイルを生成するのみ

```shell
python fine_tuning.py --model-name model_name --create-protobuf-only
```

### 2.2.2. protobuf ファイルを生成するのみ（上書き）

```shell
python fine_tuning.py --model-name model_name --create-protobuf-only --force-create-protobuf
```

### 2.3. モデルをトレーニングするのみ

```shell
python fine_tuning.py --model-name model_name --training-only
```
