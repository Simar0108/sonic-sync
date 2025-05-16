from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from typing import Dict, Any
import secrets
import json
from ..core.config import settings
from ..services.spotify import SpotifyService
from ..models.spotify import SpotifyToken, SpotifyUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login")
async def login():
    """Redirect to Spotify authorization page"""
    # Generate a random state value for CSRF protection
    state = secrets.token_urlsafe(16)
    auth_url = SpotifyService.get_auth_url(state)
    
    # Create a response that redirects to Spotify
    response = RedirectResponse(url=auth_url)
    return response

@router.get("/callback")
async def callback(code: str = None, state: str = None, error: str = None, request: Request = None):
    """Handle callback from Spotify OAuth"""
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify auth error: {error}")
    
    # Debug information
    print(f"Received state: {state}")
    
    # Verify state to prevent CSRF
    if not state:
        raise HTTPException(status_code=400, detail="No state parameter received")
    
    # Exchange code for access token
    token_data = SpotifyService.get_token(code)
    
    if "error" in token_data:
        raise HTTPException(
            status_code=400, 
            detail=f"Error getting access token: {token_data.get('error_description', token_data.get('error'))}"
        )
    
    # Get user profile
    user_data = SpotifyService.get_user_profile(token_data["access_token"])
    
    # Create response with user data
    response = RedirectResponse(url="/profile")
    
    # Store token and user data in cookies
    # In production, use a proper session management system
    response.set_cookie(
        key="spotify_token", 
        value=json.dumps(token_data),
        httponly=True,
        samesite="lax",
        max_age=3600,     # 1 hour
        path="/"          # Make sure cookie is available for all paths
    )
    
    response.set_cookie(
        key="spotify_user", 
        value=json.dumps(user_data),
        httponly=True,
        samesite="lax",
        max_age=3600,     # 1 hour
        path="/"          # Make sure cookie is available for all paths
    )
    
    return response

@router.get("/profile")
async def profile(request: Request):
    """Get the user's Spotify profile"""
    token_data = request.cookies.get("spotify_token")
    user_data = request.cookies.get("spotify_user")
    
    if not token_data or not user_data:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        token = SpotifyToken(**json.loads(token_data))
        user = SpotifyUser(**json.loads(user_data))
        
        return {
            "user": user,
            "token_expires_in": token.expires_in
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid data: {str(e)}")

@router.get("/logout")
async def logout():
    """Log out by clearing cookies"""
    response = RedirectResponse(url="/")
    
    # Clear cookies
    response.delete_cookie("spotify_token", path="/")
    response.delete_cookie("spotify_user", path="/")
    
    return response 