import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ cookies }) => {
  // Expose API base to client
  return {
    apiBase: process.env.PUBLIC_API_BASE || process.env.VITE_API_BASE || '/api'
  };
};