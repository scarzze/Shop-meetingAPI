const express = require('express');
const axios = require('axios');
const app = express();
const port = 8000;

// Enable CORS for all routes
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Authorization');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }
  next();
});

// Special health check endpoint
app.get('/health', async (req, res) => {
  res.json({ status: 'healthy', service: 'simple-proxy' });
});

// Proxy all requests to the products API
app.all('/api/products*', async (req, res) => {
  const targetUrl = `http://localhost:5006/api/v1/products${req.url.replace('/api/products', '')}`;
  console.log(`Proxying request to: ${targetUrl}`);
  
  try {
    // Forward the request to the target service
    const response = await axios({
      method: req.method,
      url: targetUrl,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers,
        host: 'localhost:5006'
      },
      data: req.body,
      timeout: 30000 // Increase timeout to 30 seconds
    });
    
    // Send the response back to the client
    res.status(response.status).json(response.data);
  } catch (error) {
    console.error('Proxy error:', error.message);
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Proxy error', message: error.message });
    }
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Simple proxy server running at http://localhost:${port}`);
  console.log('Routes:');
  console.log('- /health - Health check endpoint');
  console.log('- /api/products* - Proxies to http://localhost:5006/api/v1/products*');
});
