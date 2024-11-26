# 使い方

## インストール

```bash
git clone https://github.com/GenLipSyncVideo
cd ./GenLipSyncVideo
bash install
```

## セットアップ

```bash
cd "$HOME/workspace/fish-speech"
bash setup
```

## 通常の使い方

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name \
    --copy-source-raw-directory ./data/tmp
```

### 何が実行されるのか

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

### ファイルコピーのみ実行

```bash
# good
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

### ファイルコピーとファイル分割まで

```bash
# good
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name

# good: 分割するファイルの位置を指定した場合。e.g. 00:05:00~00:05:20, 00:05:17~00:05:37, 00:05:34~00:05:54, ...
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 300 --term 20 --overlay 3

# good: 分割するファイルの位置を指定した場合。e.g. 00:07:00~00:07:40, 00:07:37~00:08:17, 00:08:14~00:08:54, ...
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 420 --term 40 --overlay 10
```

### ファイル分割のみ

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-separate-only
```

### ファイル正規化のみ

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-normalize-only
```

### ファイル正規化のみ（上書き）

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-normalize-only --force-normalize-loudness
```

### 音声データからテキストデータを生成するのみ

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only
```

### 音声データからテキストデータを生成するのみ（上書き）

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only --force-transcribe
```

### 音声データからテキストデータを生成するのみ（モデルを指定）

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-transcribe-only --whisper-model-name whisper_model_name
```

### セマンティックトークンを生成する前処理のみ

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-before-text-reformatting-only
```

### セマンティックトークンを生成する前処理のみ（上書き）

```bash
# good
python preparation_before_fine_tuning.py --model-name model_name --file-before-text-reformatting-only --force-before-text-reformatting
```

### セマンティックトークンを生成するのみ

```bash
# good
python fine_tuning.py --model-name model_name
```

### セマンティックトークンを生成する（パスを指定）

```bash
# good
python fine_tuning.py --model-name model_name --override-path ./data/model_name/before_text_reformatting/00001_00-00-00~00-00-30_test
```
