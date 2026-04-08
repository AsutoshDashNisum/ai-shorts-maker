"""
server.py — Simple local HTTP server for Instagram Reels.

Use this with ngrok (ngrok http 8000) to give Instagram a 
public URL to fetch your local clips for free.
"""

import http.server
import socketserver
import os
from logger import log
import config

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from the output clips directory
        super().__init__(*args, directory=os.path.join(config.OUTPUT_DIR, "clips"), **kwargs)

def start_server():
    log.info("Starting local server on port %d...", PORT)
    log.info("Serving files from: %s", os.path.join(config.OUTPUT_DIR, "clips"))
    log.info("TIP: Run 'ngrok http %d' to make this public for Instagram.", PORT)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            log.info("Server stopped.")

if __name__ == "__main__":
    start_server()
