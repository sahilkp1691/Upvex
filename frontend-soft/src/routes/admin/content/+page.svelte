<script>
	import { get } from '$lib/api.js';

	let items = $state([]);
	let topics = $state([]);
	let loading = $state(true);
	let filterTopic = $state('');
	let filterStatus = $state('');
	let detail = $state(null);

	$effect(() => {
		get('/admin/topics').then((t) => (topics = t));
	});

	$effect(() => {
		const params = new URLSearchParams();
		if (filterTopic) params.set('topic_id', filterTopic);
		if (filterStatus) params.set('status', filterStatus);
		loading = true;
		get(`/admin/content?${params}`)
			.then((i) => (items = i))
			.finally(() => (loading = false));
	});

	async function openDetail(item) {
		detail = await get(`/admin/content/${item.id}`);
	}

	const statusTag = { ready: 'tag-up', pending: 'tag-warn', failed: 'tag-danger' };
</script>

<svelte:head><title>Content review — Upvex</title></svelte:head>

<div class="head-row">
	<div>
		<h2>Content review queue</h2>
		<p class="muted">Everything generated and served to real users, keyed by profile-signature.</p>
	</div>
	<div class="filters">
		<select class="input" bind:value={filterTopic}>
			<option value="">All topics</option>
			{#each topics as t (t.id)}<option value={t.id}>{t.name}</option>{/each}
		</select>
		<select class="input" bind:value={filterStatus}>
			<option value="">All statuses</option>
			<option value="ready">ready</option>
			<option value="pending">pending</option>
			<option value="failed">failed</option>
		</select>
	</div>
</div>

{#if detail}
	<div class="card detail">
		<div class="d-head">
			<h3>{detail.lesson_body?.title ?? detail.concept_node_id}</h3>
			<button class="btn btn-xs" onclick={() => (detail = null)}>Close</button>
		</div>
		<div class="d-meta">
			<span class="tag {statusTag[detail.status] ?? 'tag-dim'}">{detail.status}</span>
			<span class="faint">contract v{detail.generation_contract_version}</span>
			<span class="faint">{detail.model_used ?? ''}</span>
			<span class="faint sig">{detail.signature}</span>
		</div>
		<span class="label">Signature inputs</span>
		<pre>{JSON.stringify(detail.signature_inputs, null, 2)}</pre>
		{#if detail.lesson_body}
			<span class="label">Lesson body</span>
			<pre>{JSON.stringify(detail.lesson_body, null, 2)}</pre>
		{/if}
		{#if detail.quiz_body}
			<span class="label">Quiz body</span>
			<pre>{JSON.stringify(detail.quiz_body, null, 2)}</pre>
		{/if}
		{#if detail.error}
			<span class="label">Error</span>
			<pre>{detail.error}</pre>
		{/if}
	</div>
{/if}

{#if loading}
	<p class="faint">Loading...</p>
{:else if items.length === 0}
	<p class="faint">No generated content yet.</p>
{:else}
	<div class="list">
		{#each items as item (item.id)}
			<button class="card row" onclick={() => openDetail(item)}>
				<div class="r-main">
					<span class="r-title">{item.concept_title ?? item.concept_node_id}</span>
					<span class="faint r-sig">
						{item.signature_inputs?.difficulty_band} · {item.signature_inputs?.learning_style} ·
						{item.signature_inputs?.tone_preference}
					</span>
				</div>
				<div class="r-side">
					<span class="tag {statusTag[item.status] ?? 'tag-dim'}">{item.status}</span>
					<span class="faint">v{item.generation_contract_version}</span>
					<span class="faint">{new Date(item.created_at).toLocaleDateString()}</span>
				</div>
			</button>
		{/each}
	</div>
{/if}

<style>
	.head-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 20px;
		margin-bottom: 18px;
		flex-wrap: wrap;
	}

	.head-row h2 {
		margin-bottom: 4px;
	}

	.filters {
		display: flex;
		gap: 10px;
	}

	.filters .input {
		width: auto;
	}

	.list {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 16px;
		text-align: left;
		cursor: pointer;
		color: var(--text);
		font-family: inherit;
		font-size: inherit;
	}

	.row:hover {
		border-color: var(--accent);
	}

	.r-main {
		display: flex;
		flex-direction: column;
		gap: 2px;
	}

	.r-title {
		font-weight: 620;
	}

	.r-sig {
		font-size: 12.5px;
	}

	.r-side {
		display: flex;
		align-items: center;
		gap: 12px;
		font-size: 12.5px;
		flex-shrink: 0;
	}

	.detail {
		margin-bottom: 20px;
	}

	.d-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.d-head h3 {
		margin: 0;
	}

	.d-meta {
		display: flex;
		align-items: center;
		gap: 12px;
		margin: 10px 0 16px;
		flex-wrap: wrap;
	}

	.sig {
		font-family: var(--mono);
		font-size: 11.5px;
	}

	.label {
		margin-top: 14px;
	}

	pre {
		max-height: 340px;
		overflow: auto;
		font-size: 12px;
	}

	.btn-xs {
		padding: 4px 10px;
		font-size: 12.5px;
	}
</style>
