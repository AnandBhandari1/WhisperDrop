# WhisperDrop

Speak. Drop. Done.

WhisperDrop is a tiny, fast speech-to-text tool for **Linux and Windows**. It sits as a dark floating widget on your screen -- press F8 anywhere, speak, and your words drop right at the cursor. No copy-paste, no switching windows, no hassle. **macOS is not supported.**

<a href="https://www.buymeacoffee.com/anandbhandari" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-red.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>

## How It Works

1. Press **F8** (or click **REC**)
2. Speak naturally
3. Press **F8** again (or click **STOP**)
4. Your words drop at the cursor -- in any app, instantly

## Features

- **Instant text drop** -- words appear at your cursor via `xdotool` (Linux) or clipboard paste (Windows)
- **GPU accelerated** -- CUDA with automatic CPU fallback
- **Global hotkey** -- F8 works from any application, no sudo needed
- **Compact dark UI** -- frameless floating widget, draggable, always on top
- **Live waveform** -- visual audio feedback while you speak
- **Whisper powered** -- uses OpenAI Whisper (`small`, 464MB) via faster-whisper for fast and accurate transcription

## Requirements

- Python 3.12+
- **Linux (X11)** or **Windows** — macOS is not supported
- **Linux:** `xdotool` installed
- **Windows:** No extra system deps
- CUDA GPU (optional, falls back to CPU)

## Install

```bash
git clone https://github.com/AnandBhandari1/WhisperDrop.git
cd WhisperDrop

# Install uv if you don't have it
# Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: https://astral.sh/uv

# Linux only: install xdotool
# sudo apt install xdotool

# Install python dependencies
uv sync
```

## Run

**Linux:**
```bash
./run.sh
```

**Windows (CPU only):**
```batch
run_cpu.bat
```

**Windows (CUDA GPU):**
```batch
run_cuda.bat
```

## Project Structure

```
WhisperDrop/
├── app.py             # Linux application (xdotool)
├── app_windows.py     # Windows application (pyautogui)
├── run.sh             # Linux run script
├── run_cpu.bat        # Windows CPU run script
├── run_cuda.bat       # Windows CUDA run script
├── pyproject.toml     # Dependencies
├── uv.lock            # Lock file
├── LICENSE            # MIT License
└── README.md          # This file
```

## Troubleshooting

**Mic not working** -- Check microphone permissions and default input device in system settings.

**No GPU** -- App automatically falls back to CPU. Install NVIDIA drivers + CUDA toolkit for GPU acceleration.

**F8 not responding** -- Make sure no other app is capturing F8. The hotkey uses `pynput` and works without sudo.

**Text not inserting (Linux)** -- Ensure `xdotool` is installed (`sudo apt install xdotool`). Only works on X11, not Wayland.

**Text not inserting (Windows)** -- Ensure the target window is focused before transcription finishes. The app uses Ctrl+V to paste.

**Running on macOS** -- WhisperDrop does not support macOS. Use Linux or Windows.

## License

MIT
