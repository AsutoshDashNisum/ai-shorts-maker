import subprocess
from pathlib import Path

# Config
VIDEO_PATH = Path(r"C:\Users\adash\Downloads\Morning Tea _ Funny Episodes _ Mr Bean Cartoon World.mp4")
OUTPUT_DIR = Path(r"c:\Users\adash\Desktop\ai shorts maker\output_bean_full")
CLIP_DURATION = 60  # seconds per part
TOTAL_DURATION = 2450.84  # Total video length in seconds

def force_split_full():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Calculate total parts
    total_parts = int(TOTAL_DURATION // CLIP_DURATION) + (1 if TOTAL_DURATION % CLIP_DURATION > 0 else 0)
    
    print(f"Bypassing AI... Splitting full 40m into {total_parts} clips (60s each).")
    
    for i in range(total_parts):
        start = i * CLIP_DURATION
        duration = CLIP_DURATION
        
        # Ensure last clip doesn't over-run
        if (start + duration) > TOTAL_DURATION:
            duration = TOTAL_DURATION - start
            
        part_num = i + 1
        label_text = f"Part {part_num} of {total_parts} Mr Bean Funny"
        out_file = OUTPUT_DIR / f"Mr_Bean_Part_{part_num}.mp4"
        
        print(f"--- Exporting {part_num}/{total_parts} ({duration:.1f}s) ---")
        
        # Branding filter (Safe Windows Path format)
        filter_str = (
            "scale=1080:1920:force_original_aspect_ratio=decrease,"
            "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,"
            f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{label_text}':fontcolor=white:fontsize=70:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100,"
            "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Follow @the_anitadka':fontcolor=yellow:fontsize=80:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-200"
        )

        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", str(VIDEO_PATH),
            "-t", str(duration),
            "-vf", filter_str,
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", 
            "-c:a", "aac", "-b:a", "128k",
            str(out_file)
        ]
        
        subprocess.run(cmd)

if __name__ == "__main__":
    force_split_full()
