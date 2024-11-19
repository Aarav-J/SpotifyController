import os
import json
import threading
from flask import Flask, jsonify, redirect, request, abort
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import dotenv_values
import logging


config = dotenv_values(".env")
print("Loaded configuration:", config)

SPOTIFY_CLIENT_ID = config.get('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = config.get('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = 'http://localhost:5000/callback'

if not SPOTIFY_CLIENT_ID or not SPOTIFY_CLIENT_SECRET:
    raise Exception("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file.")

SCOPE = 'user-modify-playback-state user-read-playback-state'

FLASK_PORT = 5000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



app = Flask(__name__)


sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope=SCOPE,
    cache_path=".cache"
)

sp = None  # Will hold the Spotify client

def get_spotify_client():
    global sp
    token_info = sp_oauth.get_cached_token()
    if not token_info:
        auth_url = sp_oauth.get_authorize_url()
        logger.info("Please navigate here to authorize: %s", auth_url)
        # Open the browser for user authorization
        # import webbrowser
        # webbrowser.open(auth_url)
        return

    sp = Spotify(auth=token_info['access_token'])

    # Start a thread to refresh token periodically
    def refresh_token():
        global sp
        while True:
            try:
                token_info = sp_oauth.refresh_access_token(sp_oauth.get_cached_token()['refresh_token'])
                sp = Spotify(auth=token_info['access_token'])
                logger.info("Spotify access token refreshed.")
            except Exception as e:
                logger.error("Error refreshing token: %s", e)
            import time
            time.sleep(token_info['expires_in'] - 60)  # Refresh one minute before expiration

    thread = threading.Thread(target=refresh_token, daemon=True)
    thread.start()

@app.route('/callback')
def callback():
    global sp
    code = request.args.get('code')
    if not code:
        logger.error("No code parameter found in the callback request.")
        return jsonify({'error': 'No code provided'}), 400
    try:
        token_info = sp_oauth.get_access_token(code)
        sp = Spotify(auth=token_info['access_token'])
        logger.info("Authentication successful. Access token obtained.")
        return "Authentication successful! You can close this window.", 200
    except Exception as e:
        logger.error("Error during Spotify authentication: %s", e)
        return jsonify({'error': str(e)}), 400



@app.route('/')
def index():
    return jsonify({'message': 'Spotify Remote Control Server is running.'}), 200

@app.route('/play', methods=['GET'])
def play():
    try:
        sp.start_playback()
        logger.info("Playback started.")
        return jsonify({'status': 'Playback started'}), 200
    except Exception as e:
        logger.error("Error in /play: %s", e)
        return jsonify({'error': str(e)}), 400

@app.route('/pause', methods=['GET'])
def pause():
    try:
        sp.pause_playback()
        logger.info("Playback paused.")
        return jsonify({'status': 'Playback paused'}), 200
    except Exception as e:
        logger.error("Error in /pause: %s", e)
        return jsonify({'error': str(e)}), 400

@app.route('/next', methods=['GET'])
def next_track():
    try:
        sp.next_track()
        logger.info("Skipped to next track.")
        return jsonify({'status': 'Skipped to next track'}), 200
    except Exception as e:
        logger.error("Error in /next: %s", e)
        return jsonify({'error': str(e)}), 400

@app.route('/previous', methods=['GET'])
def previous_track():
    try:
        sp.previous_track()
        logger.info("Went back to previous track.")
        return jsonify({'status': 'Went back to previous track'}), 200
    except Exception as e:
        logger.error("Error in /previous: %s", e)
        return jsonify({'error': str(e)}), 400

@app.route('/volume/<int:volume>', methods=['GET'])
def set_volume(volume):
    try:
        if 0 <= volume <= 100:
            sp.volume(volume)
            logger.info("Volume set to %d.", volume)
            return jsonify({'status': f'Volume set to {volume}'}), 200
        else:
            logger.warning("Invalid volume level: %d", volume)
            return jsonify({'error': 'Volume must be between 0 and 100'}), 400
    except Exception as e:
        logger.error("Error in /volume: %s", e)
        return jsonify({'error': str(e)}), 400

# =======================
# Run Flask App
# =======================
if __name__ == '__main__':
    # Initialize Spotify client
    get_spotify_client()

    # Run Flask app
    app.run(host='0.0.0.0', port=FLASK_PORT)