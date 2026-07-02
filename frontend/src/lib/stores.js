import { writable } from 'svelte/store';

/** Current backend user record ({ id, email, display_name, is_admin, onboarded, profile }) or null. */
export const currentUser = writable(null);

/** True once the initial auth/user load has finished (prevents route-guard flicker). */
export const userLoaded = writable(false);

/** Transient toast notifications: [{ id, title, body, kind }] */
export const toasts = writable([]);

let toastId = 0;
export function pushToast(title, body = '', kind = 'info', ms = 4000) {
	const id = ++toastId;
	toasts.update((t) => [...t, { id, title, body, kind }]);
	setTimeout(() => toasts.update((t) => t.filter((x) => x.id !== id)), ms);
}
