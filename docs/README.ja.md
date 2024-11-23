# GenLipSyncVideo

## 使い方

### インストール

```bash
git clone https://github.com/GenLipSyncVideo
cd ./GenLipSyncVideo
bash install
```

### セットアップ

```bash
cd "$HOME/workspace/fish-speech"
bash setup
```

### ファイルコピーのみ実行

```bash
python generate_custom_model.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-copy-only
```

### ファイルコピーと分割実行

```bash
python generate_custom_model.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 0 --term 30 --overlay 5
```

### 音声データからテキストデータを生成（強制）

```bash
python generate_custom_model.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-transcribe-only --force-transcribe
```

### 音声データからテキストデータを生成（強制）（Whisper のモデルを指定）

```bash
python generate_custom_model.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --file-transcribe-only --force-transcribe --whisper-model-name small
```
