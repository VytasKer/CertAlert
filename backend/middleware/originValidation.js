const allowedOrigins = [
  process.env.FRONTEND_BASE_URL, // http://localhost:5173 (dev) or your production URL
  'http://localhost:3000',
  'http://localhost:5173',
];

const originValidation = (req, res, next) => {
  if (process.env.NODE_ENV !== 'production') {
    return next(); // Skip in development
  }

  const origin = req.headers.origin;
  const referer = req.headers.referer;

  if (origin && allowedOrigins.includes(origin)) {
    return next();
  }
  
  if (referer && allowedOrigins.some(allowed => referer.startsWith(allowed))) {
    return next();
  }

  res.status(403).json({ error: 'Access denied' });
};

module.exports = originValidation;
