import time
import requests
from instagram_uploader import upload_to_instagram

# Viral captions + hashtags for each remaining clip (07-22)
REELS = [
    {
        "path": "output/satisfying_clips/satisfying_clip_07.mp4",
        "caption": "Satisfying moments that fix your brain 🧠✨ Part 7\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #mindblowing"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_08.mp4",
        "caption": "You won't believe how satisfying this is 😮‍💨🔥 Part 8\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #oddlysatisfying"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_09.mp4",
        "caption": "This clip will give you instant peace ☮️✨ Part 9\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #calmdown"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_10.mp4",
        "caption": "Stop scrolling and watch this 👀🔥 Part 10\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #mindblowing"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_11.mp4",
        "caption": "This will instantly calm your anxiety 😌💆 Part 11\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #anxiety"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_12.mp4",
        "caption": "The most satisfying thing you'll see today 🤩✨ Part 12\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #dopamine"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_13.mp4",
        "caption": "Watch till the end, you'll thank me later 😏🔥 Part 13\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #mustwatch"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_14.mp4",
        "caption": "This gives me chills every single time 🥶✨ Part 14\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #chills"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_15.mp4",
        "caption": "Why is this so satisfying?? 🤯😌 Part 15\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #oddlysatisfying"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_16.mp4",
        "caption": "Tag someone who needs this right now 🙏✨ Part 16\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #tagafriend"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_17.mp4",
        "caption": "Your daily dose of satisfaction 💊🔥 Part 17\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #dailydose"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_18.mp4",
        "caption": "POV: You finally found peace 🕊️✨ Part 18\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #pov"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_19.mp4",
        "caption": "This is what perfection looks like 💯🔥 Part 19\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #perfection"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_20.mp4",
        "caption": "I could watch this 1000 times 🔁✨ Part 20\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #onrepeat"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_21.mp4",
        "caption": "Your brain needed this today 🧠💆‍♂️ Part 21\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #brainrot"
    },
    {
        "path": "output/satisfying_clips/satisfying_clip_22.mp4",
        "caption": "Saving this forever 🔖✨ Part 22 | Follow for more satisfying content!\n\n#satisfying #asmr #relaxing #viral #trending #reels #india #shorts #satisfyingvideo #follow"
    },
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
    print("--- 🚀 INSTAGRAM LAUNCH: Uploading Clips 07-22 ---")
    success = 0
    failed = []

    for i, reel in enumerate(REELS, start=7):
        print(f"\n[{i}/22] Processing: {reel['path']}...")
        try:
            # Step 1: Upload to public CDN
            public_url = upload_to_cdn(reel['path'])

            # Step 2: Push to Instagram
            upload_to_instagram(public_url, reel['caption'])
            print(f"[OK] Clip {i} Posted to Instagram!")
            success += 1
            time.sleep(8)  # Avoid rate limiting
        except Exception as e:
            print(f"[ERROR] Clip {i} failed: {e}")
            failed.append(i)
            time.sleep(10)

    print(f"\n--- ✅ DONE! {success}/16 Reels Published Successfully! ---")
    if failed:
        print(f"Failed clips: {failed}")

if __name__ == "__main__":
    launch()
