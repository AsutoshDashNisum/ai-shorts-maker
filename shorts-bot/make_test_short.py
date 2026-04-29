import asyncio
import edge_tts
import subprocess
import os
from pathlib import Path

# Configuration
TEXT_SCRIPT = """
Doston, kya aapke papa bhi subah 5 baje uthakar puchte hain ki 'Zindagi mein kya ukhada hai?' Don’t worry! Aaj main bataunga Top 5 hacks to handle your Strict Papa. Last waala toh bilkul Miss mat karna!

Jab Papa gusse mein hall mein baithe hon, toh wahan se aise guzro jaise tum Mr. India ho. Aankh mat milana, varna 'Beta idhar aao' sunte hi tumhari file band ho jayegi!

Hamesha apne haath mein ek moti kitaab rakho. UPSC level ki honi chahiye. Papa ko lagega ladka desh badalne wala hai, par asliyat mein toh tum uske peeche reel dekh rahe ho. Legend move!

Jab lage ki pitayi hone wali hai, turant kitchen mein jaake mummy ki help karne lago. Papa ka gussa thanda ho jayega kyunki 'Beta sudhar gaya hai.' (Sirf 10 minute ke liye!)

Agar galti se pakde gaye, toh phone khud hi unke haath mein de do aur bolo 'Papa yeh phone hi saari fasaad ki jad hai.' Reverse psychology, bhai! Woh confuse ho jayenge.

Aur sabse bada hack... jab kuch kaam na aaye, toh zor se bolo: 'Mummy, dekho Papa kya bol rahe hain!' Bas, game khatam. Papa ki bolti band, aur aap safe! Like aur subscribe karo varna agla number tumhara hai!
"""

VOICE = "hi-IN-MadhurNeural"
RATE = "+25%"  # High energy
OUTPUT_AUDIO = "test_audio.mp3"
INPUT_VIDEO = "output/satisfying_clips/satisfying_clip_01.mp4"
FINAL_OUTPUT = "final_troll_short_v2.mp4"
FFMPEG_PATH = "/Users/adash/Library/Python/3.9/bin/static_ffmpeg"

async def generate_audio():
    print("--- Generating AI Voice (Hindi Troll Style)...")
    communicate = edge_tts.Communicate(TEXT_SCRIPT, VOICE, rate=RATE)
    await communicate.save(OUTPUT_AUDIO)
    print(f"[OK] Audio saved to {OUTPUT_AUDIO}")

def create_short():
    print("--- Refactoring: Mixing Chad Music & Fixing Captions...")
    
    # Manually wrapped lines to prevent overflow
    lines = [
        "Top 5 Hacks\\:\nHandling Strict Papa",
        "Papa gusse mein hon toh\nMr. India bano!",
        "Hamesha moti kitaab\nhaath mein rakho!",
        "Kitchen mein mummy ki\nhelp karne lago!",
        "Phone khud hi Papa\n ko de do!",
        "Ultimate Weapon\\:\nMUMMY KO BULAO!"
    ]
    
    # Correctly chain drawtext filters
    current_input = "[0:v]"
    drawtext_chain = ""
    for i, line in enumerate(lines):
        start = i * 10
        end = (i + 1) * 10
        output_label = f"[v{i+1}]"
        # Fontsize reduced to 55 for better fit
        drawtext_chain += (
            f"{current_input}drawtext=text='{line}':fontcolor=yellow:fontsize=55:fontfile='/Library/Fonts/Arial.ttf':"
            f"borderw=4:bordercolor=black:line_spacing=10:x=(w-text_w)/2:y=(h-text_h)/2:enable='between(t,{start},{end})'{output_label};"
        )
        current_input = output_label
        
    # Audio filtering: 
    # [1:a] is our voice
    # synth is our background beat
    audio_filter = (
        "aevalsrc=sin(440*PI*2*t):d=60,aecho=0.8:0.8:40:0.3,volume=0.05[bg];"
        "[1:a]volume=1.5[voice];"
        "[voice][bg]amix=inputs=2:duration=first[aout]"
    )

    cmd = [
        FFMPEG_PATH, "-y",
        "-i", INPUT_VIDEO,
        "-i", OUTPUT_AUDIO,
        "-filter_complex", f"{drawtext_chain}{audio_filter}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-map", f"{current_input}",
        "-map", "[aout]",
        "-shortest",
        FINAL_OUTPUT
    ]
    
    subprocess.run(cmd, check=True)
    print(f"\n[SUCCESS] Your refactored short is ready: {FINAL_OUTPUT}")

if __name__ == "__main__":
    asyncio.run(generate_audio())
    create_short()
