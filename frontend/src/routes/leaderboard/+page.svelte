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
</script>

<svelte:head><title>Leaderboard — Upvex</title></svelte:head>

<div class="page narrow">
	<h1>Weekly leaderboard</h1>
	<p class="muted">XP earned in the last {board?.window_days ?? 7} days.</p>

	{#if loading}
		<p class="faint">Loading...</p>
	{:else if board && board.entries.length === 0}
		<div class="card empty">
			<p class="muted">No XP earned this week yet. Complete a lesson to claim the top spot.</p>
		</div>
	{:else if board}
		<div class="card list">
			{#each board.entries as entry (entry.user_id)}
				<div class="row" class:me={entry.user_id === $currentUser?.id}>
					<span class="rank" class:top={entry.rank <= 3}>#{entry.rank}</span>
					<span class="name">{entry.display_name}</span>
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

	.list {
		padding: 8px 0;
	}

	.row {
		display: grid;
		grid-template-columns: 60px 1fr auto;
		align-items: center;
		gap: 14px;
		padding: 12px 22px;
	}

	.row.me {
		background: var(--accent-soft);
	}

	.rank {
		font-weight: 700;
		color: var(--text-faint);
	}

	.rank.top {
		color: var(--gold);
	}

	.name {
		font-weight: 550;
	}

	.xp {
		color: var(--up);
		font-weight: 650;
		font-size: 14px;
	}

	.empty {
		text-align: center;
	}
</style>
