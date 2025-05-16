from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class SpotifyToken(BaseModel):
    access_token: str
    token_type: str
    scope: str
    expires_in: int
    refresh_token: str

class SpotifyUser(BaseModel):
    id: str
    display_name: Optional[str]
    email: Optional[str]
    images: Optional[List[Dict[str, Any]]]
    
    @property
    def profile_image(self) -> Optional[str]:
        if self.images and len(self.images) > 0:
            return self.images[0].get("url")
        return None

class AudioFeatures(BaseModel):
    id: str
    danceability: float
    energy: float
    key: int
    loudness: float
    mode: int
    speechiness: float
    acousticness: float
    instrumentalness: float
    liveness: float
    valence: float
    tempo: float
    duration_ms: int
    time_signature: int

class Track(BaseModel):
    id: str
    name: str
    artists: List[Dict[str, Any]]
    album: Dict[str, Any]
    popularity: int
    audio_features: Optional[AudioFeatures] = None
    
    @property
    def artist_names(self) -> str:
        return ", ".join([artist["name"] for artist in self.artists])
    
    @property
    def album_name(self) -> str:
        return self.album.get("name", "")
    
    @property
    def album_image(self) -> Optional[str]:
        images = self.album.get("images", [])
        if images and len(images) > 0:
            return images[0].get("url")
        return None

class MoodProfile(BaseModel):
    morning: Dict[str, float]
    afternoon: Dict[str, float]
    night: Dict[str, float]
    
    class Config:
        schema_extra = {
            "example": {
                "morning": {
                    "valence": 0.65,
                    "energy": 0.72,
                    "danceability": 0.58,
                    "tempo": 110.5
                },
                "afternoon": {
                    "valence": 0.72,
                    "energy": 0.85,
                    "danceability": 0.67,
                    "tempo": 125.3
                },
                "night": {
                    "valence": 0.45,
                    "energy": 0.35,
                    "danceability": 0.42,
                    "tempo": 95.2
                }
            }
        } 