<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { currentUser, userLoaded } from '$lib/stores.js';

	let { children } = $props();

	$effect(() => {
		if ($userLoaded && (!$currentUser || !$currentUser.is_admin)) goto('/topics');
	});

	const links = [
		{ href: '/admin', label: 'Analytics', exact: true },
		{ href: '/admin/topics', label: 'Topics & Graphs' },
		{ href: '/admin/contracts', label: 'Generation Contract' },
		{ href: '/admin/content', label: 'Content Review' }
	];

	function isActive(link) {
		return link.exact ? page.url.pathname === link.href : page.url.pathname.startsWith(link.href);
	}
</script>

<div class="page admin-wide">
	<div class="admin-head">
		<h1>Admin</h1>
		<nav>
			{#each links as l (l.href)}
				<a href={l.href} class:active={isActive(l)}>{l.label}</a>
			{/each}
		</nav>
	</div>
	{@render children()}
</div>

<style>
	.admin-wide {
		max-width: 1180px;
	}

	.admin-head {
		display: flex;
		align-items: center;
		gap: 30px;
		margin-bottom: 26px;
		flex-wrap: wrap;
	}

	.admin-head h1 {
		margin: 0;
	}

	nav {
		display: flex;
		gap: 4px;
	}

	nav a {
		padding: 7px 14px;
		border-radius: var(--radius-sm);
		color: var(--text-dim);
		font-weight: 550;
		font-size: 14px;
	}

	nav a:hover {
		background: var(--bg-hover);
		color: var(--text);
		text-decoration: none;
	}

	nav a.active {
		background: var(--accent-soft);
		color: var(--accent-bright);
	}
</style>
