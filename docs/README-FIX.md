# CaptionClean Online v2.5.1 — Processing Controls Upgrade

This package keeps the original interface and upgrades the browser-only caption-removal engine.

## Improvements

- Keeps the lightweight WebCodecs engine, so the old FFmpeg WebAssembly freeze does not return.
- Detects the bright caption fill and its dark outline inside the caption area.
- Uses a tight feathered mask around the caption letters.
- Reconstructs inward from the clean edge in distance order.
- Prevents caption pixels from leaking back into the reconstructed area.
- Avoids broad local averaging, temporal copying, FFmpeg WebAssembly, and OpenCV WebAssembly.
- Preserves the source frame rate and primary audio.
- Adds a real Cancel Processing button that releases conversion resources.
- Allows multiple numbered manual caption areas, with Undo Last and Clear All controls.
- Lets a simple click or tap play/pause the video in Manual mode, while dragging still creates a caption area.
- Uses an OffscreenCanvas when available and no longer waits for `requestAnimationFrame`, so processing can continue when another browser tab is active.
- Warns before closing, reloading, or navigating away during processing.
- Streams outputs longer than one minute into browser device storage instead of keeping the entire MP4 in memory.

The supplied 478×850, 29.97 FPS original video was processed from beginning to end using the exact JavaScript in this package. The result preserved the original duration, frame rate, and stereo audio and decoded without errors.

The automatic detector remains tuned to centered bright captions with a dark outline in the lower-middle area. Use Manual Caption Areas when captions appear elsewhere. Because GitHub Pages cannot run a large server-side generative video model, text covering a moving person or detailed object can still leave a small localized soft patch. The 350 MB input limit remains; outputs longer than one minute use browser device storage on supported Chrome browsers.

Background processing is best-effort. Switching browser tabs is supported, but no static website can keep running after the page is closed, reloaded, or navigated away from. Android and iOS may pause Chrome if the operating system suspends the app or the phone locks; return to CaptionClean to resume browser execution.

## Deploy to GitHub Pages

Replace the old files in the repository's `docs` folder with every file in this package:

- `index.html`
- `sw.js`
- `manifest.webmanifest`
- `icon-192.png`
- `icon-512.png`

The old `ffmpeg-core.js`, `ffmpeg-core.wasm`, and `ffmpeg-worker.js` files are not used and may be deleted from `docs`.

After GitHub Pages finishes deploying, open the site and press **Command + Shift + R** in Chrome. If Chrome still shows an older status message, clear the site's stored data and open it again in a normal Chrome window. Long-video storage may be unavailable in Private or Incognito mode.
