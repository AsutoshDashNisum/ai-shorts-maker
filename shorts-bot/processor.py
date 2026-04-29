import json
import math
import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
from logger import log
import config

# ── environment setup ──────────────────────────────────────
# Add FFmpeg to PATH for this process
FFMPEG_DIR = r"C:\Users\adash\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1-full_build\bin"
if FFMPEG_DIR not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_DIR

# ── paths ──────────────────────────────────────────────────
FFMPEG_PATH = "ffmpeg"
FFPROBE_PATH = "ffprobe"

# ── helpers ──────────────────────────────────────────────────

# ── helpers ──────────────────────────────────────────────────

def _probe_duration(video_path: str) -> float:
    """Return video duration in seconds using ffprobe."""
    cmd = [
        FFPROBE_PATH,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        video_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError) as exc:
        log.error("ffprobe failed for '%s': %s", video_path, exc)
        raise RuntimeError(f"Cannot determine video duration: {exc}") from exc


def _run_ffmpeg(args: List[str], desc: str = "") -> None:
    """Run an FFmpeg command, raising on failure."""
    cmd = [FFMPEG_PATH, "-y"] + args
    log.debug("FFmpeg: %s", " ".join(cmd))
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        log.error("FFmpeg failed (%s):\n%s", desc, result.stderr[-2000:])
        raise RuntimeError(f"FFmpeg error during '{desc}'")


# ── public API ───────────────────────────────────────────────

def process_video(
    video_path: str,
    num_clips: int | None = None,
    max_duration: int | None = None,
    custom_segments: List[Dict] | None = None,
    output_dir: str | None = None,
    original_title: str = "Video",
) -> List[str]:
    """
    Split *video_path* into vertical short clips.
    Supports either equal splits or custom AI-found segments.
    """
    num_clips = num_clips or config.NUM_CLIPS
    max_duration = max_duration or config.MAX_CLIP_DURATION
    
    # Sanitize title for directory name
    import re
    safe_title = re.sub(r'(?u)[^-\w.]', '_', original_title)
    out_dir = Path(output_dir or config.OUTPUT_DIR) / "clips" / safe_title
    out_dir.mkdir(parents=True, exist_ok=True)

    total_duration = _probe_duration(video_path)
    log.info(
        "Source: '%s'  duration=%.1f s",
        original_title, total_duration,
    )

    # ── calculate segment boundaries ─────────────────────────
    segments_to_process = []
    
    if custom_segments:
        log.info("🎯 Processing %d AI-suggested viral hooks...", len(custom_segments))
        for hook in custom_segments:
            segments_to_process.append({
                "start": float(hook["start_time"]),
                "duration": float(hook["duration"]),
                "title": hook.get("hook_title", "Clip")
            })
    else:
        log.info("🔄 Processing %d equal splits...", num_clips)
        raw_segment = total_duration / num_clips
        segment_len = min(raw_segment, float(max_duration))
        for i in range(num_clips):
            start = i * raw_segment
            dur = min(segment_len, total_duration - start)
            if dur < 1.0: continue
            segments_to_process.append({
                "start": start,
                "duration": dur,
                "title": f"Part {i+1}"
            })

    if not segments_to_process:
        raise RuntimeError("No valid segments could be created.")

    total_clips = len(segments_to_process)
    output_files: List[str] = []

    for idx, seg in enumerate(
        tqdm(segments_to_process, desc="Processing clips", colour="cyan"), start=1
    ):
        start = seg["start"]
        duration = seg["duration"]
        clip_title = seg["title"]
        
        clip_name = f"clip_{idx:02d}.mp4"
        final_path = str(out_dir / clip_name)

        # Build overlay text
        # If it's a custom hook, use the hook title!
        part_text = clip_title if custom_segments else f"Part {idx} of {total_clips}"
        
        font_path = "C\\:/Windows/Fonts/arial.ttf"
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=decrease,"
            f"pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawtext=fontfile='{font_path}':text='{part_text}':"
            f"fontsize=48:fontcolor=white:borderw=3:bordercolor=black:"
            f"x=(w-text_w)/2:y=h-th-80"
        )

        args = [
            "-ss", f"{start:.3f}",
            "-i", video_path,
            "-t", f"{duration:.3f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-r", "30",
            "-movflags", "+faststart",
            final_path,
        ]

        _run_ffmpeg(args, desc=f"rendering clip {idx}/{total_clips}")
        
        output_files.append(os.path.abspath(final_path))
        log.info("  ✓ Clip %d/%d → %s (%s)", idx, total_clips, clip_name, part_text)

    log.info("All %d clip(s) saved to %s", len(output_files), out_dir)
    return output_files
