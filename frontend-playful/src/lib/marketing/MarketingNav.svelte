<script>
	import { page } from '$app/state';
	import { currentUser } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import ThemeToggle from '$lib/ThemeToggle.svelte';

	const links = [
		{ href: '/solutions', label: 'Solutions' },
		{ href: '/pitch', label: 'Pitch' }
	];

	let menuOpen = $state(false);
</script>

<header class="mnav">
	<a href="/" class="brand" onclick={() => (menuOpen = false)}>
		<Logo size={26} />
	</a>

	<nav class="links">
		{#each links as l (l.href)}
			<a href={l.href} class:active={page.url.pathname === l.href}>{l.label}</a>
		{/each}
	</nav>

	<div class="actions">
		<ThemeToggle />
		{#if $currentUser}
			<a href="/topics" class="mnav-cta">Go to app</a>
		{:else}
			<a href="/auth" class="mnav-cta">Sign in</a>
		{/if}
		<button
			class="burger"
			type="button"
			aria-label="Toggle menu"
			aria-expanded={menuOpen}
			onclick={() => (menuOpen = !menuOpen)}
		>
			<span></span><span></span><span></span>
		</button>
	</div>

	{#if menuOpen}
		<div class="mobile-menu">
			{#each links as l (l.href)}
				<a href={l.href} onclick={() => (menuOpen = false)}>{l.label}</a>
			{/each}
		</div>
	{/if}
</header>

<style>
	.mnav {
		position: sticky;
		top: 0;
		z-index: 60;
		display: flex;
		align-items: center;
		gap: 28px;
		padding: 14px clamp(20px, 4vw, 48px);
		background: color-mix(in srgb, var(--bg) 92%, transparent);
		backdrop-filter: blur(10px);
		border-bottom: 3px solid var(--ink);
	}

	.brand:hover {
		text-decoration: none;
	}

	.links {
		display: flex;
		align-items: center;
		gap: 6px;
		flex: 1;
	}

	.links a {
		padding: 8px 14px;
		color: var(--text-dim);
		font-weight: 600;
		font-size: 14px;
		border-radius: 999px;
		border: 2px solid transparent;
	}

	.links a:hover {
		color: var(--text);
		text-decoration: none;
		background: var(--bg-hover);
	}

	.links a.active {
		color: var(--gold-fg);
		background: var(--gold-bright);
		border-color: var(--ink);
	}

	.actions {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.mnav-cta {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 9px 18px;
		background: var(--accent);
		color: #fff;
		font-weight: 700;
		font-size: 14px;
		text-decoration: none;
		border-radius: 12px;
		border: 2.5px solid var(--ink);
		box-shadow: 3px 3px 0 var(--ink);
	}

	.mnav-cta:hover {
		text-decoration: none;
		transform: translate(-1px, -1px);
		box-shadow: 4px 4px 0 var(--ink);
	}

	.burger {
		display: none;
		flex-direction: column;
		justify-content: center;
		gap: 4px;
		width: 34px;
		height: 34px;
		padding: 0;
		border: 2.5px solid var(--ink);
		background: var(--bg-card);
		border-radius: 10px;
		cursor: pointer;
		box-shadow: 2px 2px 0 var(--ink);
	}

	.burger span {
		display: block;
		height: 2px;
		margin: 0 7px;
		background: var(--text);
	}

	.mobile-menu {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		display: flex;
		flex-direction: column;
		padding: 10px clamp(20px, 4vw, 48px) 16px;
		background: var(--bg);
		border-bottom: 3px solid var(--ink);
	}

	.mobile-menu a {
		padding: 12px 4px;
		font-weight: 700;
		color: var(--text-dim);
		border-bottom: 2px solid color-mix(in srgb, var(--ink) 20%, transparent);
	}

	@media (max-width: 720px) {
		.links {
			display: none;
		}

		.burger {
			display: flex;
		}
	}
</style>
