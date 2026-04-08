import os
import sys
import json
import base64
import time
import argparse
import subprocess
import requests
import cv2
from pathlib import Path
from tqdm import tqdm
from PIL import Image
import concurrent.futures

# Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_PULL_URL = "http://localhost:11434/api/pull"
OLLAMA_MODELS = ["qwen2.5:7b", "llama3:8b"]
REQUIRED_PIP = ["openai-whisper", "opencv-python", "Pillow", "requests", "tqdm", "ffmpeg-python"]
OUTPUT_BASE = Path("./output_analysis")
TEMP_DIR = Path("./temp_frames")

# =============================================================================
# PHASE 1: SETUP & DEPENDENCY CHECK
# =============================================================================

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_pip_packages():
    import importlib.util
    missing = []
    # Mapping for packages that have different import names
    mapping = {
        "openai-whisper": "whisper",
        "opencv-python": "cv2",
        "ffmpeg-python": "ffmpeg"
    }
    for pkg in REQUIRED_PIP:
        import_name = mapping.get(pkg, pkg)
        if importlib.util.find_spec(import_name) is None:
            missing.append(pkg)
    return missing

def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            existing_models = [m['name'] for m in response.json().get('models', [])]
            return True, existing_models
    except requests.exceptions.ConnectionError:
        pass
    return False, []

