<script>
	import { get } from '$lib/api.js';
	import { currentUser, gamification } from '$lib/stores.js';

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
				gamification.set(s);
			})
			.finally(() => (loading = false));
	});

	const reasonLabels = {
		lesson_complete: 'Lesson completed',
		quiz_score: 'Quiz score',
		streak_bonus: 'Streak bonus',
		milestone: 'Milestone'
	};

	let levelPct = $derived(
		summary && summary.xp_to_next_level != null
			? Math.min(
					100,
					Math.round(
						(summary.xp_into_level / (summary.xp_into_level + summary.xp_to_next_level || 1)) * 100
					)
				)
			: 0
	);
</script>

<svelte:head><title>Profile — Upvex</title></svelte:head>

<div class="page narrow">
	<h1>{$currentUser?.display_name || 'Your profile'}</h1>

	{#if loading}
		<p class="faint">Loading...</p>
	{:else if summary}
		<section class="hero">
			<div class="level-block">
				<span class="lvl-num">Lv {summary.level}</span>
				<div class="lvl-meta">
					<span class="xp-total">{summary.total_xp.toLocaleString()} XP</span>
					<div class="progress-bar">
						<span style="width: {levelPct}%"></span>
					</div>
					<span class="faint"
						>{summary.xp_into_level} / {summary.xp_into_level + summary.xp_to_next_level} toward
						level {summary.level + 1}</span
					>
				</div>
			</div>
			<div class="streaks">
				<div class="streak-pill">
					<span class="num">{summary.streak.current}</span>
					<span class="label">Day streak</span>
				</div>
				<div class="streak-pill">
					<span class="num">{summary.streak.longest}</span>
					<span class="label">Longest</span>
				</div>
			</div>
		</section>

		<h2 class="section-h">Badge case</h2>
		<div class="badges">
			{#each allBadges as badge (badge.id)}
				<div class="badge-tile" class:earned={badge.earned} class:locked={!badge.earned}>
					<span class="b-name">{badge.name}</span>
					<span class="b-desc">{badge.description}</span>
					{#if badge.earned}
						<span class="tag tag-gold">Earned</span>
					{:else}
						<span class="tag tag-dim">Locked</span>
					{/if}
				</div>
			{/each}
		</div>

		<h2 class="section-h">Active goals</h2>
		{#if goals.length === 0}
			<p class="muted">No goals yet — <a href="/topics">pick a topic</a> to get started.</p>
		{:else}
			<div class="goal-list">
				{#each goals as goal (goal.id)}
					<a
						class="goal"
						href={goal.status === 'diagnostic_pending'
							? `/diagnostic/${goal.id}`
							: `/roadmap/${goal.id}`}
					>
						<span class="g-name">{goal.topic_name}</span>
						<span class="muted g-meta">
							{goal.status === 'diagnostic_pending'
								? 'Diagnostic pending'
								: `Skill ${Math.round(goal.level_score ?? 0)} · ${goal.completed_concepts.length} concepts done`}
						</span>
					</a>
				{/each}
			</div>
		{/if}

		{#if summary.recent_xp.length}
			<h2 class="section-h">Recent activity</h2>
			<div class="activity">
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

	.hero {
		display: flex;
		flex-wrap: wrap;
		gap: 24px;
		align-items: stretch;
		padding: 22px 0 8px;
		border-bottom: 1px solid var(--border);
	}

	.level-block {
		flex: 1 1 260px;
		display: flex;
		gap: 18px;
		align-items: center;
	}

	.lvl-num {
		font-family: var(--font-display);
		font-size: 42px;
		font-weight: 800;
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		line-height: 1;
	}

	.lvl-meta {
		flex: 1;
		display: flex;
		flex-direction: column;
		gap: 8px;
		font-size: 13px;
	}

	.xp-total {
		font-weight: 700;
		color: var(--gold);
		font-size: 15px;
	}

	.streaks {
		display: flex;
		gap: 12px;
	}

	.streak-pill {
		min-width: 88px;
		text-align: center;
		padding: 14px 16px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		background: var(--bg-elevated);
	}

	.streak-pill .num {
		display: block;
		font-family: var(--font-display);
		font-size: 28px;
		font-weight: 800;
		color: var(--warn);
	}

	.section-h {
		margin-top: 36px;
		font-size: 1.15rem;
	}

	.badges {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}

	.goal-list {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.goal {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 16px 0;
		border-bottom: 1px solid var(--border);
		color: var(--text);
		gap: 16px;
	}

	.goal:hover {
		text-decoration: none;
		color: var(--up);
	}

	.g-name {
		font-weight: 650;
	}

	.g-meta {
		font-size: 13.5px;
		flex-shrink: 0;
	}

	.activity {
		border-top: 1px solid var(--border);
	}

	.xp-row {
		display: flex;
		justify-content: space-between;
		padding: 11px 0;
		border-bottom: 1px solid var(--border);
		font-size: 14px;
	}

	.xp-amt {
		color: var(--up);
		font-weight: 650;
	}
</style>
