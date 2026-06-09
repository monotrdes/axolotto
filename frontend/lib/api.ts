export const API_BASE = process.env.NEXT_PUBLIC_API_URL || (
  typeof window !== 'undefined' && (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://localhost:8001/api/v1'
    : 'https://api.axolot.to/api/v1'
);
