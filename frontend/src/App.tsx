import React, { useState, useEffect } from 'react';
import { Container, Typography, Box, Button, CircularProgress } from '@mui/material';
import TopTracks from './components/TopTracks';
import TimeAnalysis from './components/TimeAnalysis';

function App() {
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/auth/check', {
          credentials: 'include'
        });
        
        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access_token);
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  const handleLogin = () => {
    window.location.href = 'http://127.0.0.1:8000/api/v1/auth/login';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!accessToken) {
    return (
      <Container maxWidth="sm">
        <Box sx={{ mt: 8, textAlign: 'center' }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Sonic Sync
          </Typography>
          <Typography variant="h5" component="h2" gutterBottom>
            Your Mood-Based Music Companion
          </Typography>
          <Button
            variant="contained"
            color="primary"
            size="large"
            onClick={handleLogin}
            sx={{ mt: 4 }}
          >
            Connect with Spotify
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container>
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Welcome to Sonic Sync
        </Typography>
        
        <TimeAnalysis accessToken={accessToken} />
        
        <Box sx={{ mt: 4 }}>
          <Typography variant="h4" gutterBottom>
            Your Top Tracks
          </Typography>
          <TopTracks accessToken={accessToken} />
        </Box>
      </Box>
    </Container>
  );
}

export default App; 