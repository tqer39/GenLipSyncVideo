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
    --model-name model_name --file-copy-only --force
```

### ファイルコピーと分割実行

```bash
python generate_custom_model.py --copy-source-raw-directory ./data/tmp \
    --model-name model_name --start 0 --term 30 --overlay 5 --force
```
