import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { token } = req.query;
  
  // Validate token parameter
  if (!token || typeof token !== 'string') {
    return res.status(400).json({ error: 'Missing or invalid token parameter' });
  }
  
  // Construct backend URL
  const backendUrl = (process.env.BACKEND_URL_INDICATORS || 'http://nc_webapp_backend:8000/api/indicators') + `?token=${encodeURIComponent(token)}`;
  
  try {
    // Fetch data from backend
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      const errorText = await response.text().catch(() => 'No error details available');
      return res.status(response.status).json({ 
        error: 'Failed to fetch indicators from backend',
        status: response.status,
        details: errorText
      });
    }
    
    // Parse and return data
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ 
      error: 'Error connecting to backend', 
      detail: error instanceof Error ? error.message : String(error)
    });
  }
}
