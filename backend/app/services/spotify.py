import base64
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..core.config import settings

class SpotifyService:
    AUTH_URL = "https://accounts.spotify.com/authorize"
    TOKEN_URL = "https://accounts.spotify.com/api/token"
    API_BASE_URL = "https://api.spotify.com/v1"
    
    # Time segments for analysis
    TIME_SEGMENTS = {
        "early_morning": (5, 8),    # 5am - 8am
        "morning": (8, 11),         # 8am - 11am
        "midday": (11, 14),         # 11am - 2pm
        "afternoon": (14, 17),      # 2pm - 5pm
        "evening": (17, 20),        # 5pm - 8pm
        "late_evening": (20, 23),   # 8pm - 11pm
        "night": (23, 2),           # 11pm - 2am
        "late_night": (2, 5)        # 2am - 5am
    }
    
    @staticmethod
    def get_auth_url(state: str) -> str:
        """Generate the Spotify authorization URL"""
        scope = "user-top-read playlist-modify-private user-read-private user-read-email user-read-recently-played"
        
        params = {
            "client_id": settings.SPOTIFY_CLIENT_ID,
            "response_type": "code",
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
            "state": state,
            "scope": scope,
            "show_dialog": "true"
        }
        
        auth_url = SpotifyService.AUTH_URL
        query_params = "&".join([f"{key}={val}" for key, val in params.items()])
        return f"{auth_url}?{query_params}"
    
    @staticmethod
    def get_token(code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        auth_header = base64.b64encode(
            f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.SPOTIFY_REDIRECT_URI
        }
        
        response = requests.post(SpotifyService.TOKEN_URL, headers=headers, data=data)
        return response.json()
    
    @staticmethod
    def refresh_token(refresh_token: str) -> Dict[str, Any]:
        """Refresh an expired access token"""
        auth_header = base64.b64encode(
            f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(SpotifyService.TOKEN_URL, headers=headers, data=data)
        return response.json()
    
    @staticmethod
    def get_user_profile(access_token: str) -> Dict[str, Any]:
        """Get the user's Spotify profile"""
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{SpotifyService.API_BASE_URL}/me", headers=headers)
        return response.json()
    
    @staticmethod
    def get_top_tracks(access_token: str, time_range: str = "medium_term", limit: int = 50) -> List[Dict[str, Any]]:
        """Get the user's top tracks
        
        Args:
            access_token: Spotify access token
            time_range: short_term (4 weeks), medium_term (6 months), or long_term (years)
            limit: Number of tracks to return (max 50)
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"time_range": time_range, "limit": limit}
        
        response = requests.get(
            f"{SpotifyService.API_BASE_URL}/me/top/tracks", 
            headers=headers,
            params=params
        )
        
        return response.json().get("items", [])
    
    @staticmethod
    def get_audio_features(access_token: str, track_ids: List[str]) -> List[Dict[str, Any]]:
        """Get audio features for a list of tracks"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Spotify API allows up to 100 IDs per request
        # Split into chunks if necessary
        if len(track_ids) > 100:
            # Implementation for chunking would go here
            pass
        
        track_ids_str = ",".join(track_ids)
        response = requests.get(
            f"{SpotifyService.API_BASE_URL}/audio-features", 
            headers=headers,
            params={"ids": track_ids_str}
        )
        
        return response.json().get("audio_features", [])
    
    @staticmethod
    def get_recently_played(access_token: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get the user's recently played tracks
        
        Args:
            access_token: Spotify access token
            limit: Number of tracks to return (max 50)
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"limit": limit}
        
        response = requests.get(
            f"{SpotifyService.API_BASE_URL}/me/player/recently-played",
            headers=headers,
            params=params
        )
        
        return response.json().get("items", [])
    
    @staticmethod
    def get_time_based_tracks(access_token: str, days: int = 7) -> Dict[str, List[Dict[str, Any]]]:
        """Get tracks organized by time of day
        
        Args:
            access_token: Spotify access token
            days: Number of days of history to analyze
        """
        # Get recently played tracks
        recent_tracks = SpotifyService.get_recently_played(access_token, limit=50)
        
        # Initialize time segments
        time_segments = {segment: [] for segment in SpotifyService.TIME_SEGMENTS.keys()}
        
        # Process each track
        for item in recent_tracks:
            played_at = datetime.fromisoformat(item["played_at"].replace("Z", "+00:00"))
            hour = played_at.hour
            
            # Determine time segment
            for segment, (start, end) in SpotifyService.TIME_SEGMENTS.items():
                if start <= hour < end or (start > end and (hour >= start or hour < end)):
                    time_segments[segment].append(item["track"])
                    break
        
        return time_segments
    
    @staticmethod
    def analyze_time_segment(access_token: str, tracks: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze audio features for a time segment
        
        Args:
            access_token: Spotify access token
            tracks: List of tracks to analyze
        """
        if not tracks:
            return {}
        
        # Get track IDs
        track_ids = [track["id"] for track in tracks if track["id"]]
        
        # Get audio features
        features = SpotifyService.get_audio_features(access_token, track_ids)
        
        # Calculate averages for each feature
        feature_sums = {
            "valence": 0,
            "energy": 0,
            "danceability": 0,
            "tempo": 0,
            "instrumentalness": 0,
            "acousticness": 0,
            "speechiness": 0,
            "liveness": 0
        }
        
        for feature in features:
            for key in feature_sums.keys():
                if key in feature:
                    feature_sums[key] += feature[key]
        
        # Calculate averages
        count = len(features)
        if count > 0:
            return {key: value/count for key, value in feature_sums.items()}
        
        return {} 