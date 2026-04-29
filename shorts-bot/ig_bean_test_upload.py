import sys
import time
import requests
import os
from instagram_uploader import upload_to_instagram

def upload_to_cdn(filepath):
    print(f"  Hosting {filepath} publicly via catbox.moe...")
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://litterbox.catbox.moe/resources/internals/api.php',
            data={'reqtype': 'fileupload', 'time': '72h'},
            files={'fileToUpload': f}
        )
    if response.status_code == 200 and response.text.startswith('https://'):
        url = response.text.strip()
        print(f"  Public URL: {url}")
        return url
    else:
        raise Exception(f"CDN Upload Failed: {response.text}")

def test_single_upload():
    clips_dir = "/Users/adash/Downloads/Desktop/ai shorts maker/output_bean_full"
    filepath = os.path.join(clips_dir, "Mr_Bean_Part_7.mp4")
    part_num = 7
    caption = f"When your morning tea is anything but peaceful... ☕️🤣 Mr. Bean's morning routine is a total mood! Part {part_num}\n\n#MrBean #MorningRoutine #Chaos #Relatable #ComedyGold #FunnyVideos #MorningTea #MrBeanCartoon #ClassicComedy #Shorts #Reels"

    print(f"--- 🚀 TEST LAUNCH: Uploading Mr. Bean Part {part_num} ---")
    
    try:
        # Step 1: Upload to public CDN
        public_url = upload_to_cdn(filepath)

        # Step 2: Push to Instagram
        upload_to_instagram(public_url, caption)
        print(f"\n[OK] Part {part_num} Posted to Instagram Successfully!")
    except Exception as e:
        print(f"\n[ERROR] Part {part_num} failed: {e}")

if __name__ == "__main__":
    test_single_upload()
