<script>
	import { goto } from '$app/navigation';
	import { supabase, authEnabled } from '$lib/supabase.js';
	import { get } from '$lib/api.js';
	import { currentUser } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';

	let mode = $state('signin'); // signin | signup
	let email = $state('');
	let password = $state('');
	let error = $state('');
	let notice = $state('');
	let busy = $state(false);

	async function afterAuth() {
		const me = await get('/me');
		currentUser.set(me);
		goto(me.onboarded ? '/topics' : '/onboarding');
	}

	async function submit(e) {
		e.preventDefault();
		error = '';
		notice = '';
		busy = true;
		try {
			if (!authEnabled) {
				// Dev-bypass mode: backend accepts requests without a token
				await afterAuth();
				return;
			}
			if (mode === 'signup') {
				const { data, error: err } = await supabase.auth.signUp({ email, password });
				if (err) throw err;
				if (data.session) await afterAuth();
				else notice = 'Check your email to confirm your account, then sign in.';
			} else {
				const { error: err } = await supabase.auth.signInWithPassword({ email, password });
				if (err) throw err;
				await afterAuth();
			}
		} catch (err) {
			error = err.message || 'Authentication failed';
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Sign in — Upvex</title></svelte:head>

<div class="auth-wrap">
	<div class="card auth-card">
		<div class="head"><Logo size={26} /></div>

		{#if !authEnabled}
			<p class="muted dev-note">
				Development mode: Supabase is not configured, so you'll continue as a local dev user.
			</p>
			<button class="btn btn-primary full" onclick={submit} disabled={busy}>
				Continue as Dev User
			</button>
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
		{/if}

		{#if error}<p class="error">{error}</p>{/if}
		{#if notice}<p class="notice">{notice}</p>{/if}
	</div>
</div>

<style>
	.auth-wrap {
		display: flex;
		justify-content: center;
		padding: 90px 20px;
	}

	.auth-card {
		width: 100%;
		max-width: 400px;
	}

	.head {
		display: flex;
		justify-content: center;
		margin-bottom: 20px;
	}

	.tabs {
		display: flex;
		gap: 6px;
		margin-bottom: 20px;
	}

	.tabs button {
		flex: 1;
		padding: 9px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--bg-elevated);
		color: var(--text-dim);
		font-weight: 550;
		cursor: pointer;
	}

	.tabs button.active {
		background: var(--accent-soft);
		border-color: var(--accent);
		color: var(--accent-bright);
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
</style>
