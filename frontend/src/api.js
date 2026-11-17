import axios from 'axios';

/**
 * Centralized API client supporting both:
 * 1. Distributed deployment (Vercel Frontend -> Render Backend via VITE_API_BASE_URL)
 * 2. Local/Unified single-origin deployment (relative paths fallback)
 */
const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default api;
export { API_BASE_URL };
