"""
main.py — CLI entrypoint for shorts-bot.

Pipeline:  download → split/reformat → upload YouTube → upload Instagram
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import ssl
from pathlib import Path
from typing import Dict, List

# Global SSL Bypass for Windows Environments
ssl._create_default_https_context = ssl._create_unverified_context

import whisper
from ai_assistant import ai
from logger import log
import config
from downloader import download_video
import processor
import youtube_uploader


# ── Summary table ────────────────────────────────────────────

def _print_summary(
    clips: List[str],
    yt_results: List[Dict[str, str]],
) -> None:
    """Print a formatted table of upload results."""
    sep = "─" * 60
    header = f"{'Clip':<30} {'YouTube':<30}"

    print(f"\n{sep}")
    print(f"    UPLOAD SUMMARY")
    print(sep)
    print(f"  {header}")
    print(f"  {'─'*30} {'─'*30}")

    for idx in range(len(clips)):
        clip_name = clips[idx].split("\\")[-1].split("/")[-1]
        yt_status = yt_results[idx]["status"] if idx < len(yt_results) else "—"

        yt_icon = "✅" if yt_status == "success" else "❌" if "failed" in yt_status else "⏭️"

        print(f"  {clip_name:<30} {yt_icon} {yt_status:<27}")

    print(sep)

    yt_ok = sum(1 for r in yt_results if r["status"] == "success")
    print(f"  YouTube:   {yt_ok}/{len(yt_results)} succeeded")
    print(sep + "\n")


# ── CLI ──────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="shorts-bot",
        description="Download a video, split into vertical shorts, and upload to YouTube.",
    )
    parser.add_argument(
        "--url", required=True, help="Video URL (YouTube, Vimeo, Twitter, …)"
    )
    parser.add_argument(
        "--clips", type=int, default=config.NUM_CLIPS,
        help=f"Number of clips to produce (default {config.NUM_CLIPS})",
    )
    parser.add_argument(
        "--title", type=str, default="",
        help="Custom title for the shorts",
    )
    parser.add_argument(
        "--dry-run", action="store_true", default=False,
        help="Download & process only — skip all uploads",
    )
    parser.add_argument(
        "--skip-youtube", action="store_true", default=False,
        help="Skip YouTube upload",
    )
    parser.add_argument(
        "--output-dir", type=str, default=config.OUTPUT_DIR,
        help=f"Output directory (default: {config.OUTPUT_DIR})",
    )
    parser.add_argument(
        "--no-ai", action="store_true", default=False,
        help="Skip AI metadata generation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start = time.time()

    log.info("=" * 60)
    log.info("=" * 60)
    log.info("  shorts-bot  -  automated AI-powered pipeline")
    log.info("=" * 60)
    log.info("URL        : %s", args.url)
    log.info("Clips      : %d", args.clips)
    log.info("AI Enabled : %s", not args.no_ai)
    log.info("")

    # ── Step 1: Download or Use Local File ───────────────────
    if os.path.exists(args.url):
        log.info("Local file detected: %s", args.url)
        video_path = os.path.abspath(args.url)
        # Dummy metadata for local files
        metadata = {
            "title": args.title if args.title else Path(video_path).stem,
            "duration": 0,
            "description": "",
            "tags": []
        }
        log.info("✓ Using local file → skipping download.")
    else:
        log.info("STEP 1/4  Downloading video...")
        try:
            video_path, metadata = download_video(args.url, output_dir=args.output_dir)
            if args.title:
                metadata["title"] = args.title
        except Exception as exc:
            log.error("Download failed — aborting. %s", exc)
            sys.exit(1)

    # ── Step AI: Power up with Llama-3 ───────────────────────
    final_title = args.title if args.title else Path(video_path).stem
    description = "Viral animation! 😂🔥 #Shorts"
    tags = ["Shorts", "Viral"]
    hooks = []

    if not args.no_ai:
        log.info("🚀 Pumping AI magic into metadata...")
        try:
            # Check for transcript cache
            cache_path = f"{video_path}.transcript"
            if os.path.exists(cache_path):
                log.info("  💾 Found transcript cache — skipping AI Listening.")
                with open(cache_path, "r", encoding="utf-8") as f:
                    full_transcript = f.read()
            else:
                # 1. Transcribe the whole video once for the LLM (Using Base for speed)
                log.info("  📂 Transcribing full original video for AI analysis (Model: Base)...")
                whisper_model = whisper.load_model("base")
                transcript_result = whisper_model.transcribe(video_path, task="transcribe", language="hi")
                full_transcript = transcript_result["text"]
                
                # Save to cache
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(full_transcript)
            
            # 2. Generate Viral Metadata
            ai_data = ai.generate_viral_metadata(full_transcript, final_title)
            final_title = ai_data.get("title", final_title)
            description = ai_data.get("description", description)
            tags = ai_data.get("tags", tags)

            # 3. Find Viral Hooks (The OpusClip Upgrade!)
            hooks = ai.find_viral_hooks(full_transcript)
            
        except Exception as e:
            log.error(f"❌ AI Metadata phase failed: {e}")

    # ── STEP 2/4  Splitting & reformatting ────────────────────
    log.info("▶ STEP 2/4  Splitting into vertical clips...")
    all_clips_to_upload = []

    # A. Regular Equal Splits
    log.info("--- Strategy A: Regular Equal Splits ---")
    regular_clips = processor.process_video(
        video_path=video_path,
        num_clips=args.clips,
        output_dir=args.output_dir,
        original_title=f"{final_title}_Regular"
    )
    all_clips_to_upload.extend(regular_clips)

    # B. AI Hook Splits (If hooks were found)
    if hooks:
        log.info("--- Strategy B: AI Viral Hooks ---")
        hook_clips = processor.process_video(
            video_path=video_path,
            custom_segments=hooks,
            output_dir=args.output_dir,
            original_title=f"{final_title}_AI_Hooks"
        )
        all_clips_to_upload.extend(hook_clips)

    # ── STEP 3/4  YouTube upload ──────────────────────────────
    log.info("▶ STEP 3/4  YouTube upload")
    yt_results = []
    
    if args.dry_run or args.skip_youtube:
        reason = "dry-run" if args.dry_run else "skipped"
        log.info("  YouTube upload — %s", reason)
        yt_results = [
            {"id": "", "title": f"Clip {i+1}", "status": f"skipped: {reason}"}
            for i in range(len(all_clips_to_upload))
        ]
    else:
        if not all_clips_to_upload:
            log.warning("  No clips found to upload.")
        else:
            log.info("🚀 Uploading ALL clips to YouTube Shorts...")
            try:
                yt_results = youtube_uploader.upload_clips(
                    all_clips_to_upload,
                    original_title=final_title,
                    description=description,
                    tags=tags
                )
            except Exception as exc:
                log.error("YouTube upload error: %s", exc)
                yt_results = [
                    {"id": "", "title": f"Clip {i+1}", "status": f"failed: {exc}"}
                    for i in range(len(all_clips_to_upload))
                ]

    log.info("")

    # ── Summary ──────────────────────────────────────────────
    _print_summary(all_clips_to_upload, yt_results)

    elapsed = time.time() - start
    log.info("✅ Pipeline completed in %.1f s", elapsed)


if __name__ == "__main__":
    main()
