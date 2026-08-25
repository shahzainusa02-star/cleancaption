# CaptionClean Online v2.5 — Browser Fast-Marching Upgrade

This package keeps the original interface and upgrades the browser-only caption-removal engine.

## Improvements

- Keeps the lightweight WebCodecs engine, so the old FFmpeg WebAssembly freeze does not return.
- Detects the bright caption fill and its dark outline inside the caption area.
- Uses a tight feathered mask around the caption letters.
- Reconstructs inward from the clean edge in distance order.
- Prevents caption pixels from leaking back into the reconstructed area.
- Avoids broad local averaging, temporal copying, FFmpeg WebAssembly, and OpenCV WebAssembly.
- Preserves the source frame rate and primary audio.
- Streams the growing cleaned MP4 into the browser's device storage instead of keeping the entire export in RAM. This prevents the misleading `network error` caused by memory exhaustion on videos longer than one minute.

The supplied 478×850, 29.97 FPS original video was processed from beginning to end using the exact JavaScript in this package. The result preserved the original duration, frame rate, and stereo audio and decoded without errors.

The automatic detector remains tuned to centered bright captions with a dark outline in the lower-middle area. Use Manual Caption Area when captions appear elsewhere. Because GitHub Pages cannot run a large server-side generative video model, text covering a moving person or detailed object can still leave a small localized soft patch. The 350 MB input limit remains, while supported Chrome browsers now keep long outputs in device storage instead of browser memory.

## Deploy to GitHub Pages

Replace the old files in the repository's `docs` folder with every file in this package:

- `index.html`
- `sw.js`
- `manifest.webmanifest`
- `icon-192.png`
- `icon-512.png`

The old `ffmpeg-core.js`, `ffmpeg-core.wasm`, and `ffmpeg-worker.js` files are not used and may be deleted from `docs`.

After GitHub Pages finishes deploying, open the site and press **Command + Shift + R** in Chrome. If Chrome still shows an older status message, test once in an Incognito window.
