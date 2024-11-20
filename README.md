# GenLipSyncVideo

## Using

### Setup

```bash
bash ./setup
```

### Separate

1. wav ファイルを分割する。`bash ./setup` 実行後、fish-speech のディレクトリで実行すること。
2. `separate.py` は、指定されたWAVファイルを指定の間隔で分割するスクリプトです。以下のコマンドを使用してスクリプトを実行できます。

```bash
deactivate
source .venv/bin/activate
```

#### 引数の説明

- `--input`: 入力する単一のWAVファイルのパス（例: `"$HOME/workspace/GenLipSyncVideo/data/raw/d_208302/d_208302_track_001.wav"`）
- `--directory`: 入力する複数のWAVファイルが存在するディレクトリのパス
- `--output`: 出力するディレクトリのパス（例: `"$HOME/workspace/GenLipSyncVideo/data/raw/separate"`）
- `--dmm`-id: DMM ID（例: `d_208302`）。指定された場合、出力ディレクトリのパスに追加されます。
- `--start`: 分割開始時間（秒）（例: `0`）
- `--interval`: 分割間隔（秒）（例: `5`）
- `--duration`: 各分割ファイルの長さ（秒）（例: `15`）

#### 個別で DMM の wav ファイルを分割

```bash
cd "$HOME/workspace/fish-speech"
python "$HOME/workspace/GenLipSyncVideo/scripts/separate.py" \
  --input "$HOME/workspace/GenLipSyncVideo/data/raw/d_208302/d_208302_track_001.wav" \
  --output "$HOME/workspace/GenLipSyncVideo/data/raw/separate" \
  --dmm-id d_208302 \
  --start 0 \
  --interval 5 \
  --duration 15
```

#### 一括で DMM の wav ファイルを分割

```bash
cd "$HOME/workspace/fish-speech"
python "$HOME/workspace/GenLipSyncVideo/scripts/separate.py" \
  --directory "$HOME/workspace/GenLipSyncVideo/data/raw/d_208302" \
  --output "$HOME/workspace/GenLipSyncVideo/data/raw/separate" \
  --dmm-id d_208302 \
  --start 0 \
  --interval 5 \
  --duration 15
```

#### 注意事項

- `--input` または `--directory` のいずれかを指定する必要があります。両方指定されていない場合、エラーが発生します。
- 出力ディレクトリが存在しない場合は、自動的に作成されます。

### Speech-to-Text with OpenAI Whisper

1. `speech_to_text.py` は、指定されたWAVファイルをテキストに変換するスクリプトです。以下のコマンドを使用してスクリプトを実行できます。

```bash
deactivate
source .venv/bin/activate
```

#### 引数の説明

- `--input`: 入力する単一のWAVファイルのパス（例: `"$HOME/workspace/GenLipSyncVideo/data/raw/d_208302/d_208302_track_001.wav"`）
- `--output`: 出力するテキストファイルのパス（例: `"$HOME/workspace/GenLipSyncVideo/data/raw/text/d_208302_track_001.txt"`）
- `--dmm-id`: DMM ID（例: `d_208302`）。指定された場合、出力ファイルの名前に追加されます。
- `--model`: [使用するモデル](https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages)（例: `tiny`, `base`, `small`, `medium`, `large`, `turbo`）
-
