import sys
import time
import requests
import os
import re
from instagram_uploader import upload_to_instagram

STATE_FILE = "last_uploaded_bean.txt"

def get_start_part():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            content = f.read().strip()
            if content.isdigit():
                # Start from the part immediately following the last successful one
                return int(content) + 1
    # If no state file, we assume part 7 since 1-6 are done
    return 7

def save_state(part_num):
    with open(STATE_FILE, "w") as f:
        f.write(str(part_num))

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

def upload_bean_series():
    clips_dir = "/Users/adash/Downloads/Desktop/ai shorts maker/output_bean_full"
    caption_template = "When your morning tea is anything but peaceful... ☕️🤣 Mr. Bean's morning routine is a total mood! Part {part_num}\n\n#MrBean #MorningRoutine #Chaos #Relatable #ComedyGold #FunnyVideos #MorningTea #MrBeanCartoon #ClassicComedy #Shorts #Reels"

    files = [f for f in os.listdir(clips_dir) if f.endswith(".mp4")]
    
    def extract_number(filename):
        match = re.search(r'Part_(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    files.sort(key=extract_number)
    
    start_part = get_start_part()
    files_to_upload = [f for f in files if extract_number(f) >= start_part]
    total_files = len(files_to_upload)

    if total_files == 0:
        print("🎉 No more clips to upload. All parts are finished!")
        return

    print(f"--- 🚀 RESUMABLE INSTAGRAM LAUNCH: Mr. Bean ---")
    print(f"Starting from Part {start_part}. Total remaining: {total_files}")

    for i, filename in enumerate(files_to_upload, start=1):
        part_num = extract_number(filename)
        filepath = os.path.join(clips_dir, filename)
        caption = caption_template.format(part_num=part_num)
        
        print(f"\nProcessing: Mr. Bean Part {part_num}...")
        try:
            # Step 1: Upload to public CDN
            public_url = upload_to_cdn(filepath)

            # Step 2: Push to Instagram
            media_id = upload_to_instagram(public_url, caption)
            if not media_id:
                raise Exception("Instagram API returned None - upload failed!")
                
            print(f"[OK] Part {part_num} Posted to Instagram! Media ID: {media_id}")
            
            # Save progress so we know we successfully uploaded this part
            save_state(part_num)
            
            time.sleep(8)  # Avoid rate limiting
        except Exception as e:
            print(f"[CRITICAL ERROR] Part {part_num} failed: {e}")
            print("🛑 STOPPING UPLOAD PROCESS to preserve story sequence.")
            print("Please fix the issue (e.g., check internet) and re-run this script to resume.")
            sys.exit(1)

    print(f"\n--- ✅ ALL REELS PUBLISHED SUCCESSFULLY! ---")

if __name__ == "__main__":
    upload_bean_series()
