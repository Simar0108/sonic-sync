import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, Box, CircularProgress } from '@mui/material';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface TimeAnalysisProps {
  accessToken: string;
}

interface TimeSegment {
  track_count: number;
  features: {
    valence: number;
    energy: number;
    danceability: number;
    tempo: number;
    instrumentalness: number;
    acousticness: number;
    speechiness: number;
    liveness: number;
  };
  tracks: Array<{
    name: string;
    artists: Array<{ name: string }>;
  }>;
}

interface TimeAnalysis {
  time_analysis: {
    [key: string]: TimeSegment;
  };
  time_segments: {
    [key: string]: [number, number];
  };
}

const TimeAnalysis: React.FC<TimeAnalysisProps> = ({ accessToken }) => {
  const [analysis, setAnalysis] = useState<TimeAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/v1/tracks/time-analysis', {
          headers: {
            'Authorization': `Bearer ${accessToken}`
          }
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch time analysis');
        }
        
        const data = await response.json();
        setAnalysis(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysis();
  }, [accessToken]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Typography color="error" align="center">
        {error}
      </Typography>
    );
  }

  if (!analysis) {
    return null;
  }

  // Prepare data for the chart
  const timeLabels = Object.keys(analysis.time_analysis);
  const featureData = {
    valence: timeLabels.map(label => analysis.time_analysis[label]?.features.valence || 0),
    energy: timeLabels.map(label => analysis.time_analysis[label]?.features.energy || 0),
    danceability: timeLabels.map(label => analysis.time_analysis[label]?.features.danceability || 0),
  };

  const chartData = {
    labels: timeLabels.map(label => label.replace('_', ' ').toUpperCase()),
    datasets: [
      {
        label: 'Valence',
        data: featureData.valence,
        borderColor: 'rgb(255, 99, 132)',
        tension: 0.1,
      },
      {
        label: 'Energy',
        data: featureData.energy,
        borderColor: 'rgb(54, 162, 235)',
        tension: 0.1,
      },
      {
        label: 'Danceability',
        data: featureData.danceability,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Listening Patterns Throughout the Day',
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
      },
    },
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Your Sonic Spectrum
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Line data={chartData} options={chartOptions} />
            </CardContent>
          </Card>
        </Grid>

        {Object.entries(analysis.time_analysis).map(([segment, data]) => (
          <Grid item xs={12} md={6} lg={3} key={segment}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {segment.replace('_', ' ').toUpperCase()}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Tracks: {data.track_count}
                </Typography>
                <Box mt={2}>
                  <Typography variant="subtitle2">Top Tracks:</Typography>
                  {data.tracks.map((track, index) => (
                    <Typography key={index} variant="body2">
                      {track.name} - {track.artists.map(a => a.name).join(', ')}
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default TimeAnalysis; 