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
		<span class="brand-tag">// VECTOR&nbsp;OS</span>
	</a>

	<nav class="links">
		{#each links as l (l.href)}
			<a href={l.href} class:active={page.url.pathname === l.href}>
				<span class="br">[</span>{l.label}<span class="br">]</span>
			</a>
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
		--sig: var(--mkt-signal, var(--warn));
		position: sticky;
		top: 0;
		z-index: 60;
		display: flex;
		align-items: center;
		gap: 28px;
		padding: 14px clamp(20px, 4vw, 48px);
		background: color-mix(in srgb, var(--bg) 90%, transparent);
		backdrop-filter: blur(10px);
		border-bottom: 1px solid var(--border);
	}

	.brand {
		display: flex;
		align-items: baseline;
		gap: 10px;
	}

	.brand:hover {
		text-decoration: none;
	}

	.brand-tag {
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
		font-size: 10.5px;
		font-weight: 600;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		white-space: nowrap;
		display: none;
	}

	@media (min-width: 560px) {
		.brand-tag {
			display: inline;
		}
	}

	.links {
		display: flex;
		align-items: center;
		gap: 4px;
		flex: 1;
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
	}

	.links a {
		padding: 8px 10px;
		color: var(--text-dim);
		font-weight: 500;
		font-size: 13.5px;
		letter-spacing: 0.01em;
	}

	.links a .br {
		color: var(--text-faint);
		transition: color 0.15s;
	}

	.links a:hover {
		color: var(--text);
		text-decoration: none;
	}

	.links a:hover .br {
		color: var(--sig);
	}

	.links a.active {
		color: var(--sig);
	}

	.links a.active .br {
		color: var(--sig);
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
		background: var(--sig);
		color: var(--bg);
		font-weight: 700;
		font-size: 13.5px;
		letter-spacing: 0.01em;
		text-decoration: none;
		clip-path: polygon(0 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%);
		transition: transform 0.15s ease;
	}

	.mnav-cta:hover {
		text-decoration: none;
		transform: translateY(-1px);
	}

	.mnav-cta:active {
		transform: translateY(0);
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
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
	}

	.mobile-menu a {
		padding: 12px 4px;
		font-weight: 600;
		color: var(--text-dim);
		border-bottom: 1px solid var(--border);
	}

	.mobile-menu a:last-child {
		border-bottom: none;
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
