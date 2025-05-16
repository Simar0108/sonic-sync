from fastapi import APIRouter, Depends, HTTPException, Request, Cookie, Response
import json
from typing import List, Dict, Any, Optional
from ..services.spotify import SpotifyService
from ..models.spotify import Track, AudioFeatures
from ..core.auth import get_current_user

router = APIRouter(prefix="/tracks", tags=["tracks"])

async def get_access_token(request: Request) -> str:
    """Get the access token from cookies"""
    token_data = request.cookies.get("spotify_token")
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = json.loads(token_data)
        return token["access_token"]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token data: {str(e)}")

@router.get("/top")
async def get_top_tracks(
    time_range: str = "medium_term",
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's top tracks"""
    try:
        tracks = SpotifyService.get_top_tracks(
            current_user["access_token"],
            time_range=time_range,
            limit=limit
        )
        return {"tracks": tracks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-features")
async def get_audio_features(
    request: Request,
    track_ids: str,
    access_token: str = Depends(get_access_token)
):
    """Get audio features for tracks
    
    Args:
        track_ids: Comma-separated list of Spotify track IDs
    """
    if not track_ids:
        raise HTTPException(status_code=400, detail="No track IDs provided")
    
    track_id_list = track_ids.split(",")
    audio_features = SpotifyService.get_audio_features(access_token, track_id_list)
    
    return audio_features

@router.get("/top-with-features")
async def get_top_tracks_with_features(
    request: Request,
    time_range: str = "medium_term",
    limit: int = 50,
    access_token: str = Depends(get_access_token)
):
    """Get the user's top tracks with audio features"""
    if time_range not in ["short_term", "medium_term", "long_term"]:
        raise HTTPException(status_code=400, detail="Invalid time_range. Must be one of: short_term, medium_term, long_term")
    
    if limit < 1 or limit > 50:
        raise HTTPException(status_code=400, detail="Invalid limit. Must be between 1 and 50")
    
    # Get top tracks
    tracks = SpotifyService.get_top_tracks(access_token, time_range, limit)
    
    if not tracks:
        return []
    
    # Get audio features for all tracks
    track_ids = [track["id"] for track in tracks]
    audio_features = SpotifyService.get_audio_features(access_token, track_ids)
    
    # Create a mapping of track ID to audio features
    features_map = {feature["id"]: feature for feature in audio_features if feature}
    
    # Combine track data with audio features
    result = []
    for track in tracks:
        track_id = track["id"]
        if track_id in features_map:
            track_with_features = Track(
                **track,
                audio_features=AudioFeatures(**features_map[track_id])
            )
            result.append(track_with_features)
        else:
            # Include track even if audio features are not available
            track_with_features = Track(**track)
            result.append(track_with_features)
    
    return result

@router.get("/time-analysis")
async def get_time_analysis(
    days: int = 7,
    current_user: Dict = Depends(get_current_user)
):
    """Get time-based analysis of listening habits"""
    try:
        # Get tracks organized by time
        time_tracks = SpotifyService.get_time_based_tracks(
            current_user["access_token"],
            days=days
        )
        
        # Analyze each time segment
        analysis = {}
        for segment, tracks in time_tracks.items():
            if tracks:
                features = SpotifyService.analyze_time_segment(
                    current_user["access_token"],
                    tracks
                )
                analysis[segment] = {
                    "track_count": len(tracks),
                    "features": features,
                    "tracks": tracks[:5]  # Include top 5 tracks for each segment
                }
        
        return {
            "time_analysis": analysis,
            "time_segments": SpotifyService.TIME_SEGMENTS
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent")
async def get_recent_tracks(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """Get user's recently played tracks"""
    try:
        tracks = SpotifyService.get_recently_played(
            current_user["access_token"],
            limit=limit
        )
        return {"tracks": tracks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 