import { ApiError } from './api.js';

/** Turn Supabase/API failures into user-facing auth messages. */
export function formatAuthError(err, mode = 'signin') {
	if (err instanceof ApiError) {
		if (err.status === 0) return err.message;
		if (err.status === 401) return 'Your session expired. Please sign in again.';
		if (err.status >= 500) return 'Something went wrong on our side. Please try again in a moment.';
		return err.message;
	}

	const message = err?.message || '';

	if (/failed to fetch|networkerror|load failed/i.test(message)) {
		return 'Could not reach the server. Make sure the backend is running and try again.';
	}
	if (/invalid login credentials|invalid email or password/i.test(message)) {
		return mode === 'signin'
			? 'Incorrect email or password. If you do not have an account yet, switch to Create account.'
			: message;
	}
	if (/token has expired|otp.*expired|expired or is invalid|invalid.*(otp|token|code)/i.test(message)) {
		return 'That code is invalid or has expired. Request a new one and try again.';
	}
	if (/email not confirmed|confirm your email/i.test(message)) {
		return 'Please confirm your email before signing in. Check your inbox or resend the confirmation email below.';
	}
	if (/user already registered|already been registered/i.test(message)) {
		return 'An account with this email already exists. Sign in instead.';
	}
	if (/signup is disabled/i.test(message)) {
		return 'New sign-ups are currently disabled.';
	}

	return message || 'Authentication failed';
}
