import requests
import time
import os
from logger import log
import config

class InstagramUploader:
    def __init__(self):
        self.access_token = config.INSTAGRAM_ACCESS_TOKEN
        self.ig_user_id = config.INSTAGRAM_BUSINESS_ACCOUNT_ID
        self.base_url = "https://graph.facebook.com/v25.0"

    def upload_reel(self, video_url, caption):
        """
        Full flow to upload a reel.
        1. Create media container
        2. Wait for it to process
        3. Publish container
        """
        log.info(f"Step 1: Creating Instagram Media Container for {video_url}...")
        
        container_id = self._create_container(video_url, caption)
        if not container_id:
            return None

        log.info(f"Step 2: Waiting for container {container_id} to be ready...")
        if not self._wait_for_container(container_id):
            log.error("Container processing timed out or failed.")
            return None

        log.info(f"Step 3: Publishing Reel...")
        media_id = self._publish_container(container_id)
        
        if media_id:
            log.info(f"SUCCESS! Reel published. Media ID: {media_id}")
            return media_id
        else:
            log.error("Failed to publish Reel.")
            return None

    def _create_container(self, video_url, caption):
        url = f"{self.base_url}/{self.ig_user_id}/media"
        params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "access_token": self.access_token
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        if "id" in data:
            return data["id"]
        else:
            log.error(f"Error creating container: {data}")
            return None

    def _wait_for_container(self, container_id, timeout_mins=5):
        url = f"{self.base_url}/{container_id}"
        params = {
            "fields": "status_code,status",
            "access_token": self.access_token
        }
        
        start_time = time.time()
        while time.time() - start_time < timeout_mins * 60:
            response = requests.get(url, params=params)
            data = response.json()
            
            status = data.get("status_code")
            if status == "FINISHED":
                return True
            elif status == "ERROR":
                log.error(f"Container processing error: {data}")
                return False
            
            log.info(f"Still processing... (Status: {status})")
            time.sleep(10) # Poll every 10 seconds
            
        return False

    def _publish_container(self, container_id):
        url = f"{self.base_url}/{self.ig_user_id}/media_publish"
        params = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        
        response = requests.post(url, params=params)
        data = response.json()
        
        if "id" in data:
            return data["id"]
        else:
            log.error(f"Error publishing container: {data}")
            return None

def upload_to_instagram(video_url, caption):
    uploader = InstagramUploader()
    return uploader.upload_reel(video_url, caption)
