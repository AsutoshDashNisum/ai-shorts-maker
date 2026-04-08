import os
import youtube_uploader
from pathlib import Path

def resume():
    # Configuration
    clips_dir = "output/clips"
    original_title = "What If Chat GPT Was A Person 2"
    description = "Dosto, dekhlo agar ye asli insan hota toh kya hota! 😂🔥 #Shorts #Comedy #Funny #India #Desi #Animation #Viral"
    tags = ["Shorts", "Comedy", "Funny", "India", "Desi", "Animation", "AngryPrash"]
    
    # We want to upload Part 4 and Part 5
    # These correspond to clip_04_of_05.mp4 and clip_05_of_05.mp4
    remaining_clips = [
        os.path.join(clips_dir, "clip_04_of_05.mp4"),
        os.path.join(clips_dir, "clip_05_of_05.mp4")
    ]
    
    print(f"🚀 Resuming upload for {len(remaining_clips)} clips...")
    
    # We need to hack the index in upload_clips or just call _upload_single directly
    # Since upload_clips starts indexing from 1, we can't easily use it for Part 4/5 
    # without passing the whole list.
    
    import youtube_uploader as ytu
    youtube = ytu._get_authenticated_service()
    
    for i, path in enumerate(remaining_clips, start=4):
        if not os.path.exists(path):
            print(f"❌ Clip not found: {path}")
            continue
            
        title = f"{original_title} - Part {i} | #Shorts"
        clip_desc = f"{description}\n\nPart {i} of 5\n#Shorts #Short"
        
        print(f"📤 Uploading {title}...")
        result = ytu._upload_single(youtube, path, title, clip_desc, tags)
        
        if result['status'] == 'success':
            print(f"✅ Successfully uploaded: {title}")
        else:
            print(f"❌ Failed to upload {title}: {result['status']}")

if __name__ == "__main__":
    resume()
