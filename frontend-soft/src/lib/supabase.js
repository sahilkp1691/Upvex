import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

/** Null when Supabase env vars are absent — the app then runs in dev-bypass mode
 * (backend DEV_AUTH_BYPASS=true) with no real authentication. */
export const supabase = url && anonKey ? createClient(url, anonKey) : null;

export const authEnabled = supabase !== null;

/** Where Supabase sends users after they click a confirmation or recovery link. */
export function getAuthRedirectUrl() {
	if (typeof window === 'undefined') return '';
	return `${window.location.origin}/auth`;
}
