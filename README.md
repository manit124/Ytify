# Spotify to YouTube Link Converter

This project allows users to log in with their Spotify account, fetch their playlists, and get YouTube links for the tracks in those playlists.

## Setup Instructions

### Prerequisites

- Python 3.7+
- Git

### Steps

1. **Clone the Repository**

    ```bash
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install Dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Setting Up Environment Variables**

    ### Step 1: Create a Spotify Developer Account

    1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications) and log in with your Spotify account.
    2. Click on "Create an App" and provide a name and description for your app.
    3. After creating the app, you will see your `CLIENT_ID` and `CLIENT_SECRET` on the app's dashboard.
    4. Set the redirect URI to `http://localhost:5000/callback` in the application settings.

    ### Step 2: Create a `.env` File

    1. In the root directory of the project, create a file named `.env`.
    2. Open the `.env` file and add the following lines, replacing the placeholders with your actual Spotify client ID, client secret, and a secret key for your Flask app:

        ```plaintext
        CLIENT_ID=your_spotify_client_id
        CLIENT_SECRET=your_spotify_client_secret
        SECRET_KEY=your_secret_key
        ```

5. **Run the Flask App**

    ```bash
    flask run
    ```

    By default, the app will run on `http://localhost:5000`.

6. **Access the Application**

    Open a web browser and go to `http://localhost:5000`. You should see a welcome message with a link to log in with Spotify.

## Usage

- Click on "Login with Spotify" to authorize the application.
- After logging in, you will be redirected to the playlists page where you can see your playlists.
- Click on a playlist to get YouTube links for the tracks in that playlist.

## Troubleshooting

If you encounter any issues, ensure that:

- Your environment variables are correctly set.
- Your Spotify Developer Dashboard has the correct redirect URI.
- You have a stable internet connection.

For further assistance, please open an issue on the GitHub repository.

---
