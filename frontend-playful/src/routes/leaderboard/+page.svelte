<script>
	import { get } from '$lib/api.js';
	import { currentUser } from '$lib/stores.js';

	let board = $state(null);
	let loading = $state(true);

	$effect(() => {
		get('/gamification/leaderboard')
			.then((b) => (board = b))
			.finally(() => (loading = false));
	});

	let inTop = $derived(
		board?.entries?.some((e) => e.user_id === $currentUser?.id) ?? false
	);

	function medal(rank) {
		if (rank === 1) return '1st';
		if (rank === 2) return '2nd';
		if (rank === 3) return '3rd';
		return `#${rank}`;
	}
</script>

<svelte:head><title>Leaderboard — Upvex</title></svelte:head>

<div class="page narrow">
	<h1>Weekly leaderboard</h1>
	<p class="muted">XP earned in the last {board?.window_days ?? 7} days.</p>

	{#if loading}
		<p class="faint">Loading...</p>
	{:else if board && board.entries.length === 0}
		<div class="empty">
			<p class="muted">No XP earned this week yet. Complete a lesson to claim the top spot.</p>
		</div>
	{:else if board}
		{#if board.me && !inTop}
			<div class="my-rank">
				<span class="mr-label">Your rank</span>
				<span class="mr-rank">#{board.my_rank}</span>
				<span class="mr-xp">{board.my_xp.toLocaleString()} XP this week</span>
			</div>
		{/if}

		<div class="list">
			{#each board.entries as entry (entry.user_id)}
				<div
					class="row"
					class:me={entry.user_id === $currentUser?.id}
					class:top={entry.rank <= 3}
				>
					<span class="rank" class:gold={entry.rank === 1} class:silver={entry.rank === 2} class:bronze={entry.rank === 3}>
						{medal(entry.rank)}
					</span>
					<span class="name">
						{entry.display_name}
						{#if entry.user_id === $currentUser?.id}<span class="you">you</span>{/if}
					</span>
					<span class="xp">{entry.xp.toLocaleString()} XP</span>
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.narrow {
		max-width: 620px;
	}

	.my-rank {
		display: flex;
		align-items: baseline;
		gap: 12px;
		flex-wrap: wrap;
		padding: 14px 18px;
		margin-bottom: 16px;
		border-radius: var(--radius);
		border: 1px solid color-mix(in srgb, var(--up) 40%, var(--border));
		background: var(--up-soft);
		position: sticky;
		top: 64px;
		z-index: 5;
	}

	.mr-label {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--text-dim);
		font-weight: 650;
	}

	.mr-rank {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 22px;
		color: var(--up);
	}

	.mr-xp {
		margin-left: auto;
		font-weight: 650;
		color: var(--text);
		font-size: 14px;
	}

	.list {
		display: flex;
		flex-direction: column;
		border-top: 1px solid var(--border);
	}

	.row {
		display: grid;
		grid-template-columns: 64px 1fr auto;
		align-items: center;
		gap: 14px;
		padding: 14px 4px;
		border-bottom: 1px solid var(--border);
	}

	.row.me {
		background: var(--accent-soft);
		margin: 0 -12px;
		padding-left: 16px;
		padding-right: 16px;
		border-radius: var(--radius-sm);
		border-bottom-color: transparent;
	}

	.row.top .name {
		font-weight: 700;
	}

	.rank {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 14px;
		color: var(--text-faint);
	}

	.rank.gold {
		color: var(--gold);
		font-size: 16px;
	}

	.rank.silver {
		color: var(--text-dim);
		font-size: 15px;
	}

	.rank.bronze {
		color: #c47a3a;
		font-size: 15px;
	}

	.name {
		font-weight: 550;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.you {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.04em;
		color: var(--accent-bright);
		background: var(--accent-soft);
		padding: 2px 7px;
		border-radius: 999px;
	}

	.xp {
		color: var(--up);
		font-weight: 650;
		font-size: 14px;
	}

	.empty {
		padding: 28px 0;
		text-align: center;
		border-top: 1px solid var(--border);
	}
</style>
