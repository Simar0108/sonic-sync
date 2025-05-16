#!/usr/bin/env python
import os
import secrets

def create_env_file():
    """Create a .env file with template values"""
    env_path = os.path.join(os.path.dirname(__file__), "app", ".env")
    
    if os.path.exists(env_path):
        overwrite = input(f".env file already exists at {env_path}. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("Aborted.")
            return
    
    # Generate a random secret key
    secret_key = secrets.token_hex(32)
    
    env_content = f"""# Spotify API Credentials
# Get these from https://developer.spotify.com/dashboard/applications
SPOTIFY_CLIENT_ID=04151aa3de4d444398ebc097b0da9cd5
SPOTIFY_CLIENT_SECRET=74b32eb5b4a042c68abdd1594dbb1fd7
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/callback

# App Secret Key (used for session encryption)
SECRET_KEY={secret_key}
"""
    
    try:
        os.makedirs(os.path.dirname(env_path), exist_ok=True)
        with open(env_path, 'w') as f:
            f.write(env_content)
        print(f"Created .env file at {env_path}")
        print("Please update it with your Spotify API credentials.")
    except Exception as e:
        print(f"Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 