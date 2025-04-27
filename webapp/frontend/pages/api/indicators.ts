import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { token } = req.query;
  
  // Validate token parameter
  if (!token || typeof token !== 'string') {
    console.error('Invalid or missing token parameter:', token);
    return res.status(400).json({ error: 'Missing or invalid token parameter' });
  }
  
  // Construct backend URL
  const backendUrl = (process.env.BACKEND_URL_INDICATORS || 'http://nc_webapp_backend:8000/api/indicators') + `?token=${encodeURIComponent(token)}`;
  console.log(`Indicators API: Fetching from ${backendUrl}`);
  
  try {
    // Fetch data from backend
    const response = await fetch(backendUrl);
    console.log(`Indicators API: Backend response status: ${response.status}`);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'No error details available');
      console.error(`Indicators API: Backend error: ${errorText}`);
      return res.status(response.status).json({ 
        error: 'Failed to fetch indicators from backend',
        status: response.status,
        details: errorText
      });
    }
    
    // Parse and return data
    const data = await response.json();
    console.log(`Indicators API: Successfully fetched data for token: ${token}`);
    res.status(200).json(data);
  } catch (error) {
    console.error('Indicators API: Error connecting to backend:', error);
    res.status(500).json({ 
      error: 'Error connecting to backend', 
      detail: error instanceof Error ? error.message : String(error)
    });
  }
}
