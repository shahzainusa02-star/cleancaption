import shutil
import subprocess
import tempfile
from pathlib import Path

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse

BASE = Path(__file__).resolve().parent
INDEX = BASE / "index.html"
WORK = Path(tempfile.gettempdir()) / "cleancaption_stage2_exact"
WORK.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="CleanCaption v1.0 Beta")


def detect_caption_box(frame):
    h, w = frame.shape[:2]
    yA, yB = int(h * 0.72), int(h * 0.84)
    roi = frame[yA:yB]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    _, S, V = cv2.split(hsv)
    white = ((V > 175) & (S < 110)).astype(np.uint8) * 255
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    n, labels, stats, centers = cv2.connectedComponentsWithStats(white, 8)
    candidates = []

    for i in range(1, n):
        x, y, ww, hh, area = map(int, stats[i])
        if not (7 <= area <= 650 and 2 <= ww <= 55 and 5 <= hh <= 31):
            continue

        pad = 4
        x0 = max(0, x - pad)
        y0 = max(0, y - pad)
        x1 = min(w, x + ww + pad)
        y1 = min(roi.shape[0], y + hh + pad)

        patch = gray[y0:y1, x0:x1]
        dark_fraction = float(np.mean(patch < 95))
        if dark_fraction < 0.09:
            continue

        gy = y + yA
        candidates.append((x, gy, ww, hh, area, dark_fraction, gy + hh))

    core = [
        c for c in candidates
        if c[0] + c[2] > 35 and c[0] < w - 35 and 668 <= c[6] <= 686
    ]
    strong = [c for c in core if c[3] >= 14 and c[1] <= 663]

    if len(strong) < 2:
        return None

    scored = []
    for baseline in range(672, 683):
        group = [c for c in strong if abs(c[6] - baseline) <= 1]
        if not group:
            continue

        gx0 = min(c[0] for c in group)
        gx1 = max(c[0] + c[2] for c in group)
        center = (gx0 + gx1) / 2

        score = (
            len(group) * 6
            + (gx1 - gx0) / 20
            - abs(center - w / 2) / 25
            - abs(baseline - 676) * 0.8
        )
        scored.append((score, baseline, group))

    if not scored:
        return None

    score, baseline, anchor = max(scored, key=lambda z: z[0])
    if len(anchor) < 2 or score < 10:
        return None

    ax0 = min(c[0] for c in anchor)
    ax1 = max(c[0] + c[2] for c in anchor)

    same_baseline = [
        c for c in core
        if abs(c[6] - baseline) <= 2 and c[1] <= 666
    ]

    extras = [
        c for c in core
        if 647 <= c[1] <= 665
        and baseline - 2 <= c[6] <= baseline + 9
        and c[0] <= ax1 + 28
        and c[0] + c[2] >= ax0 - 28
    ]

    merged = {tuple(c): c for c in (anchor + same_baseline + extras)}
    group = list(merged.values())

    x0 = min(c[0] for c in group)
    x1 = max(c[0] + c[2] for c in group)
    y0 = min(c[1] for c in group)
    y1 = max(c[1] + c[3] for c in group)

    return (
        max(0, x0 - 14),
        max(0, y0 - 10),
        min(w - 1, x1 + 14),
        min(h - 1, y1 + 12),
    )


def build_stage2_mask(frame, box):
    h, w = frame.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    if box is None:
        return mask

    x0, y0, x1, y1 = box

    # This is intentionally the SAME Stage 2 method:
    # cover the complete detected caption rectangle, including outline/shadow.
    mask[y0:y1 + 1, x0:x1 + 1] = 255

    # Slight expansion prevents edge letters from surviving.
    mask = cv2.dilate(
        mask,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
        iterations=1,
    )
    return mask


def get_ffmpeg():
    path = shutil.which("ffmpeg")
    if not path:
        raise RuntimeError("FFmpeg is not installed or not visible in PATH.")
    return path


def process_video(source: Path, output: Path):
    cap = cv2.VideoCapture(str(source))
    if not cap.isOpened():
        raise RuntimeError("Could not open the uploaded video.")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 29.97)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    if width <= 0 or height <= 0:
        cap.release()
        raise RuntimeError("Could not read video size.")

    temp = output.with_name("stage2-no-audio.mp4")
    writer = cv2.VideoWriter(
        str(temp),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )

    if not writer.isOpened():
        cap.release()
        raise RuntimeError("Could not create temporary output video.")

    frames = 0
    cleaned = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        box = detect_caption_box(frame)

        if box is not None:
            mask = build_stage2_mask(frame, box)
            frame = cv2.inpaint(frame, mask, 3, cv2.INPAINT_TELEA)
            cleaned += 1

        writer.write(frame)
        frames += 1

    cap.release()
    writer.release()

    if frames == 0:
        temp.unlink(missing_ok=True)
        raise RuntimeError("No video frames were processed.")

    # Same compatible export settings as the Stage 2 reference video.
    command = [
        get_ffmpeg(), "-y",
        "-i", str(temp),
        "-i", str(source),
        "-map", "0:v:0",
        "-map", "1:a:0?",
        "-c:v", "libx264",
        "-profile:v", "baseline",
        "-level", "3.1",
        "-preset", "medium",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-r", "30000/1001",
        "-c:a", "aac",
        "-profile:a", "aac_low",
        "-b:a", "128k",
        "-ar", "44100",
        "-ac", "2",
        "-movflags", "+faststart",
        str(output),
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    temp.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError("Final MP4 export failed:\n" + result.stderr[-2500:])

    if not output.exists() or output.stat().st_size < 1024:
        raise RuntimeError("Final video was not created.")

    return frames, cleaned


@app.get("/", response_class=HTMLResponse)
def home():
    return INDEX.read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {
        "ok": True,
        "ffmpeg": bool(shutil.which("ffmpeg")),
        "engine": "Stage 2 exact local",
    }


@app.post("/api/remove")
async def remove(video: UploadFile = File(...)):
    suffix = Path(video.filename or "video.mp4").suffix.lower()

    if suffix not in {".mp4", ".mov", ".m4v", ".avi", ".webm", ".mkv"}:
        raise HTTPException(status_code=400, detail="Unsupported video format.")

    job = WORK / next(tempfile._get_candidate_names())
    job.mkdir(parents=True, exist_ok=True)

    source = job / ("original" + suffix)
    output = job / "cleaned-video.mp4"

    with source.open("wb") as f:
        shutil.copyfileobj(video.file, f)

    try:
        process_video(source, output)
        return FileResponse(
            str(output),
            media_type="video/mp4",
            filename="cleaned-video.mp4",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8040)
