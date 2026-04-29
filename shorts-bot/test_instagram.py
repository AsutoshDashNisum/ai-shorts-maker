import sys
import os
from instagram_uploader import upload_to_instagram
from logger import log

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 test_instagram.py <your_ngrok_url>")
        print("Example: python3 test_instagram.py https://a1b2-c3d4.ngrok-free.app")
        return

    ngrok_url = sys.argv[1].rstrip('/')
    
    # If the URL is already a direct link to a file, use it.
    if ngrok_url.endswith('.mp4'):
        video_public_url = ngrok_url
    else:
        # We will test with clip_01_of_05.mp4 (already in output/clips/)
        clip_filename = "clip_01_of_05.mp4"
        video_public_url = f"{ngrok_url}/{clip_filename}"
    
    caption = "Mr. Bean Fun! 🤩 #mrbean #funny #shorts #reels"

    log.info(f"🚀 Starting Test Upload for Instagram Reels")
    log.info(f"Target URL: {video_public_url}")
    
    result = upload_to_instagram(video_public_url, caption)
    
    if result:
        log.info("✅ TEST PASSED! The video should be live on your Instagram Reels shortly.")
    else:
        log.error("❌ TEST FAILED. Check the error messages above.")

if __name__ == "__main__":
    main()
