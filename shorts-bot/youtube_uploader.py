"""
youtube_uploader.py — Upload clips to YouTube Shorts via YouTube Data API v3.

• Uses OAuth 2.0 with automatic token refresh
• Saves / loads OAuth token from token.json
• Retry logic with exponential backoff (3 retries)
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from google.auth.transport.requests import Request          # type: ignore
from google.oauth2.credentials import Credentials            # type: ignore
from google_auth_oauthlib.flow import InstalledAppFlow       # type: ignore
from googleapiclient.discovery import build                  # type: ignore
from googleapiclient.http import MediaFileUpload             # type: ignore
from googleapiclient.errors import HttpError                 # type: ignore
from tqdm import tqdm
import httplib2

from logger import log
import config

# YouTube API scopes
_SCOPES: List[str] = ["https://www.googleapis.com/auth/youtube.upload"]
_TOKEN_FILE: str = "token.json"


# ── Auth helpers ─────────────────────────────────────────────

def _get_authenticated_service() -> Any:
    """
    Build and return an authenticated YouTube Data API service object.
    Handles first-time OAuth flow + token refresh.
    """
    creds: Optional[Credentials] = None

    if Path(_TOKEN_FILE).exists():
        creds = Credentials.from_authorized_user_file(_TOKEN_FILE, _SCOPES)

    # Refresh or run flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            log.info("Refreshing expired YouTube OAuth token…")
            creds.refresh(Request())
        else:
            log.info("Starting YouTube OAuth flow (browser will open)…")
            config.validate_youtube_config()
            flow = InstalledAppFlow.from_client_secrets_file(
                config.YOUTUBE_CLIENT_SECRET_FILE, _SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save for next run
        with open(_TOKEN_FILE, "w", encoding="utf-8") as fp:
            fp.write(creds.to_json())
        log.info("YouTube token saved to %s", _TOKEN_FILE)

    http_obj = httplib2.Http(disable_ssl_certificate_validation=True)
    import google_auth_httplib2
    http_obj = httplib2.Http(disable_ssl_certificate_validation=True)
    authorized_http = google_auth_httplib2.AuthorizedHttp(creds, http=http_obj)
    return build("youtube", "v3", http=authorized_http)


# ── Upload with retry ───────────────────────────────────────

def _upload_single(
    youtube: Any,
    file_path: str,
    title: str,
    description: str,
    tags: List[str],
) -> Dict[str, str]:
    """
    Upload one video file. Returns ``{ 'id': ..., 'title': ..., 'status': ... }``.

    Retries up to ``config.MAX_RETRIES`` times on transient errors.
    """
    body: dict = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }

    # Use direct upload (resumable=False) for higher stability with small clips
    media = MediaFileUpload(
        file_path, mimetype="video/mp4", resumable=False
    )

    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    last_exc: Optional[Exception] = None
    for attempt in range(1, 6): # Increase to 5 attempts
        try:
            log.info("  YouTube upload attempt %d/5: %s", attempt, title)
            
            # Since resumable=False, we just execute once
            response = request.execute()

            video_id: str = response["id"]
            log.info("  ✓ Uploaded → https://youtube.com/shorts/%s", video_id)
            return {"id": video_id, "title": title, "status": "success"}

        except HttpError as exc:
            last_exc = exc
            if exc.resp.status in (500, 502, 503):
                delay = config.RETRY_BASE_DELAY ** attempt
                log.warning(
                    "  Transient HTTP %s — retrying in %.1f s…", exc.resp.status, delay
                )
                time.sleep(delay)
            else:
                log.error("  Non-retryable YouTube error: %s", exc)
                raise
        except Exception as exc:
            last_exc = exc
            delay = config.RETRY_BASE_DELAY ** attempt
            log.warning("  Upload error: %s — retrying in %.1f s…", exc, delay)
            time.sleep(delay)

    log.error("  ✗ All %d upload attempts failed for '%s'", config.MAX_RETRIES, title)
    return {"id": "", "title": title, "status": f"failed: {last_exc}"}


# ── Public API ───────────────────────────────────────────────

def upload_clips(
    clip_paths: List[str],
    original_title: str,
    description: str = "",
    tags: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Upload all *clip_paths* to YouTube Shorts.

    Each clip is titled: ``{original_title} - Part X | #Shorts``

    Returns a list of result dicts (one per clip).
    """
    config.validate_youtube_config()
    youtube = _get_authenticated_service()
    tags = tags or []

    results: List[Dict[str, str]] = []
    total = len(clip_paths)

    for idx, path in enumerate(
        tqdm(clip_paths, desc="YouTube uploads", colour="red"), start=1
    ):
        title = f"{original_title} - Part {idx} | #Shorts"
        clip_desc = (
            f"{description}\n\n"
            f"Part {idx} of {total}\n"
            f"#Shorts #Short"
        )
        result = _upload_single(youtube, path, title, clip_desc, tags)
        results.append(result)

    return results
