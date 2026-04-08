# 🎬 shorts-bot

> Fully automated pipeline: **Download any video → Split into vertical shorts → Upload to YouTube Shorts & Instagram Reels**

```
shorts-bot/
├── main.py               # CLI entrypoint
├── config.py             # Secrets & settings from .env
├── downloader.py         # yt-dlp video downloader
├── processor.py          # FFmpeg split + reformat (9:16)
├── youtube_uploader.py   # YouTube Data API v3 upload
├── instagram_uploader.py # Meta Graph API upload
├── logger.py             # Colored logging
├── requirements.txt      # Python dependencies
├── .env.example          # Template for secrets
└── README.md             # ← you are here
```

---

## 📋 Prerequisites

| Tool          | Version  | Purpose                          |
|---------------|----------|----------------------------------|
| Python        | ≥ 3.10   | Runtime                          |
| FFmpeg        | ≥ 5.0    | Video processing                 |
| pip           | latest   | Package manager                  |

---

## 1️⃣ Install FFmpeg

### Windows (via winget)
```powershell
winget install --id Gyan.FFmpeg -e --source winget
# then restart your terminal so ffmpeg is on PATH
ffmpeg -version
```

### Windows (manual)
1. Download from https://www.gyan.dev/ffmpeg/builds/ (full build)
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your system PATH
4. Verify: `ffmpeg -version`

### macOS
```bash
brew install ffmpeg
```

### Ubuntu / Debian
```bash
sudo apt update && sudo apt install ffmpeg -y
```

---

## 2️⃣ Python Setup

```bash
# Clone / navigate to project
cd shorts-bot

# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install deps
pip install -r requirements.txt
```

---

## 3️⃣ YouTube OAuth Credentials  (step by step)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use an existing one)
3. Enable the **YouTube Data API v3**:
   - APIs & Services → Library → search "YouTube Data API v3" → Enable
4. Create OAuth 2.0 credentials:
   - APIs & Services → Credentials → **+ CREATE CREDENTIALS** → OAuth client ID
   - Application type: **Desktop app**
   - Click **Create**
5. Download the JSON file and save it as `client_secret.json` in the project root
6. Configure the **OAuth consent screen**:
   - APIs & Services → OAuth consent screen
   - User type: **External** (or Internal if using Google Workspace)
   - Add your email as a **test user**
   - Add scope: `https://www.googleapis.com/auth/youtube.upload`

> **First run:** A browser window will open asking you to authorize. After that, a `token.json` file is saved and re-used automatically.

---

## 4️⃣ Instagram Graph API Token  (step by step)

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create a new app → choose **Business** type
3. Add the **Instagram Graph API** product
4. Link your **Facebook Page** and **Instagram Business Account**
5. Get your tokens:
   - Go to **Graph API Explorer**
   - Select your app
   - Generate a **User Access Token** with these permissions:
     - `instagram_content_publish`
     - `instagram_basic`
     - `pages_read_engagement`
   - Click **Generate Access Token**
6. Get your **Instagram Business Account ID**:
   ```
   GET /me/accounts?fields=instagram_business_account&access_token={token}
   ```
7. Copy the values into `.env`:
   ```env
   INSTAGRAM_ACCESS_TOKEN=your_long_lived_token
   INSTAGRAM_BUSINESS_ACCOUNT_ID=123456789
   ```

> **⚠️ Important:** Instagram requires clips to be hosted at a **publicly accessible URL** (not local files). You'll need to upload clips to a server/CDN first. The bot will warn you about this.

> **Token expiry:** Page tokens are long-lived (~60 days). Refresh via the [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/).

---

## 5️⃣ Environment Setup

```bash
# Copy the template
cp .env.example .env

# Edit with your real values
# Windows: notepad .env
# macOS/Linux: nano .env
```

Fill in:
```env
YOUTUBE_CLIENT_SECRET_FILE=client_secret.json
INSTAGRAM_ACCESS_TOKEN=your_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
OUTPUT_DIR=./output
NUM_CLIPS=5
MAX_CLIP_DURATION=59
```

---

## 🚀 Usage

### Basic run (full pipeline)
```bash
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --clips 5
```

### Dry run (download + process only, no uploads)
```bash
python main.py --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --clips 3 --dry-run
```

### Skip specific platforms
```bash
# YouTube only
python main.py --url "https://..." --skip-instagram

# Instagram only
python main.py --url "https://..." --skip-youtube
```

### Custom output directory
```bash
python main.py --url "https://..." --output-dir ./my_clips
```

---

## 📊 Output

After a run, you'll see a summary table:

```
──────────────────────────────────────────────────────────────────────────────────────────
  📊  UPLOAD SUMMARY
──────────────────────────────────────────────────────────────────────────────────────────
  Clip                           YouTube                        Instagram
  ────────────────────────────── ────────────────────────────── ──────────────────────────────
  clip_01_of_05.mp4              ✅ success                     ✅ success
  clip_02_of_05.mp4              ✅ success                     ⏭️ skipped: no public URL
  clip_03_of_05.mp4              ✅ success                     ⏭️ skipped: no public URL
  clip_04_of_05.mp4              ✅ success                     ⏭️ skipped: no public URL
  clip_05_of_05.mp4              ✅ success                     ⏭️ skipped: no public URL
──────────────────────────────────────────────────────────────────────────────────────────
```

---

## 🗂️ Generated Files

```
output/
├── Original Video Title.mp4     ← downloaded source
└── clips/
    ├── clip_01_of_05.mp4        ← 1080×1920 vertical, H.264
    ├── clip_02_of_05.mp4
    ├── clip_03_of_05.mp4
    ├── clip_04_of_05.mp4
    └── clip_05_of_05.mp4
```

Each clip:
- 📐 1080×1920 (9:16 vertical)
- 🎞️ H.264 video + AAC audio
- ⏱️ ≤ 59 seconds
- 📝 "Part X of N" text burned in

---

## 🔧 Troubleshooting

| Problem | Fix |
|---------|-----|
| `ffmpeg: command not found` | Install FFmpeg and add to PATH |
| `yt-dlp` download error | Update: `pip install -U yt-dlp` |
| YouTube 403 error | Re-authorize: delete `token.json` and re-run |
| YouTube quota exceeded | Wait 24h or request quota increase in Cloud Console |
| IG "media not ready" | Video may be too large; try shorter clips |
| IG requires public URL | Host clips on a public server before uploading |

---

## 📄 License

MIT — use freely, no warranties.
