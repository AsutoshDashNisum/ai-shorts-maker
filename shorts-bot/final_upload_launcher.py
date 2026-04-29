import sys
import logging
from youtube_uploader import _get_authenticated_service, _upload_single

# Viral Savage Shorts Series
CLIPS = [
    {
        "path": "savage_papa_final.mp4",
        "title": "How to Handle Strict Papa 🧔‍♂️🔥 #shorts #hindi #roast",
        "description": "Savage hacks for strict Indian dads. #shorts #hindi #roast #satisfying"
    },
    {
        "path": "savage_rishtedar_final.mp4",
        "title": "Bhagao Toxic Rishtedar like a Pro! 🏠🚪 #shorts #hindi",
        "description": "Dealing with nosy relatives in savage style. #shorts #hindi #roast #satisfying"
    },
    {
        "path": "savage_ex_final.mp4",
        "title": "Dealing with Ex-Girlfriend: Revenge Roast 💔🗿 #shorts",
        "description": "The ultimate guide to move on savgelly. #shorts #hindi #roast #satisfying"
    },
    {
        "path": "savage_sibling_final.mp4",
        "title": "Ziddi Sibling: System Hang! 🎮👦 #shorts #hindi",
        "description": "Handling younger siblings with logic. #shorts #hindi #roast #satisfying"
    },
    {
        "path": "savage_exam_final.mp4",
        "title": "Exam Hall Jugaad for Nalayaks 📝🎓 #shorts #hindi",
        "description": "How to pass exams with zero preparation. #shorts #hindi #roast #satisfying"
    }
]

def launch():
    print("--- 🚀 FINAL LAUNCH: Sending Savage 5 to YouTube! ---")
    try:
        youtube = _get_authenticated_service()
    except Exception as e:
        print(f"Auth Error: {e}")
        return

    for clip in CLIPS:
        print(f"Uploading: {clip['title']}...")
        try:
            _upload_single(
                youtube, 
                clip['path'], 
                clip['title'], 
                clip['description'], 
                ["shorts", "hindi", "roast", "savage", "AI"]
            )
            print(f"[OK] Successfully uploaded {clip['path']}")
        except Exception as e:
            print(f"[ERROR] Failed to upload {clip['path']}: {e}")

    print("\n--- ✅ ALL UPLOADS COMPLETE! Check your channel! ---")

if __name__ == "__main__":
    launch()
