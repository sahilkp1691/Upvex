<script>
	import { get } from '$lib/api.js';

	let data = $state(null);
	let loading = $state(true);

	$effect(() => {
		get('/admin/analytics')
			.then((d) => (data = d))
			.finally(() => (loading = false));
	});
</script>

<svelte:head><title>Admin analytics — Upvex</title></svelte:head>

{#if loading}
	<p class="faint">Loading analytics...</p>
{:else if data}
	<div class="stats">
		<div class="card stat">
			<span class="num">{data.total_users}</span><span class="label">Users</span>
		</div>
		<div class="card stat">
			<span class="num">{data.total_goals}</span><span class="label">Goals</span>
		</div>
		<div class="card stat">
			<span class="num">{data.goals_by_status.active ?? 0}</span>
			<span class="label">Active goals</span>
		</div>
		<div class="card stat">
			<span class="num">{data.generated_content_by_status.ready ?? 0}</span>
			<span class="label">Cached lessons</span>
		</div>
	</div>

	<div class="cols">
		<div class="card">
			<h3>Common root gaps</h3>
			<p class="muted small">
				If many users share a root gap, that concept may need clearer or earlier placement in the
				graph.
			</p>
			{#if data.common_root_gaps.length === 0}
				<p class="faint">No data yet.</p>
			{:else}
				{#each data.common_root_gaps as gap (gap.concept_node_id)}
					<div class="row">
						<span>{gap.title}</span>
						<span class="tag tag-warn">{gap.user_count} user{gap.user_count === 1 ? '' : 's'}</span>
					</div>
				{/each}
			{/if}
		</div>

		<div class="card">
			<h3>Concept completions</h3>
			<p class="muted small">Completions and average quiz score per concept.</p>
			{#if data.concept_stats.length === 0}
				<p class="faint">No completions yet.</p>
			{:else}
				{#each data.concept_stats as c (c.concept_node_id)}
					<div class="row">
						<span>{c.title}</span>
						<span class="muted">
							{c.completions} done{c.avg_quiz_score != null ? ` · avg ${c.avg_quiz_score}` : ''}
						</span>
					</div>
				{/each}
			{/if}
		</div>
	</div>
{/if}

<style>
	.stats {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
		gap: 14px;
		margin-bottom: 20px;
	}

	.stat {
		text-align: center;
		padding: 18px;
	}

	.num {
		display: block;
		font-size: 30px;
		font-weight: 750;
		color: var(--accent-bright);
	}

	.cols {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 16px;
	}

	@media (max-width: 860px) {
		.cols {
			grid-template-columns: 1fr;
		}
	}

	.row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		padding: 9px 0;
		border-top: 1px solid var(--border);
		font-size: 14px;
	}

	.small {
		font-size: 13px;
	}
</style>
