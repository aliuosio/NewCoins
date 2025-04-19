import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { token } = req.query;
  const backendUrl = `http://pad_webapp_backend:8000/api/indicators?token=${encodeURIComponent(token as string)}`;
  try {
    const response = await fetch(backendUrl);
    if (!response.ok) {
      return res.status(response.status).json({ error: 'Failed to fetch indicators from backend' });
    }
    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Error connecting to backend', detail: error instanceof Error ? error.message : error });
  }
}
