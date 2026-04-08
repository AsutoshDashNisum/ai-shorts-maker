"""
downloader.py — Download any video URL using yt-dlp.

Returns local file path + metadata dict (title, duration, description, tags).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Tuple

import yt_dlp  # type: ignore
from tqdm import tqdm

from logger import log
import config


# ── Types ────────────────────────────────────────────────────
VideoMeta = Dict[str, Any]


class _TqdmLogger:
    """Redirect yt-dlp download progress into a tqdm bar."""

    def __init__(self) -> None:
        self._bar: tqdm | None = None

    def hook(self, d: dict) -> None:
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes", 0)
            if self._bar is None:
                self._bar = tqdm(
                    total=total,
                    unit="B",
                    unit_scale=True,
                    desc="Downloading",
                    colour="green",
                )
            self._bar.n = downloaded
            self._bar.total = total
            self._bar.refresh()
        elif d["status"] == "finished":
            if self._bar:
                self._bar.close()
                self._bar = None
            log.info("Download finished, post-processing…")


def download_video(url: str, output_dir: str | None = None) -> Tuple[str, VideoMeta]:
    """
    Download a video from *url* and return ``(file_path, metadata)``.
    """
    out = Path(output_dir or config.OUTPUT_DIR)
    out.mkdir(parents=True, exist_ok=True)

    progress = _TqdmLogger()

    # Using Nightly Build with robust multi-client rotation and cookies
    ydl_opts: dict = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "merge_output_format": "mp4",
        "outtmpl": str(out / "%(title)s.%(ext)s"),
        "quiet": False,
        "no_warnings": True,
        "nocheckcertificate": True,
        "cookiesfrombrowser": ("chrome",),
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android", "ios"]
            }
        },
        "progress_hooks": [progress.hook],
    }

    log.info("Starting download: %s", url)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: dict = ydl.extract_info(url, download=True)
            if info is None:
                raise RuntimeError("yt-dlp returned no info for the URL.")

            file_path: str = ydl.prepare_filename(info)

            if not os.path.isfile(file_path):
                for ext in (".mp4", ".mkv", ".webm"):
                    candidate = Path(file_path).with_suffix(ext)
                    if candidate.exists():
                        file_path = str(candidate)
                        break

            metadata: VideoMeta = {
                "title":       info.get("title", "Untitled"),
                "duration":    info.get("duration", 0),
                "description": info.get("description", ""),
                "tags":        info.get("tags") or [],
                "uploader":    info.get("uploader", ""),
            }

            log.info("Downloaded → %s  (%d s)", file_path, metadata["duration"])
            return os.path.abspath(file_path), metadata

    except Exception as exc:
        log.error("yt-dlp download failed: %s", exc)
        raise
