import subprocess
import os
from pathlib import Path

# Configuration
VIDEO_PATH = "/Users/adash/Downloads/The Most Satisfying Videos On The Internet - Daily Dose Of Internet (360p, h264).mp4"
OUTPUT_DIR = Path("./output/satisfying_clips")
CLIP_DURATION = 59  # Seconds

def split_video():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get total duration using ffprobe or ffmpeg
    # (We already know it's ~21:23 from previous check)
    total_duration = 1283 
    
    num_clips = (total_duration // CLIP_DURATION) + 1
    print(f"Creating {num_clips} clips...")

    for i in range(num_clips):
        start_time = i * CLIP_DURATION
        output_path = OUTPUT_DIR / f"satisfying_clip_{i+1:02d}.mp4"
        
        print(f"Exporting clip {i+1}/{num_clips} (starting at {start_time}s)...")
        
        # FFmpeg command:
        # -an: Remove audio
        # -vf: scale to 1080:1920 with padding (black bars)
        # -c:v libx264: encode with x264
        cmd = [
            "/usr/local/bin/ffmpeg", "-y",
            "-ss", str(start_time),
            "-t", str(CLIP_DURATION),
            "-i", VIDEO_PATH,
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
            "-an",  # REMOVE AUDIO
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "23",
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True)

    print(f"\n[SUCCESS] Exported {num_clips} clips to {OUTPUT_DIR}")

if __name__ == "__main__":
    split_video()
