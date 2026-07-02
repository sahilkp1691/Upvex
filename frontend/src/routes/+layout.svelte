<script>
	import '../app.css';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { get } from '$lib/api.js';
	import { supabase, authEnabled } from '$lib/supabase.js';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import Toasts from '$lib/Toasts.svelte';

	let { children } = $props();

	async function loadUser() {
		try {
			if (authEnabled) {
				const { data } = await supabase.auth.getSession();
				if (!data?.session) {
					currentUser.set(null);
					return;
				}
			}
			currentUser.set(await get('/me'));
		} catch {
			currentUser.set(null);
		}
	}

	$effect(() => {
		loadUser().finally(() => userLoaded.set(true));
		if (authEnabled) {
			const { data } = supabase.auth.onAuthStateChange(() => loadUser());
			return () => data.subscription.unsubscribe();
		}
	});

	async function signOut() {
		if (authEnabled) await supabase.auth.signOut();
		currentUser.set(null);
		goto('/');
	}

	const navLinks = [
		{ href: '/topics', label: 'Learn' },
		{ href: '/leaderboard', label: 'Leaderboard' },
		{ href: '/profile', label: 'Profile' }
	];

	let onLanding = $derived(page.url.pathname === '/');
</script>

<div class="shell">
	{#if !onLanding}
		<header>
			<a href={$currentUser ? '/topics' : '/'} class="brand"><Logo size={24} /></a>
			{#if $currentUser}
				<nav>
					{#each navLinks as l (l.href)}
						<a href={l.href} class:active={page.url.pathname.startsWith(l.href)}>{l.label}</a>
					{/each}
					{#if $currentUser.is_admin}
						<a href="/admin" class:active={page.url.pathname.startsWith('/admin')}>Admin</a>
					{/if}
				</nav>
				<div class="user-area">
					<span class="muted name">{$currentUser.display_name || $currentUser.email}</span>
					<button class="btn btn-sm" onclick={signOut}>Sign out</button>
				</div>
			{/if}
		</header>
	{/if}
	<main>
		{@render children()}
	</main>
	<Toasts />
</div>

<style>
	.shell {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	header {
		display: flex;
		align-items: center;
		gap: 30px;
		padding: 14px 28px;
		border-bottom: 1px solid var(--border);
		background: var(--bg-elevated);
		position: sticky;
		top: 0;
		z-index: 50;
	}

	.brand:hover {
		text-decoration: none;
	}

	nav {
		display: flex;
		gap: 4px;
		flex: 1;
	}

	nav a {
		padding: 7px 14px;
		border-radius: var(--radius-sm);
		color: var(--text-dim);
		font-weight: 550;
		font-size: 14.5px;
	}

	nav a:hover {
		color: var(--text);
		background: var(--bg-hover);
		text-decoration: none;
	}

	nav a.active {
		color: var(--accent-bright);
		background: var(--accent-soft);
	}

	.user-area {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.name {
		font-size: 13.5px;
	}

	.btn-sm {
		padding: 6px 13px;
		font-size: 13px;
	}

	main {
		flex: 1;
	}
</style>
