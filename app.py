from datetime import datetime
from flask import Flask, redirect, jsonify, session, request, render_template
from dotenv import load_dotenv
import urllib.parse
import os
import requests
import logging
from bs4 import BeautifulSoup
import re
from flask_sqlalchemy import SQLAlchemy

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spotify_tokens.db'
db = SQLAlchemy(app)

# Spotify API URLs
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'
API_BASE_URL = 'https://api.spotify.com/v1/'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Database model for storing user tokens
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spotify_id = db.Column(db.String(255), unique=True, nullable=False)
    access_token = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.String(255), nullable=False)

# Routes
@app.route('/')
def index():
    return "Welcome to my Spotify App <a href='/login'>Login with Spotify</a>"

@app.route('/login')
def login():
    scope = 'user-read-private user-read-email playlist-read-private playlist-read-collaborative'

    params = {
        'client_id': os.getenv("CLIENT_ID"),
        'response_type': 'code',
        'scope': scope,
        'redirect_uri': os.getenv("REDIRECT_URI"),
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
            'redirect_uri': os.getenv("REDIRECT_URI"),
            'client_id': os.getenv("CLIENT_ID"),
            'client_secret': os.getenv("CLIENT_SECRET")
        }

        response = requests.post(TOKEN_URL, data=req_body)
        token_info = response.json()

        store_user_tokens(token_info['access_token'], token_info['refresh_token'])

        return redirect('/playlists')

@app.route('/playlists')
def get_playlists():
    if 'access_token' not in session:
        return redirect('/login')

    user = User.query.filter_by(spotify_id=session['spotify_id']).first()
    if not user:
        return redirect('/login')

    headers = {
        'Authorization': f"Bearer {user.access_token}"
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

def store_user_tokens(access_token, refresh_token):
    user = User(spotify_id=session['spotify_id'], access_token=access_token, refresh_token=refresh_token)
    db.session.add(user)
    db.session.commit()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
