# CaptionClean Online v2.2 — Lightweight Final Fix

This package keeps the original v2.2 interface and replaces only the video-processing engine.

## Fixed

The earlier build first failed while importing `ffmpeg-core.js`. After that import was repaired, its roughly 30 MB WebAssembly engine could still make Chrome show **Page Unresponsive** on older computers.

This build removes FFmpeg WebAssembly and OpenCV. It uses the browser's lightweight WebCodecs engine, keeps Chrome responsive by yielding after each processed frame, exports a high-quality H.264 MP4, preserves the original frame rate, and preserves audio whenever the source audio is compatible with MP4.

The 350 MB file limit remains because the finished video is held in browser memory before download. Short videos are recommended on older computers and phones.

## Deploy to GitHub Pages

Replace the old files in the repository's `docs` folder with every file in this package:

- `index.html`
- `sw.js`
- `manifest.webmanifest`
- `icon-192.png`
- `icon-512.png`

The old `ffmpeg-core.js`, `ffmpeg-core.wasm`, and `ffmpeg-worker.js` files are no longer used and may be deleted from `docs`.

After GitHub Pages finishes deploying, open the site and press **Command + Shift + R** in Chrome. If Chrome still shows an older status message, test once in an Incognito window.
