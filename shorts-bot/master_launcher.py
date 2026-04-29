import subprocess
import sys
import logging

def run():
    print("--- 🎬 PHASE 1: Rendering 5 New Savage Shorts ---")
    subprocess.run(["python3", "batch_render.py"], check=True)

    print("\n--- 🚀 PHASE 2: Launching to YouTube ---")
    # Custom upload script for these 5
    upload_script = """
import sys
sys.path.append('.')
from youtube_uploader import _get_authenticated_service, _upload_single

CLIPS = [
    {'path': 'savage_gym_final.mp4', 'title': 'Gym Freaks: Stop the Show-off! 🏋️‍♂️💪 #shorts #hindi #gym', 'description': 'Savage roast for gym reelers. #funny #hindi #gym'},
    {'path': 'savage_boss_final.mp4', 'title': 'Meetings from Hell: The Boring Boss 💼💤 #shorts #hindi', 'description': 'How to survive boring office meetings. #workplace #roast #hindi'},
    {'path': 'savage_wedding_final.mp4', 'title': 'Wedding Buffet Monsters! 🍗🍛 #shorts #hindi #wedding', 'description': 'The struggle for paneer is real. #desi #wedding #funny'},
    {'path': 'savage_police_final.mp4', 'title': 'Traffic Mama vs Helmet-less Hero 👮‍♂️🚦 #shorts #hindi', 'description': 'The art of the U-turn. #traffic #roast #hindi'},
    {'path': 'savage_helpline_final.mp4', 'title': 'Customer Care Hold Music: Infinite Pain 📞🎶 #shorts', 'description': 'Your call is NOT important to them. #funny #roast #hindi'}
]

youtube = _get_authenticated_service()
for clip in CLIPS:
    print(f'Uploading: {clip["title"]}...')
    _upload_single(youtube, clip['path'], clip['title'], clip['description'], ['shorts', 'hindi', 'roast', 'trending'])
"""
    with open("temp_uploader.py", "w") as f:
        f.write(upload_script)
    
    subprocess.run(["python3", "temp_uploader.py"], check=True)
    print("\n--- ✅ ALL 5 NEW SHORTS ARE LIVE! ---")

if __name__ == "__main__":
    run()
