<script>
	import '../app.css';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { get } from '$lib/api.js';
	import { supabase, authEnabled } from '$lib/supabase.js';
	import { currentUser, userLoaded, gamification, refreshGamification } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import ThemeToggle from '$lib/ThemeToggle.svelte';
	import Toasts from '$lib/Toasts.svelte';

	let { children } = $props();

	async function loadUser() {
		try {
			if (authEnabled) {
				const { data } = await supabase.auth.getSession();
				if (!data?.session) {
					currentUser.set(null);
					gamification.set(null);
					return;
				}
			}
			currentUser.set(await get('/me'));
			await refreshGamification(get);
		} catch {
			currentUser.set(null);
			gamification.set(null);
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
		gamification.set(null);
		goto('/');
	}

	const navLinks = [
		{ href: '/topics', label: 'Learn' },
		{ href: '/leaderboard', label: 'Leaderboard' },
		{ href: '/profile', label: 'Profile' }
	];

	let onLanding = $derived(page.url.pathname === '/');

	let levelPct = $derived(
		$gamification && $gamification.xp_to_next_level != null
			? Math.min(
					100,
					Math.round(
						($gamification.xp_into_level /
							($gamification.xp_into_level + $gamification.xp_to_next_level || 1)) *
							100
					)
				)
			: 0
	);
</script>

<div class="shell mesh-bg">
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
					{#if $gamification}
						<a href="/profile" class="hud" title="Your progress">
							<span class="hud-chip streak" class:active={$gamification.streak.current > 0}>
								<span class="flame" aria-hidden="true">&#9670;</span>
								{$gamification.streak.current}
								<span class="hud-label">streak</span>
							</span>
							<span class="hud-chip xp">
								{$gamification.total_xp.toLocaleString()}
								<span class="hud-label">XP</span>
							</span>
							<span class="hud-chip level">
								<span class="lvl">Lv {$gamification.level}</span>
								<span class="progress-bar thin level-bar">
									<span style="width: {levelPct}%"></span>
								</span>
							</span>
						</a>
					{/if}
					<ThemeToggle />
					<span class="muted name">{$currentUser.display_name || $currentUser.email}</span>
					<button class="btn btn-sm" onclick={signOut}>Sign out</button>
				</div>
			{:else}
				<div class="user-area">
					<ThemeToggle />
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
		gap: 20px;
		padding: 12px 24px;
		border-bottom: 1px solid var(--border);
		background: color-mix(in srgb, var(--bg-elevated) 88%, transparent);
		backdrop-filter: blur(12px);
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
		color: var(--up);
		background: var(--up-soft);
	}

	.user-area {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.hud {
		display: flex;
		align-items: center;
		gap: 8px;
		text-decoration: none;
		color: inherit;
	}

	.hud:hover {
		text-decoration: none;
	}

	.hud .flame {
		color: var(--warn);
		font-size: 10px;
		animation: streak-pulse 2s ease-in-out infinite;
	}

	.hud .streak.active .flame {
		animation: streak-pulse 1.2s ease-in-out infinite;
	}

	.hud .lvl {
		font-variant-numeric: tabular-nums;
	}

	.level-bar {
		width: 48px;
		flex-shrink: 0;
	}

	.name {
		font-size: 13.5px;
	}

	main {
		flex: 1;
	}

	@media (max-width: 900px) {
		.hud .hud-chip.xp .hud-label,
		.hud .hud-chip.streak .hud-label {
			display: none;
		}

		.name {
			display: none;
		}

		nav a {
			padding: 7px 10px;
			font-size: 13.5px;
		}
	}
</style>
