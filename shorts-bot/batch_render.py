import asyncio
import edge_tts
import subprocess
import os
from pathlib import Path

# Configuration
BG_MUSIC = "/Users/adash/Downloads/Attitude song  attitude background music no copyright  no copyright attitude song  ncs attitude - YT HELPER EDITOR.mp3"
VOICE = "hi-IN-MadhurNeural"
RATE = "+25%"
FFMPEG_PATH = "/Users/adash/Library/Python/3.9/bin/static_ffmpeg"

STORIES = [
    {
        "id": 6,
        "name": "Gym Freak",
        "text": """Abe oye 'Chicken Legs'! Gym sirf reel banane ke liye ja raha hai ya asli mein bicep phulana hai? Sharam kar, teri toh t-shirt bhi sweat se nahi, aansuon se gili ho rahi hai. Weight utha varna tera gym instructor tujhe hi dumbbell bana dega! Subscribe kar varna puri zindagi gym ka chanda hi bharta reh jayega!""",
        "video": "output/satisfying_clips/satisfying_clip_06.mp4",
        "output": "savage_gym_final.mp4"
    },
    {
        "id": 7,
        "name": "Boring Boss",
        "text": """Boss jab 'Let's take this offline' bolta hai, toh samajh jao tumhari weekend ki 'waat' lagne wali hai. Camera off karke so jao aur Zoom pe 'Net kharab hai' ka bahana maaro. Promotion toh nahi milega, par sukoon ki neend zaroor milegi! Like thoko varna kal tera boss tere ghar hi meeting rakh lega!""",
        "video": "output/satisfying_clips/satisfying_clip_07.mp4",
        "output": "savage_boss_final.mp4"
    },
    {
        "id": 8,
        "name": "Wedding Buffet",
        "text": """Shaadi mein jaake aise toot-te ho jaise 4 saal se bhooke nange ghum rahe ho. Paneer ke liye aise ladte ho jaise Woh Kohinoor diamond ho. Thora sharam kar bhai, ladki wale tujhe plates dhone pe laga denge! Share kar un doston ko jo shaadi sirf khane ke liye jaate hain!""",
        "video": "output/satisfying_clips/satisfying_clip_08.mp4",
        "output": "savage_wedding_final.mp4"
    },
    {
        "id": 9,
        "name": "Traffic Police",
        "text": """Jab door se Mama dikhe aur pass mein helmet na ho, toh aise U-turn maaro jaise tum Rohit Shetty ki movie ke hero ho. Pakde gaye toh 'Mummy bimar hai' wala card phenko. Emotional damage 100%! Follow karo varna kal tera licence pakka cancel hai!""",
        "video": "output/satisfying_clips/satisfying_clip_09.mp4",
        "output": "savage_police_final.mp4"
    },
    {
        "id": 10,
        "name": "Customer Care",
        "text": """Helpline pe call karo toh 'Your call is important' bolke 40 minute tak wahi flute music sunate hain. Inse baas ek hi cheez seekho—Inka patience. Account band ho jaye par inka music nahi rukta! Subscribe karo varna agla number tumhara hi hold pe hoga!""",
        "video": "output/satisfying_clips/satisfying_clip_10.mp4",
        "output": "savage_helpline_final.mp4"
    }
]

async def process_story(story):
    story_id = story["id"]
    text = story["text"]
    voice_file = f"temp_voice_{story_id}.mp3"
    subs_file = f"temp_subs_{story_id}.vtt"
    input_video = story["video"]
    output_video = story["output"]

    print(f"--- Processing Story {story_id}: {output_video} ---")
    
    # 1. Generate Voice & Subs
    cmd_tts = [
        "python3", "-m", "edge_tts",
        "--text", text,
        "--voice", VOICE,
        "--rate", RATE,
        "--write-media", voice_file,
        "--write-subtitles", subs_file
    ]
    subprocess.run(cmd_tts, check=True)
    
    # 2. Render Final Video
    audio_filter = (
        "[1:a]volume=1.8[voice];"
        "[2:a]volume=0.15[bg];"
        "[voice][bg]amix=inputs=2:duration=first[aout]"
    )
    sub_style = "Alignment=2,FontSize=12,PrimaryColour=&H00FFFF,OutlineColour=&H000000,BorderStyle=1,Outline=1"
    v_filter = f"[0:v]scale=-1:1920,crop=1080:1920,subtitles={subs_file}:force_style='{sub_style}'[fullv]"

    cmd_ffmpeg = [
        FFMPEG_PATH, "-y",
        "-i", input_video,
        "-i", voice_file,
        "-i", BG_MUSIC,
        "-filter_complex", f"{v_filter};{audio_filter}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-map", "[fullv]",
        "-map", "[aout]",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd_ffmpeg, check=True)
    
    os.remove(voice_file)
    os.remove(subs_file)
    print(f"[OK] Story {story_id} Complete!")

async def main():
    tasks = [process_story(s) for s in STORIES]
    await asyncio.gather(*tasks)
    print("\n--- BATCH PROCESSED! ---")

if __name__ == "__main__":
    asyncio.run(main())
