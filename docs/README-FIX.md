# CaptionClean Online v2.2 — FFmpeg Core Fix

This package keeps the original v2.2 interface and caption-removal workflow.

## Fixed

The old page loaded the ESM version of `ffmpeg-core.js` through a temporary blob URL. Chrome's FFmpeg class worker could not import it and displayed:

`Processing failed: Error: failed to import ffmpeg-core.js`

This build serves the compatible UMD `ffmpeg-core.js` and the FFmpeg class worker from the same GitHub Pages site. The large WebAssembly file still downloads from the pinned public CDN when processing begins.

## Deploy to GitHub Pages

Replace the old site files with every file in this package. In particular, make sure these three updated files are uploaded together:

- `index.html`
- `ffmpeg-worker.js`
- `ffmpeg-core.js`

Also upload `sw.js` so the old cached build is removed. After GitHub Pages finishes deploying, open the site and press **Command + Shift + R** in Chrome.
