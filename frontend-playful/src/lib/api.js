import { supabase } from './supabase.js';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
	constructor(status, detail) {
		super(detail || `Request failed (${status})`);
		this.status = status;
	}
}

async function authHeaders() {
	if (!supabase) return {};
	const { data } = await supabase.auth.getSession();
	const token = data?.session?.access_token;
	return token ? { Authorization: `Bearer ${token}` } : {};
}

/** Single fetch wrapper for the Upvex API. */
export async function api(path, { method = 'GET', body } = {}) {
	const headers = { ...(await authHeaders()) };
	if (body !== undefined) headers['Content-Type'] = 'application/json';
	let res;
	try {
		res = await fetch(`${API_URL}/api${path}`, {
			method,
			headers,
			body: body !== undefined ? JSON.stringify(body) : undefined
		});
	} catch {
		throw new ApiError(
			0,
			'Could not reach the server. Make sure the backend is running and try again.'
		);
	}
	if (!res.ok) {
		let detail = null;
		try {
			detail = (await res.json())?.detail;
		} catch {
			/* non-JSON error body */
		}
		throw new ApiError(res.status, typeof detail === 'string' ? detail : JSON.stringify(detail));
	}
	return res.json();
}

export const get = (path) => api(path);
export const post = (path, body = {}) => api(path, { method: 'POST', body });
export const patch = (path, body = {}) => api(path, { method: 'PATCH', body });
export const del = (path) => api(path, { method: 'DELETE' });
