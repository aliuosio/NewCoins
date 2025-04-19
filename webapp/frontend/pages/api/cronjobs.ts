import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    // Use the backend service name for Docker networking
    const backendUrl = process.env.BACKEND_URL || 'http://webapp-backend:8000/api/cronjobs';
    const response = await fetch(backendUrl);
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Backend error' });
    }
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Proxy error', details: String(error) });
  }
}
