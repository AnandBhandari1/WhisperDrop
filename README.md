# WhisperDrop

Speak. Drop. Done.

WhisperDrop is a tiny, fast speech-to-text tool for Linux. It sits as a dark floating widget on your screen -- press F8 anywhere, speak, and your words drop right at the cursor with grammar correction. No copy-paste, no switching windows, no hassle.

## How It Works

1. Press **F8** (or click **REC**)
2. Speak naturally
3. Press **F8** again (or click **STOP**)
4. Your words drop at the cursor -- in any app, instantly

## Features

- **Instant text drop** -- words appear at your cursor via `xdotool`, no clipboard hijacking
- **Grammar correction** -- auto-fixes grammar using LanguageTool
- **GPU accelerated** -- CUDA with automatic CPU fallback
- **Global hotkey** -- F8 works from any application, no sudo needed
- **Compact dark UI** -- frameless floating widget, draggable, always on top
- **Live waveform** -- visual audio feedback while you speak
- **Whisper powered** -- uses OpenAI Whisper (`small`, 464MB) via faster-whisper for fast and accurate transcription

## Requirements

- Python 3.12+
- Linux (X11)
- `xdotool` installed
- CUDA GPU (optional, falls back to CPU)

## Install

```bash
git clone https://github.com/AnandBhandari1/WhisperDrop.git
cd WhisperDrop

# Install uv if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install system dependencies
sudo apt install xdotool

# Install python dependencies
uv sync
```

## Run

```bash
./run.sh
```

## Project Structure

```
WhisperDrop/
├── app.py             # Application
├── run.sh             # Run script
├── pyproject.toml     # Dependencies
├── uv.lock            # Lock file
├── LICENSE            # MIT License
└── README.md          # This file
```

## Troubleshooting

**Mic not working** -- Check microphone permissions and default input device in system settings.

**No GPU** -- App automatically falls back to CPU. Install NVIDIA drivers + CUDA toolkit for GPU acceleration.

**F8 not responding** -- Make sure no other app is capturing F8. The hotkey uses `pynput` and works without sudo.

**Text not inserting** -- Ensure `xdotool` is installed (`sudo apt install xdotool`). Only works on X11, not Wayland.

## License

MIT
