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

## サンプルデータを通常の使い方

```bash
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
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-copy-only
```

### ファイルコピーと分割実行

```bash
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 0 --term 30 --overlay 5
```

### 音声データからテキストデータを生成（強制）

```bash
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-transcribe-only --force-transcribe
```

### 音声データからテキストデータを生成（強制）（Whisper のモデルを指定）

```bash
python preparation_before_fine_tuning.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-transcribe-only --force-transcribe --whisper-model-name small
```
