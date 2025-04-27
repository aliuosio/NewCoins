

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const { symbol } = req.query;
  if (!symbol || typeof symbol !== 'string') {
    res.status(400).json({ error: 'Missing or invalid symbol' });
    return;
  }
  try {
    const backendRes = await fetch(`http://localhost:8000/api/coin/${symbol}`);
    if (!backendRes.ok) {
      res.status(backendRes.status).json({ error: 'Not found' });
      return;
    }
    const data = await backendRes.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Internal server error' });
  }
}
