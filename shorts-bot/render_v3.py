import asyncio
import edge_tts
import subprocess
import os
from pathlib import Path

# Configuration
BG_MUSIC = "/Users/adash/Downloads/Attitude song  attitude background music no copyright  no copyright attitude song  ncs attitude - YT HELPER EDITOR.mp3"
TEXT_SCRIPT = """
Doston, kya aapke papa bhi subah 5 baje uthakar puchte hain ki 'Zindagi mein kya ukhada hai?' Don’t worry! Aaj main bataunga Top 5 hacks to handle your Strict Papa. Last waala toh bilkul Miss mat karna!

Jab Papa gusse mein hall mein baithe hon, toh wahan se aise guzro jaise tum Mr. India ho. Aankh mat milana, varna 'Beta idhar aao' sunte hi tumhari file band ho jayegi!

Hamesha apne haath mein ek moti kitaab rakho. UPSC level ki honi chahiye. Papa ko lagega ladka desh badalne wala hai, par asliyat mein toh tum uske peeche reel dekh rahe ho. Legend move!

Jab lage ki pitayi hone wali hai, turant kitchen mein jaake mummy ki help karne lago. Papa ka gussa thanda ho jayega kyunki 'Beta sudhar gaya hai.' (Sirf 10 minute ke liye!)

Agar galti se pakde gaye, toh phone khud hi unke haath mein de do aur bolo 'Papa yeh phone hi saari fasaad ki jad hai.' Reverse psychology, bhai! Woh confuse ho jayenge.

Aur sabse bada hack... jab kuch kaam na aaye, toh zor se bolo: 'Mummy, dekho Papa kya bol rahe hain!' Bas, game khatam. Papa ki bolti band, aur aap safe! Like aur subscribe karo varna agla number tumhara hai!
"""

VOICE = "hi-IN-MadhurNeural"
RATE = "+25%"
OUTPUT_VOICE = "temp_voice.mp3"
OUTPUT_SUBS = "temp_subs.vtt"
INPUT_VIDEO = "output/satisfying_clips/satisfying_clip_01.mp4"
FINAL_OUTPUT = "final_troll_short_v3.mp4"
FFMPEG_PATH = "/Users/adash/Library/Python/3.9/bin/static_ffmpeg"

async def generate_assets():
    print("--- Generating AI Voice & Word-Synced Subtitles...")
    # Using CLI for more stability between versions
    cmd = [
        "python3", "-m", "edge_tts",
        "--text", TEXT_SCRIPT,
        "--voice", VOICE,
        "--rate", RATE,
        "--write-media", OUTPUT_VOICE,
        "--write-subtitles", OUTPUT_SUBS
    ]
    subprocess.run(cmd, check=True)
    print("[OK] Assets generated.")

def render_final():
    print("--- Pro Rendering: Mixing Audio & Burning Bottom Subtitles...")
    
    # Audio Filter: 
    # [0:a] is video audio (silent)
    # [1:a] is commentary
    # [2:a] is background music
    audio_filter = (
        "[1:a]volume=1.8[voice];"
        "[2:a]volume=0.15[bg];"
        "[voice][bg]amix=inputs=2:duration=first[aout]"
    )
    
    # Subtitle Filter:
    # Using 'subtitles' filter with the generated VTT
    # We'll set the style to be at the bottom with smaller font
    # force_style uses ASS style parameters
    sub_style = "Alignment=2,FontSize=14,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1"

    cmd = [
        FFMPEG_PATH, "-y",
        "-i", INPUT_VIDEO,
        "-i", OUTPUT_VOICE,
        "-i", BG_MUSIC,
        "-filter_complex", f"{audio_filter}",
        "-vf", f"subtitles={OUTPUT_SUBS}:force_style='{sub_style}'",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-map", "0:v:0",
        "-map", "[aout]",
        "-shortest",
        FINAL_OUTPUT
    ]
    
    subprocess.run(cmd, check=True)
    print(f"\n[SUCCESS] V3 Short Complete! Check: {FINAL_OUTPUT}")

if __name__ == "__main__":
    asyncio.run(generate_assets())
    render_final()
