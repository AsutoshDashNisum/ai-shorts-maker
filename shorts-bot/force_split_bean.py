import json
import subprocess
from pathlib import Path

# Paths
REPORT_PATH = Path(r"c:\Users\adash\Desktop\ai shorts maker\shorts-bot\Morning Tea _ Funny Episodes _ Mr Bean Cartoon World_analysis.json")
VIDEO_PATH = Path(r"C:\Users\adash\Downloads\Morning Tea _ Funny Episodes _ Mr Bean Cartoon World.mp4")
OUTPUT_DIR = Path(r"c:\Users\adash\Desktop\ai shorts maker\output_analysis_BEAN")

def force_split():
    if not REPORT_PATH.exists():
        print(f"Error: Report {REPORT_PATH} not found.")
        return
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(REPORT_PATH, 'r') as f:
        data = json.load(f)
    
    clips = data.get('clips', [])
    print(f"Starting force-split of {len(clips)} clips from report...")
    
    for i, clip in enumerate(clips):
        start = clip['start']
        end = clip['end']
        duration = float(end) - float(start)
        label = clip.get('label', f'Part_{i+1}').replace(" ", "_").replace("'", "")
        out_file = OUTPUT_DIR / f"{label}.mp4"
        
        print(f"--- Processing Clip {i+1}: {label} ({duration}s) ---")
        
        # Robust drawtext formatting - SANITIZE TEXT FOR FFMPEG
        part_info = f"Part {i+1} of {len(clips)}"
        # Remove colons and special chars that break ffmpeg filters
        safe_label = label.replace('_', ' ').replace(':', '').replace("'", "")
        label_text = f"{part_info} {safe_label}"
        
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
        
        print(f"Exporting {label} with branding...")
        subprocess.run(cmd)

if __name__ == "__main__":
    force_split()