def pull_ollama_model(model_name):
    print(f"--- Pulling Ollama model '{model_name}'... This may take a while.")
    payload = {"name": model_name}
    with requests.post(OLLAMA_PULL_URL, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                status = json.loads(line)
                if 'status' in status:
                    print(f"  > {model_name}: {status['status']}", end='\r')
    print(f"\n[DONE] Model '{model_name}' is ready.")

def phase_1_setup():
    print("\n" + "="*60)
    print("PHASE 1: STARTING SETUP & DEPENDENCY CHECK")
    print("="*60)

    # 1. FFmpeg
    if not check_ffmpeg():
        print("[ERROR] FFmpeg not found! Please install it.")
        sys.exit(1)
    print("[OK] FFmpeg detected.")

    # 2. Pip Packages
    missing_pip = check_pip_packages()
    if missing_pip:
        print(f"[INSTALLING] Missing packages: {', '.join(missing_pip)}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_pip)
    print("[OK] Python packages verified.")

    # 3. Ollama
    running, models = check_ollama()
    if not running:
        print("[ERROR] Ollama is NOT running or not installed!")
        print("Please download and start Ollama from: https://ollama.com")
        sys.exit(1)
    print("[OK] Ollama is running.")

    for m in OLLAMA_MODELS:
        if not any(m in existing for existing in models):
            pull_ollama_model(m)
        else:
            print(f"[OK] Model '{m}' detected.")

    print("\n" + "="*60)
    print("Setup complete. Please provide the video path to analyze.")
    print("="*60)

# =============================================================================
# PHASE 2: VIDEO ANALYSIS
# =============================================================================

def extract_frames(video_path):
    print(f"--- Extracting frames (1 frame/0.5s) from {video_path}...")
    TEMP_DIR.mkdir(exist_ok=True)
    # Clear old frames safely
    for f in TEMP_DIR.glob("*.jpg"):
        try:
            f.unlink(missing_ok=True)
        except PermissionError:
            pass
    
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-vf", "fps=2",
        "-q:v", "2",
        str(TEMP_DIR / "frame_%04d.jpg")
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    frames = sorted(list(TEMP_DIR.glob("*.jpg")))
    print(f"[OK] Extracted {len(frames)} frames.")
    return frames

def transcribe_audio(video_path):
    print("--- Transcribing audio with Whisper (base)...")
    import whisper
    model = whisper.load_model("tiny")
    result = model.transcribe(str(video_path))
    print("[OK] Transcription complete.")
    return result

def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def analyze_visuals_qwen(frames):
    print("--- Analyzing visual patterns with qwen2-vl...")
    sample_size = min(len(frames), 20)
    step = len(frames) // sample_size
    sampled_frames = frames[::step]
    
    analysis_results = []
    
    for i, frame in enumerate(tqdm(sampled_frames, desc="Qwen Frame Analysis")):
        b64_image = encode_image(frame)
        prompt = """
        Analyze this video frame. Identify:
        1. Detected text on screen (font style, size, color, position).
        2. Visual energy/brightness.
        3. Is this a logo, title card, or actual content?
        4. Scene description.
        Return JSON format.
        """
        
        payload = {
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "images": [b64_image],
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(OLLAMA_URL, json=payload, timeout=None)
            if response.status_code == 200:
                analysis_results.append(response.json().get('response'))
        except Exception as e:
            print(f"[WARN] Qwen error on frame {i}: {e}")
            continue
            
    return analysis_results

def finalize_viral_llama(visual_data, transcription):
    print("--- Running Viral Pattern Analysis with llama3.3...")
    prompt = f"""
    You are a Viral Content Expert. Based on these visual findings and this transcription, 
    generate an analysis report for splitting this video into clips.

    Visual Data: {visual_data[:5]} ... (truncated)
    Transcript: {transcription['text'][:2000]} ... (truncated)

    Identify:
    - Best clip start/end timestamps (in seconds).
    - Episode and Part numbering.
    - Viral score (1-10) for each segment.
    - Caption style spec (font size, position, style).

    Return ONLY a JSON object with a 'clips' list containing { 'start', 'end', 'label', 'viral_score', 'style_spec' }.
    """
    
    payload = {
        "model": "llama3:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json"
    }
    
    response = requests.post(OLLAMA_URL, json=payload, timeout=None)
    return response.json().get('response')

def run_phase_2(video_path):
    print(f"\n[FILE] Processing: {video_path}")
    
    frames = extract_frames(video_path)
    transcription = transcribe_audio(video_path)
    visual_data = analyze_visuals_qwen(frames)
    report_json = finalize_viral_llama(visual_data, transcription)
    
    report_filename = f"{video_path.stem}_analysis.json"
    with open(report_filename, "w", encoding='utf-8') as f:
        f.write(report_json)
        
    print("\n" + "="*60)
    print(f"[OK] Analysis complete. Report saved as '{report_filename}'.")
    print("Ready to split - provide confirmation to proceed (type 'yes').")
    print("="*60)
    return report_filename

# =============================================================================
# PHASE 3: CLIP SPLITTING
# =============================================================================

def run_phase_3(video_path, report_filename):
    print(f"--- Starting PHASE 3: Clip Splitting using {report_filename}...")
    
    with open(report_filename, "r") as f:
        report = json.load(f)
    
    clips = report.get('clips', [])
    
    for i, clip in enumerate(clips):
        start = clip['start']
        end = clip['end']
        duration = float(end) - float(start)
        label = clip.get('label', f"Part_{i+1}").replace(" ", "_").replace("→", "_")
        
        output_dir = OUTPUT_BASE / label.split("_")[0]
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{label}.mp4"
        
        print(f"[EXPORT] {label} ({start}s - {end}s)...")
        
        # Consistent vertical format with follow CTA branding
        drawtext_part = f"drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='{{label}}':fontcolor=white:fontsize=100:borderw=3:bordercolor=black:x=(w-text_w)/2:y=100"
        drawtext_follow = "drawtext=fontfile='C\\:/Windows/Fonts/arial.ttf':text='Follow @the_anitadka':fontcolor=yellow:fontsize=80:borderw=3:bordercolor=black:x=(w-text_w)/2:y=h-200"
        
        cmd = [
            "ffmpeg", "-y", "-ss", str(start), "-i", str(video_path),
            "-t", str(duration),
            "-vf", f"scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black,{drawtext_part},{drawtext_follow}",
            "-c:v", "libx264", "-preset", "fast", "-crf", "23", "-c:a aac", "-b:a 128k", str(output_path)
        ]
        
        full_cmd = " ".join(cmd)
        subprocess.run(full_cmd, shell=True, capture_output=False, check=False)
        
    print("\n" + "="*60)
    print("[OK] All clips exported. Check the /output_analysis folder.")
    print("="*60)

# =============================================================================
# MAIN ENTRY
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Local AI Video Factory Pipeline")
    parser.add_argument("--video", type=str, help="Path to video file")
    args = parser.parse_args()

    phase_1_setup()
    
    video_path = args.video
    if not video_path:
        video_path = input("\n[INPUT] Enter video path: ").strip().replace('"', '')
    
    p_video = Path(video_path)
    if not p_video.exists():
        print(f"[ERROR] File {video_path} not found.")
        sys.exit(1)
        
    report_filename = run_phase_2(p_video)
    
    confirm = input("\n[INPUT] Proceed with splitting? (yes/no): ").lower().strip()
    if confirm == "yes" or confirm == "y":
        run_phase_3(p_video, report_filename)
    else:
        print("Pipeline stopped by user.")
