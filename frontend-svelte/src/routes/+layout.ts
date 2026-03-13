import type { LayoutLoad } from './$types';
import { initFromStorage } from '$lib/auth/store';

export const load: LayoutLoad = async () => {
  initFromStorage();
  return {};
};
