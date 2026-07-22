<script>
	import { goto } from '$app/navigation';
	import { supabase, authEnabled, getAuthRedirectUrl } from '$lib/supabase.js';
	import { get } from '$lib/api.js';
	import { formatAuthError } from '$lib/authErrors.js';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import ThemeToggle from '$lib/ThemeToggle.svelte';

	let mode = $state('signin'); // signin | signup
	let email = $state('');
	let password = $state('');
	let code = $state('');
	let error = $state('');
	let notice = $state('');
	let busy = $state(false);
	let pendingVerification = $state(false);

	$effect(() => {
		if ($userLoaded && $currentUser) {
			goto($currentUser.onboarded ? '/topics' : '/onboarding');
		}
	});

	async function afterAuth() {
		const me = await get('/me');
		currentUser.set(me);
		goto(me.onboarded ? '/topics' : '/onboarding');
	}

	function authOptions() {
		return { emailRedirectTo: getAuthRedirectUrl() };
	}

	async function resendConfirmation() {
		error = '';
		notice = '';
		busy = true;
		try {
			const { error: err } = await supabase.auth.resend({
				type: 'signup',
				email,
				options: authOptions()
			});
			if (err) throw err;
			notice = 'New code sent. Check your inbox.';
		} catch (err) {
			error = formatAuthError(err, 'signup');
		} finally {
			busy = false;
		}
	}

	async function verifyCode(e) {
		e.preventDefault();
		error = '';
		notice = '';
		busy = true;
		try {
			const { error: err } = await supabase.auth.verifyOtp({
				email,
				token: code.trim(),
				type: 'signup'
			});
			if (err) throw err;
			// verifyOtp establishes a session; hydrate the backend user and route on.
			await afterAuth();
		} catch (err) {
			error = formatAuthError(err, 'signup');
		} finally {
			busy = false;
		}
	}

	async function submit(e) {
		e.preventDefault();
		error = '';
		notice = '';
		pendingVerification = false;
		busy = true;
		try {
			if (!authEnabled) {
				// Dev-bypass mode: backend accepts requests without a token
				await afterAuth();
				return;
			}
			if (mode === 'signup') {
				const { data, error: err } = await supabase.auth.signUp({
					email,
					password,
					options: authOptions()
				});
				if (err) throw err;
				// Supabase returns a session only when Confirm email is off (auto-confirm).
				// Treat that as a misconfiguration for this product — require verification.
				if (data.session) {
					await supabase.auth.signOut();
					currentUser.set(null);
					error =
						'Email confirmation is not being enforced by Supabase (account was auto-confirmed). In the dashboard, turn Confirm email OFF, Save, then ON and Save again, then retry with a new email.';
					return;
				}
				if (data.user?.identities?.length === 0) {
					error = 'An account with this email already exists. Sign in instead.';
					mode = 'signin';
					pendingVerification = false;
				} else {
					pendingVerification = true;
					notice = '';
				}
			} else {
				const { error: err } = await supabase.auth.signInWithPassword({ email, password });
				if (err) throw err;
				await afterAuth();
			}
		} catch (err) {
			const message = formatAuthError(err, mode);
			error = message;
			if (/confirm/i.test(message)) pendingVerification = true;
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Sign in — Upvex</title></svelte:head>

<div class="auth-wrap mesh-bg">
	<div class="auth-top">
		<a href="/" class="back muted">Back</a>
		<ThemeToggle />
	</div>
	<div class="auth-card">
		<div class="head"><Logo size={28} /></div>

		{#if !authEnabled}
			<p class="muted dev-note">
				Development mode: Supabase is not configured, so you'll continue as a local dev user.
			</p>
			<button class="btn btn-primary full" onclick={submit} disabled={busy}>
				Continue as Dev User
			</button>
		{:else if pendingVerification}
			<div class="verify-panel">
				<h1 class="verify-title">Enter your code</h1>
				<p class="muted verify-copy">
					We sent a 6-digit verification code to <strong>{email}</strong>. Enter it below to
					activate your account.
				</p>
				<form onsubmit={verifyCode}>
					<input
						id="code"
						class="input code-input"
						type="text"
						inputmode="numeric"
						autocomplete="one-time-code"
						maxlength="6"
						placeholder="000000"
						bind:value={code}
						oninput={() => (code = code.replace(/\D/g, ''))}
						required
					/>
					<button class="btn btn-primary full" type="submit" disabled={busy || code.trim().length !== 6}>
						{busy ? 'Verifying…' : 'Verify and continue'}
					</button>
				</form>
				{#if notice}<p class="notice">{notice}</p>{/if}
				{#if error}<p class="error">{error}</p>{/if}
				<button class="btn full resend" type="button" onclick={resendConfirmation} disabled={busy}>
					{busy ? 'Sending…' : 'Resend code'}
				</button>
				<button
					class="btn full resend"
					type="button"
					disabled={busy}
					onclick={() => {
						pendingVerification = false;
						code = '';
						error = '';
						notice = '';
						mode = 'signin';
					}}
				>
					Back to sign in
				</button>
			</div>
		{:else}
			<div class="tabs">
				<button class:active={mode === 'signin'} onclick={() => (mode = 'signin')}>Sign in</button>
				<button class:active={mode === 'signup'} onclick={() => (mode = 'signup')}>
					Create account
				</button>
			</div>
			<form onsubmit={submit}>
				<label class="label" for="email">Email</label>
				<input id="email" class="input" type="email" bind:value={email} required />
				<label class="label" for="password">Password</label>
				<input
					id="password"
					class="input"
					type="password"
					bind:value={password}
					minlength="6"
					required
				/>
				<button class="btn btn-primary full" type="submit" disabled={busy}>
					{mode === 'signin' ? 'Sign in' : 'Create account'}
				</button>
			</form>
			{#if error}<p class="error">{error}</p>{/if}
			{#if notice}<p class="notice">{notice}</p>{/if}
		{/if}
	</div>
</div>

<style>
	.auth-wrap {
		display: flex;
		flex-direction: column;
		align-items: center;
		min-height: 100vh;
		padding: 24px 20px 80px;
	}

	.auth-top {
		width: 100%;
		max-width: 400px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 40px;
	}

	.back:hover {
		color: var(--text);
		text-decoration: none;
	}

	.auth-card {
		width: 100%;
		max-width: 400px;
		padding: 8px 0;
	}

	.head {
		display: flex;
		justify-content: center;
		margin-bottom: 28px;
	}

	.tabs {
		display: flex;
		gap: 6px;
		margin-bottom: 20px;
		padding: 4px;
		border-radius: var(--radius);
		background: var(--bg-elevated);
		border: 1px solid var(--border);
	}

	.tabs button {
		flex: 1;
		padding: 9px;
		border-radius: var(--radius-sm);
		border: 1px solid transparent;
		background: transparent;
		color: var(--text-dim);
		font-weight: 550;
		cursor: pointer;
	}

	.tabs button.active {
		background: var(--up-soft);
		border-color: color-mix(in srgb, var(--up) 35%, transparent);
		color: var(--up);
	}

	.label {
		margin-top: 14px;
	}

	.full {
		width: 100%;
		justify-content: center;
		margin-top: 20px;
	}

	.dev-note {
		text-align: center;
		font-size: 14px;
	}

	.error {
		margin-top: 14px;
		color: var(--danger);
		font-size: 14px;
	}

	.notice {
		margin-top: 14px;
		color: var(--up);
		font-size: 14px;
	}

	.verify-panel {
		text-align: center;
	}

	.verify-title {
		font-size: 1.25rem;
		margin: 0 0 10px;
	}

	.verify-copy {
		font-size: 14px;
		line-height: 1.45;
		margin: 0 0 8px;
	}

	.verify-copy strong {
		color: var(--text);
	}

	.resend {
		margin-top: 12px;
	}

	.code-input {
		text-align: center;
		font-size: 22px;
		letter-spacing: 0.4em;
		font-variant-numeric: tabular-nums;
	}
</style>
