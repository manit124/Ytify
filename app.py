from datetime import datetime
from flask import Flask, redirect, jsonify, session, request, render_template
from dotenv import load_dotenv
import urllib.parse
import os
import requests
import logging
from bs4 import BeautifulSoup
import re


# Load environment variables
load_dotenv()

# Retrieve client ID, client secret, and YouTube API key from environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
SECRET_KEY = os.getenv('SECRET_KEY')



# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
REDIRECT_URI = "https://ytify-jvoc.onrender.com/callback"


# Spotify API URLs
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Routes
@app.route('/')
def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email'

    params = {
        'client_id': client_id,
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': REDIRECT_URI,
        'show_dialog': True
    }
    query_string = urllib.parse.urlencode(params)
    auth_url = f"{AUTH_URL}?{query_string}"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    if 'error' in request.args:
        return jsonify({"error": request.args['error']})

    if 'code' in request.args:
        req_body = {
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': REDIRECT_URI,
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        session['access_token'] = token_info.get('access_token')
        session['refresh_token'] = token_info.get('refresh_token')
        session['expires_at'] = datetime.now().timestamp() + token_info.get('expires_in', 0)

        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')

    if 'expires_at' in session and datetime.now().timestamp() > session['expires_at']:
        return redirect('/refresh-token')

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + "me/playlists", headers=headers)
    playlists = response.json()

    if 'items' not in playlists:
        return jsonify({"error": "Unable to fetch playlists"}), 500

    # Extract playlist names and URLs
    simplified_playlists = [
        {"name": playlist["name"], "url": playlist["external_urls"]["spotify"], "id": playlist["id"]}
        for playlist in playlists["items"]
    ]

    return render_template('playlists.html', playlists=simplified_playlists)

@app.route('/refresh-token')
def refresh_token():
    if 'refresh_token' not in session:
        return redirect('/login')

    if 'expires_at' in session and datetime.now().timestamp() > session['expires_at']:
        req_body = {
            'grant_type': 'refresh_token',
            'refresh_token': session['refresh_token'],
            'client_id': client_id,
            'client_secret': client_secret
        }

        response = requests.post(TOKEN_URL, data=req_body)
        new_token_info = response.json()

        session['access_token'] = new_token_info.get('access_token')
        session['expires_at'] = datetime.now().timestamp() + new_token_info.get('expires_in', 0)

        return redirect('/playlists')

@app.route('/playlist/<playlist_id>/youtube-links', methods=['POST'])
def youtube_links(playlist_id):
    if 'access_token' not in session:
        return jsonify({"message": "Not logged in"}), 401

    headers = {
        'Authorization': f"Bearer {session['access_token']}"
    }
    response = requests.get(API_BASE_URL + f"playlists/{playlist_id}/tracks", headers=headers)
    tracks = response.json()

    if 'items' not in tracks:
        return jsonify({"error": "Unable to fetch playlist tracks"}), 500

    track_details = [{"track_name": track['track']['name'], "artist_name": track['track']['artists'][0]['name']} for track in tracks['items']]
    logging.debug(f"Track details extracted: {track_details}")

    # Function to search YouTube video links using BeautifulSoup
    def search_youtube_video(query):
        try:
            search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
            response = requests.get(search_url)
            if response.status_code == 200:
                video_id = re.search(r"watch\?v=(\S{11})", response.text).group(1)
                video_link = f"https://www.youtube.com/watch?v={video_id}"
                logging.debug(f"Found YouTube link for query '{query}': {video_link}")
                return video_link
        except Exception as e:
            logging.error(f"Error occurred while searching for YouTube video: {e}")
        return None

    # Extract YouTube links for each track
    youtube_links = []
    for track in track_details:
        search_query = f"{track['track_name']} {track['artist_name']}"
        youtube_link = search_youtube_video(search_query)
        if youtube_link:
            youtube_links.append({"track_name": track['track_name'], "artist_name": track['artist_name'], "youtube_link": youtube_link})
        else:
            logging.debug(f"No YouTube link found for track: {track}")

    logging.debug(f"YouTube links found: {youtube_links}")

    return render_template('youtube_links.html', youtube_links=youtube_links)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001)) 
    app.run(host='0.0.0.0', port=port)
