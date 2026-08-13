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
			<a href="/auth" class="mnav-cta">Talk to us</a>
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
		background: color-mix(in srgb, var(--bg-elevated) 88%, transparent);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid var(--border);
	}

	.brand {
		font-family: var(--font-display);
	}

	.brand:hover {
		text-decoration: none;
	}

	.links {
		display: flex;
		align-items: center;
		gap: 4px;
		flex: 1;
	}

	.links a {
		padding: 8px 12px;
		color: var(--text-dim);
		font-weight: 500;
		font-size: 13.5px;
		border-radius: 8px;
	}

	.links a:hover {
		color: var(--text);
		text-decoration: none;
		background: var(--bg-hover);
	}

	.links a.active {
		color: var(--accent);
		background: var(--accent-soft);
		font-weight: 600;
	}

	.actions {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.mnav-cta {
		display: inline-flex;
		align-items: center;
		padding: 8px 14px;
		background: var(--accent);
		color: var(--accent-fg);
		font-weight: 600;
		font-size: 13px;
		text-decoration: none;
		border-radius: 8px;
	}

	.mnav-cta:hover {
		text-decoration: none;
		background: var(--accent-bright);
	}

	.burger {
		display: none;
		flex-direction: column;
		justify-content: center;
		gap: 4px;
		width: 34px;
		height: 34px;
		padding: 0;
		border: 1px solid var(--border-strong);
		background: var(--bg-card);
		border-radius: 8px;
		cursor: pointer;
	}

	.burger span {
		display: block;
		height: 2px;
		margin: 0 7px;
		background: var(--text-dim);
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
		border-bottom: 1px solid var(--border);
	}

	.mobile-menu a {
		padding: 12px 4px;
		font-weight: 600;
		color: var(--text-dim);
		border-bottom: 1px solid var(--border);
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
