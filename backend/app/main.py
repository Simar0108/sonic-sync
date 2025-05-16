from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from .core.config import settings
from .api import auth, tracks

app = FastAPI(title=settings.APP_NAME)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(tracks.router, prefix=settings.API_V1_STR)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with login link"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sonic Sync</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: linear-gradient(135deg, #1DB954, #191414);
                color: white;
                height: 100vh;
                margin: 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
            }
            p {
                font-size: 1.2rem;
                margin-bottom: 2rem;
                max-width: 600px;
            }
            .login-button {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 15px 30px;
                font-size: 1.1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
            }
            .login-button:hover {
                background-color: #1ed760;
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <h1>🎧 Sonic Sync</h1>
        <p>Discover your music mood profile and find your Sonic Twin based on your Spotify listening habits.</p>
        <a href="/api/v1/auth/login" class="login-button">Login with Spotify</a>
    </body>
    </html>
    """
    return html_content

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """Profile page after successful login"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sonic Sync - Profile</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background: linear-gradient(135deg, #1DB954, #191414);
                color: white;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }
            h1 {
                font-size: 2.5rem;
                margin: 0;
            }
            .profile {
                display: flex;
                align-items: center;
                margin-bottom: 30px;
            }
            .profile-image {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                margin-right: 20px;
                object-fit: cover;
            }
            .user-info {
                flex: 1;
            }
            .button {
                background-color: #1DB954;
                color: white;
                border: none;
                border-radius: 30px;
                padding: 10px 20px;
                font-size: 1rem;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            .button:hover {
                background-color: #1ed760;
            }
            .button.secondary {
                background-color: transparent;
                border: 1px solid white;
            }
            .button.secondary:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            .section {
                margin-bottom: 30px;
            }
            #loading {
                text-align: center;
                padding: 50px;
            }
            #error {
                background-color: rgba(255, 0, 0, 0.1);
                border-left: 4px solid red;
                padding: 10px 20px;
                margin: 20px 0;
                display: none;
            }
            #top-tracks {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
            }
            .track-card {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                overflow: hidden;
                transition: transform 0.3s ease;
            }
            .track-card:hover {
                transform: translateY(-5px);
            }
            .track-image {
                width: 100%;
                aspect-ratio: 1;
                object-fit: cover;
            }
            .track-info {
                padding: 15px;
            }
            .track-name {
                font-weight: bold;
                margin: 0 0 5px 0;
            }
            .track-artist {
                font-size: 0.9rem;
                opacity: 0.8;
                margin: 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🎧 Sonic Sync</h1>
                <a href="/api/v1/auth/logout" class="button secondary">Logout</a>
            </header>
            
            <div id="loading">Loading your profile...</div>
            <div id="error"></div>
            
            <div id="content" style="display: none;">
                <div class="profile">
                    <img id="profile-image" class="profile-image" src="" alt="Profile Picture">
                    <div class="user-info">
                        <h2 id="display-name"></h2>
                        <p id="user-id"></p>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Your Top Tracks</h2>
                    <div id="top-tracks"></div>
                </div>
                
                <div class="section">
                    <h2>Generate Your Mood Profile</h2>
                    <p>Analyze your listening habits to create your personal mood map.</p>
                    <button id="generate-profile" class="button">Generate Mood Profile</button>
                </div>
            </div>
        </div>
        
        <script>
            // Fetch user profile
            async function fetchProfile() {
                try {
                    const response = await fetch('/api/v1/auth/profile');
                    if (!response.ok) {
                        throw new Error('Not authenticated');
                    }
                    const data = await response.json();
                    
                    // Display user info
                    document.getElementById('display-name').textContent = data.user.display_name || 'Spotify User';
                    document.getElementById('user-id').textContent = `ID: ${data.user.id}`;
                    
                    if (data.user.images && data.user.images.length > 0) {
                        document.getElementById('profile-image').src = data.user.images[0].url;
                    } else {
                        document.getElementById('profile-image').src = 'https://via.placeholder.com/100';
                    }
                    
                    // Fetch top tracks
                    fetchTopTracks();
                    
                    // Show content
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('content').style.display = 'block';
                } catch (error) {
                    showError(error.message);
                }
            }
            
            // Fetch top tracks
            async function fetchTopTracks() {
                try {
                    const response = await fetch('/api/v1/tracks/top?limit=10');
                    if (!response.ok) {
                        throw new Error('Failed to fetch top tracks');
                    }
                    const tracks = await response.json();
                    
                    const tracksContainer = document.getElementById('top-tracks');
                    tracksContainer.innerHTML = '';
                    
                    tracks.forEach(track => {
                        const trackCard = document.createElement('div');
                        trackCard.className = 'track-card';
                        
                        let albumImage = 'https://via.placeholder.com/200';
                        if (track.album && track.album.images && track.album.images.length > 0) {
                            albumImage = track.album.images[0].url;
                        }
                        
                        trackCard.innerHTML = `
                            <img class="track-image" src="${albumImage}" alt="${track.name}">
                            <div class="track-info">
                                <p class="track-name">${track.name}</p>
                                <p class="track-artist">${track.artists.map(a => a.name).join(', ')}</p>
                            </div>
                        `;
                        
                        tracksContainer.appendChild(trackCard);
                    });
                } catch (error) {
                    showError(error.message);
                }
            }
            
            // Show error message
            function showError(message) {
                const errorElement = document.getElementById('error');
                errorElement.textContent = `Error: ${message}`;
                errorElement.style.display = 'block';
                document.getElementById('loading').style.display = 'none';
            }
            
            // Initialize
            document.addEventListener('DOMContentLoaded', fetchProfile);
            
            // Generate profile button (placeholder for now)
            document.getElementById('generate-profile').addEventListener('click', function() {
                alert('This feature will be implemented in the next version!');
            });
        </script>
    </body>
    </html>
    """
    return html_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 