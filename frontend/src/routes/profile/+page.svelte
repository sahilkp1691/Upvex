<script>
	import { get } from '$lib/api.js';
	import { currentUser } from '$lib/stores.js';

	let summary = $state(null);
	let allBadges = $state([]);
	let goals = $state([]);
	let loading = $state(true);

	$effect(() => {
		Promise.all([get('/gamification/summary'), get('/gamification/badges'), get('/goals')])
			.then(([s, b, g]) => {
				summary = s;
				allBadges = b;
				goals = g;
			})
			.finally(() => (loading = false));
	});

	const reasonLabels = {
		lesson_complete: 'Lesson completed',
		quiz_score: 'Quiz score',
		streak_bonus: 'Streak bonus',
		milestone: 'Milestone'
	};
</script>

<svelte:head><title>Profile — Upvex</title></svelte:head>

<div class="page narrow">
	<h1>{$currentUser?.display_name || 'Your profile'}</h1>

	{#if loading}
		<p class="faint">Loading...</p>
	{:else if summary}
		<div class="stats">
			<div class="card stat">
				<span class="num">{summary.total_xp.toLocaleString()}</span>
				<span class="label">Total XP</span>
			</div>
			<div class="card stat">
				<span class="num">{summary.streak.current}</span>
				<span class="label">Day streak</span>
			</div>
			<div class="card stat">
				<span class="num">{summary.streak.longest}</span>
				<span class="label">Longest streak</span>
			</div>
		</div>

		<h2 class="section-h">Badge case</h2>
		<div class="badges">
			{#each allBadges as badge (badge.id)}
				<div class="card badge" class:earned={badge.earned}>
					<span class="b-name">{badge.name}</span>
					<span class="b-desc muted">{badge.description}</span>
					{#if badge.earned}<span class="tag tag-up">Earned</span>{/if}
				</div>
			{/each}
		</div>

		<h2 class="section-h">Active goals</h2>
		{#if goals.length === 0}
			<p class="muted">No goals yet — <a href="/topics">pick a topic</a> to get started.</p>
		{:else}
			<div class="goal-list">
				{#each goals as goal (goal.id)}
					<a class="card goal" href={goal.status === 'diagnostic_pending' ? `/diagnostic/${goal.id}` : `/roadmap/${goal.id}`}>
						<span class="g-name">{goal.topic_name}</span>
						<span class="muted g-meta">
							{goal.status === 'diagnostic_pending'
								? 'Diagnostic pending'
								: `Level ${Math.round(goal.level_score ?? 0)} · ${goal.completed_concepts.length} concepts done`}
						</span>
					</a>
				{/each}
			</div>
		{/if}

		{#if summary.recent_xp.length}
			<h2 class="section-h">Recent activity</h2>
			<div class="card">
				{#each summary.recent_xp as e, i (i)}
					<div class="xp-row">
						<span>{reasonLabels[e.reason] || e.reason}</span>
						<span class="xp-amt">+{e.amount} XP</span>
					</div>
				{/each}
			</div>
		{/if}
	{/if}
</div>

<style>
	.narrow {
		max-width: 720px;
	}

	.stats {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 14px;
	}

	.stat {
		text-align: center;
		padding: 20px;
	}

	.num {
		display: block;
		font-size: 34px;
		font-weight: 750;
		color: var(--accent-bright);
	}

	.section-h {
		margin-top: 36px;
	}

	.badges {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}

	.badge {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 16px;
		opacity: 0.55;
	}

	.badge.earned {
		opacity: 1;
		border-color: rgba(240, 198, 90, 0.45);
	}

	.b-name {
		font-weight: 650;
	}

	.b-desc {
		font-size: 13px;
		flex: 1;
	}

	.tag {
		align-self: flex-start;
	}

	.goal-list {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.goal {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 20px;
		color: var(--text);
	}

	.goal:hover {
		text-decoration: none;
		border-color: var(--accent);
	}

	.g-name {
		font-weight: 620;
	}

	.g-meta {
		font-size: 13.5px;
	}

	.xp-row {
		display: flex;
		justify-content: space-between;
		padding: 8px 0;
		border-top: 1px solid var(--border);
		font-size: 14px;
	}

	.xp-row:first-child {
		border-top: none;
	}

	.xp-amt {
		color: var(--up);
		font-weight: 650;
	}
</style>
