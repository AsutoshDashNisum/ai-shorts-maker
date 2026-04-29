import sys
import time
import subprocess
import requests
from instagram_uploader import upload_to_instagram

REELS = [
    {'path': 'savage_papa_final.mp4', 'caption': 'How to Handle Strict Papa 🧔‍♂️🔥 #shorts #roast #hindi #satisfying'},
    {'path': 'savage_rishtedar_final.mp4', 'caption': 'Bhagao Toxic Rishtedar like a Pro! 🏠🚪 #shorts #hindi #savage'},
    {'path': 'savage_ex_final.mp4', 'caption': 'Dealing with Ex-Girlfriend: Revenge Roast 💔🗿 #shorts #roast'},
    {'path': 'savage_sibling_final.mp4', 'caption': 'Ziddi Sibling: System Hang! 🎮👦 #shorts #hindi #sibling'},
    {'path': 'savage_exam_final.mp4', 'caption': 'Exam Hall Jugaad for Nalayaks 📝🎓 #shorts #exam #hindi'},
    {'path': 'savage_gym_final.mp4', 'caption': 'Gym Freaks: Stop the Show-off! 🏋️‍♂️💪 #shorts #gym #roast'},
    {'path': 'savage_boss_final.mp4', 'caption': 'Meetings from Hell: The Boring Boss 💼💤 #shorts #office'},
    {'path': 'savage_wedding_final.mp4', 'caption': 'Wedding Buffet Monsters! 🍗🍛 #shorts #desi #shaadi'},
    {'path': 'savage_police_final.mp4', 'caption': 'Traffic Mama vs Helmet-less Hero 👮‍♂️🚦 #shorts #mumbai'},
    {'path': 'savage_helpline_final.mp4', 'caption': 'Customer Care Hold Music: Infinite Pain 📞🎶 #shorts'}
]

def upload_to_cdn(filepath):
    """Upload video to catbox.moe (72h temp hosting) and return public URL."""
    print(f"  Hosting {filepath} publicly via catbox.moe...")
    with open(filepath, 'rb') as f:
        response = requests.post(
            'https://litterbox.catbox.moe/resources/internals/api.php',
            data={'reqtype': 'fileupload', 'time': '72h'},
            files={'fileToUpload': f}
        )
    if response.status_code == 200 and response.text.startswith('https://'):
        url = response.text.strip()
        print(f"  Public URL: {url}")
        return url
    else:
        raise Exception(f"CDN Upload Failed: {response.text}")

def launch():
    print("--- 🚀 INSTAGRAM IG LAUNCH: Pushing 10 Reels! ---")
    for reel in REELS:
        print(f"\nProcessing: {reel['caption'][:40]}...")
        try:
            # Step 1: Upload file to public CDN
            public_url = upload_to_cdn(reel['path'])
            
            # Step 2: Push to Instagram using public URL
            upload_to_instagram(public_url, reel['caption'])
            print(f"[OK] Reel Posted Successfully!")
            
            # Sleep to avoid rate limiting
            time.sleep(8)
        except Exception as e:
            print(f"[ERROR] Failed for {reel['path']}: {e}")
            time.sleep(10)

    print("\n--- ✅ ALL INSTAGRAM UPLOADS COMPLETE! Check your @the_anitadka feed! ---")

if __name__ == "__main__":
    launch()
