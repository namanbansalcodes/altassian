import ky from 'ky';

export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export const api = ky.create({
  prefixUrl: API_BASE,
  credentials: 'include',
  hooks: {
    beforeRequest: [async (req) => {
      const token = (await import('../auth/store')).getAccessToken();
      if (token) req.headers.set('Authorization', `Bearer ${token}`);
    }],
    afterResponse: [async (_req, _opts, res) => {
      if (res.status === 401) {
        const { refreshIfNeeded } = await import('../auth/store');
        const ok = await refreshIfNeeded();
        if (ok) throw new Error('RETRY');
      }
    }]
  }
});
