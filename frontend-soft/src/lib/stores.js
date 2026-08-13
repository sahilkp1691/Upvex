import { writable, get } from 'svelte/store';
import { browser } from '$app/environment';

/** Current backend user record ({ id, email, display_name, is_admin, onboarded, profile }) or null. */
export const currentUser = writable(null);

/** True once the initial auth/user load has finished (prevents route-guard flicker). */
export const userLoaded = writable(false);

/** Transient toast notifications: [{ id, title, body, kind }] */
export const toasts = writable([]);

/** Gamification summary from GET /gamification/summary (or null). */
export const gamification = writable(null);

const THEME_KEY = 'upvex-theme';

function initialTheme() {
	if (!browser) return 'dark';
	try {
		const stored = localStorage.getItem(THEME_KEY);
		if (stored === 'light' || stored === 'dark') return stored;
	} catch {
		/* ignore */
	}
	return 'dark';
}

function applyTheme(value) {
	if (!browser) return;
	document.documentElement.dataset.theme = value;
	try {
		localStorage.setItem(THEME_KEY, value);
	} catch {
		/* ignore */
	}
}

/** 'dark' | 'light' — persisted to localStorage. */
export const theme = writable(initialTheme());

if (browser) {
	applyTheme(get(theme));
	theme.subscribe(applyTheme);
}

export function toggleTheme() {
	theme.update((t) => (t === 'dark' ? 'light' : 'dark'));
}

let toastId = 0;
export function pushToast(title, body = '', kind = 'info', ms = 4000) {
	const id = ++toastId;
	toasts.update((t) => [...t, { id, title, body, kind }]);
	setTimeout(() => toasts.update((t) => t.filter((x) => x.id !== id)), ms);
}

/** Fetch and cache gamification summary. Safe to call when logged out. */
export async function refreshGamification(fetcher) {
	try {
		const data = await fetcher('/gamification/summary');
		gamification.set(data);
		return data;
	} catch {
		gamification.set(null);
		return null;
	}
}
