#!/bin/bash
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "======================================"
echo "        CleanCaption v1.0 Beta"
echo "======================================"
echo "Local processing. No cloud. No API."
echo ""

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: Python 3 is required."
  echo "Install Python 3, then open CleanCaption again."
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: FFmpeg is required."
  echo "If you use Homebrew, run: brew install ffmpeg"
  read -n 1 -s -r -p "Press any key to close..."
  exit 1
fi

if [ ! -d ".venv" ]; then
  echo "First launch: creating CleanCaption environment..."
  python3 -m venv .venv
fi

source .venv/bin/activate
echo "Checking required packages..."
python3 -m pip install --quiet --disable-pip-version-check -r requirements.txt

echo ""
echo "Starting CleanCaption..."
echo "Browser address: http://127.0.0.1:8040"
echo "Keep this Terminal window open."
echo ""

(
  sleep 2
  open "http://127.0.0.1:8040"
) &

python3 main.py
