<script>
	import { get, post, patch } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	let categories = $state([]);
	let topics = $state([]);
	let loading = $state(true);
	let showNewTopic = $state(false);
	let newTopic = $state({ name: '', description: '', category_id: '' });

	$effect(() => {
		load();
	});

	async function load() {
		try {
			[categories, topics] = await Promise.all([get('/admin/categories'), get('/admin/topics')]);
			if (!newTopic.category_id && categories.length) newTopic.category_id = categories[0].id;
		} finally {
			loading = false;
		}
	}

	async function createTopic() {
		try {
			await post('/admin/topics', { ...newTopic, is_active: true });
			pushToast('Topic created', newTopic.name);
			showNewTopic = false;
			newTopic = { name: '', description: '', category_id: categories[0]?.id ?? '' };
			await load();
		} catch (err) {
			pushToast('Create failed', err.message, 'error');
		}
	}

	async function toggleTopic(topic) {
		try {
			await patch(`/admin/topics/${topic.id}`, {
				category_id: topic.category_id,
				name: topic.name,
				description: topic.description,
				is_active: !topic.is_active
			});
			await load();
		} catch (err) {
			pushToast('Update failed', err.message, 'error');
		}
	}
</script>

<svelte:head><title>Admin topics — Upvex</title></svelte:head>

{#if loading}
	<p class="faint">Loading...</p>
{:else}
	<div class="toolbar">
		<h2>Topics</h2>
		<button class="btn btn-primary" onclick={() => (showNewTopic = !showNewTopic)}>
			{showNewTopic ? 'Cancel' : 'New topic'}
		</button>
	</div>

	{#if showNewTopic}
		<div class="card form">
			<label class="label" for="t-cat">Category</label>
			<select id="t-cat" class="input" bind:value={newTopic.category_id}>
				{#each categories as c (c.id)}
					<option value={c.id}>{c.name}</option>
				{/each}
			</select>
			<label class="label" for="t-name">Name</label>
			<input id="t-name" class="input" bind:value={newTopic.name} placeholder="e.g. Airflow" />
			<label class="label" for="t-desc">Description</label>
			<textarea id="t-desc" class="input" bind:value={newTopic.description}></textarea>
			<button class="btn btn-primary save" disabled={!newTopic.name.trim()} onclick={createTopic}>
				Create
			</button>
		</div>
	{/if}

	<div class="topic-list">
		{#each topics as topic (topic.id)}
			<div class="card topic-row">
				<div class="t-info">
					<span class="t-name">{topic.name}</span>
					<span class="muted t-desc">{topic.description}</span>
					<span class="faint t-meta">{topic.concept_count} concepts</span>
				</div>
				<div class="t-actions">
					<span class="tag {topic.is_active ? 'tag-up' : 'tag-dim'}">
						{topic.is_active ? 'Active' : 'Inactive'}
					</span>
					<a class="btn" href={`/admin/graph/${topic.id}`}>Edit graph</a>
					<button class="btn" onclick={() => toggleTopic(topic)}>
						{topic.is_active ? 'Deactivate' : 'Activate'}
					</button>
				</div>
			</div>
		{/each}
	</div>
{/if}

<style>
	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 16px;
	}

	.toolbar h2 {
		margin: 0;
	}

	.form {
		margin-bottom: 20px;
	}

	.form .label {
		margin-top: 12px;
	}

	.form .label:first-child {
		margin-top: 0;
	}

	.save {
		margin-top: 16px;
	}

	.topic-list {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.topic-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 20px;
	}

	.t-info {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}

	.t-name {
		font-weight: 650;
		font-size: 16px;
	}

	.t-desc {
		font-size: 14px;
	}

	.t-meta {
		font-size: 12.5px;
	}

	.t-actions {
		display: flex;
		align-items: center;
		gap: 10px;
		flex-shrink: 0;
	}
</style>
