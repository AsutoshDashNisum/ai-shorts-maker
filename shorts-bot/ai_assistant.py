import requests
import json
from logger import log

class AIAssistant:
    def __init__(self, model="llama3:8b", base_url="http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate_viral_metadata(self, transcript, original_title):
        """
        Takes a video transcript and generates viral title, description, and tags.
        """
        log.info(f"🤖 AI is analyzing transcript for '{original_title}'...")
        
        prompt = f"""
        Analyze this transcript from an animation video titled "{original_title}" (in Hindi/Hinglish).
        Generate a set of viral metadata for a YouTube Short/Instagram Reel.
        Use "Hinglish" (Hindi written in English script + English) for the description to make it relatable to the Indian youth.
        Make the title catchy and the description funny.
        
        Transcript:
        {transcript}
        
        Return ONLY a JSON object with these exact keys:
        - title: (Catchy viral title)
        - description: (Funny Hinglish description with emojis)
        - tags: (List of 10 trending hashtags without #)
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=1800)
            response.raise_for_status()
            result = response.json()
            
            # Parse the JSON response from the LLM
            metadata = json.loads(result["response"])
            log.info("✅ AI successfully generated viral metadata!")
            return metadata
        except Exception as e:
            log.error(f"❌ AI Assistant (Metadata) failed: {e}")
            return {
                "title": original_title,
                "description": "Dosto, dekho ye naya video! 😂🔥 #Shorts #Comedy #India",
                "tags": ["Shorts", "Comedy", "Funny", "India"]
            }

    def find_viral_hooks(self, transcript, max_clips=5):
        """
        Asks Llama-3 to find the 5 most funny/dramatic/viral moments with timestamps.
        """
        log.info(f"🧠 AI is hunting for {max_clips} viral hooks in the transcript...")
        
        prompt = f"""
        Analyze this transcript from a Doraemon episode in Hindi. 
        Identify the {max_clips} most viral, funny, or dramatic moments (hooks) that would make great 60-second YouTube Shorts.
        Look for gadget reveals, funny Nobita reactions, or Suneo's bullying.

        Transcript:
        {transcript}

        Return ONLY a JSON object with a key 'hooks' which is a list of objects.
        Each hook object MUST have:
        - start_time: The starting timestamp in seconds (integer).
        - duration: (The length of the clip in seconds - max 59s).
        - hook_title: (A viral catchy title for this specific moment).
        - reason: (A short reason why this moment is a good hook).
        """
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        
        try:
            response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=1800)
            response.raise_for_status()
            result = response.json()
            
            # Parse the JSON response from the LLM
            data = json.loads(result["response"])
            log.info(f"🎯 AI found {len(data.get('hooks', []))} viral hooks!")
            return data.get("hooks", [])
        except Exception as e:
            log.error(f"❌ AI Assistant (Hook Finder) failed: {e}")
            return []

# Singleton instance
ai = AIAssistant()
