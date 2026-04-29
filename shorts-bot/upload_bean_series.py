import os
import re
import youtube_uploader as ytu
from pathlib import Path
from logger import log

def upload_bean_series():
    # Configuration
    clips_dir = "/Users/adash/Downloads/Desktop/ai shorts maker/output_bean_full"
    original_title = "Mr Bean Morning Tea"
    description = "When your morning tea is anything but peaceful... ☕️🤣 Mr. Bean's morning routine is a total mood! Starting the day with Mr. Bean means starting it with pure chaos! Watch how he handles his morning tea in this classic clip."
    tags = ["MrBean", "MorningRoutine", "Chaos", "Relatable", "ComedyGold", "FunnyVideos", "MorningTea", "MrBeanCartoon", "ClassicComedy", "Shorts", "Reels"]

    # 1. Get all mp4 files
    files = [f for f in os.listdir(clips_dir) if f.endswith(".mp4")]
    
    # 2. Sort them numerically
    def extract_number(filename):
        match = re.search(r'Part_(\d+)', filename)
        return int(match.group(1)) if match else 0
    
    files.sort(key=extract_number)
    
    full_paths = [os.path.join(clips_dir, f) for f in files]
    total = len(full_paths)
    
    print(f"🚀 Found {total} Mr. Bean parts. Starting upload...")
    log.info(f"Starting bulk upload of {total} clips from {clips_dir}")

    # 3. Get authenticated service
    try:
        youtube = ytu._get_authenticated_service()
    except Exception as e:
        print(f"❌ Auth failed: {e}")
        return

    # 4. Upload loop
    for i, path in enumerate(full_paths, start=1):
        if not os.path.exists(path):
            print(f"❌ Clip not found: {path}")
            continue
            
        title = f"{original_title} - Part {i} | #Shorts"
        clip_desc = f"{description}\n\nPart {i} of {total}\n#Shorts #Short #Comedy #Funny"
        
        print(f"📤 [{i}/{total}] Uploading {title}...")
        try:
            result = ytu._upload_single(youtube, path, title, clip_desc, tags)
            
            if result['status'] == 'success':
                print(f"✅ Successfully uploaded: {title}")
            else:
                print(f"❌ Failed to upload {title}: {result['status']}")
                # If we hit a quota limit, we should probably stop
                if "quota" in result['status'].lower():
                    print("🛑 Quota exceeded! Stopping upload.")
                    break
        except Exception as e:
            print(f"❌ Critical error uploading {title}: {e}")
            break

    print("🏁 Upload process finished.")

if __name__ == "__main__":
    upload_bean_series()
