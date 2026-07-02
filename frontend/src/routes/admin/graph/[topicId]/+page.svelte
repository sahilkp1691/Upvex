<script>
	import { page } from '$app/state';
	import { get, post, patch, del } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	const topicId = page.params.topicId;

	let graph = $state(null);
	let loading = $state(true);
	let editingNode = $state(null); // null | 'new' | node object
	let nodeForm = $state(blankNode());
	let edgeForm = $state({ from_concept_id: '', to_concept_id: '', edge_type: 'required' });

	function blankNode() {
		return {
			title: '',
			learning_objective: '',
			difficulty_tag: 'beginner',
			bloom_level: 'understand',
			estimated_duration_mins: 10,
			is_root: false
		};
	}

	$effect(() => {
		load();
	});

	async function load() {
		try {
			graph = await get(`/admin/topics/${topicId}/graph`);
		} finally {
			loading = false;
		}
	}

	function titleOf(id) {
		return graph?.nodes.find((n) => n.id === id)?.title ?? id;
	}

	function startEdit(node) {
		editingNode = node;
		nodeForm = node === 'new' ? blankNode() : { ...node };
	}

	async function saveNode() {
		try {
			if (editingNode === 'new') {
				await post(`/admin/topics/${topicId}/nodes`, nodeForm);
				pushToast('Concept created', nodeForm.title);
			} else {
				const { id, ...body } = nodeForm;
				await patch(`/admin/nodes/${id}`, body);
				pushToast('Concept updated', nodeForm.title);
			}
			editingNode = null;
			await load();
		} catch (err) {
			pushToast('Save failed', err.message, 'error');
		}
	}

	async function removeNode(node) {
		if (!confirm(`Delete "${node.title}" and all its edges?`)) return;
		try {
			await del(`/admin/nodes/${node.id}`);
			pushToast('Concept deleted', node.title);
			await load();
		} catch (err) {
			pushToast('Delete failed', err.message, 'error');
		}
	}

	async function addEdge() {
		try {
			await post(`/admin/topics/${topicId}/edges`, edgeForm);
			pushToast('Edge added');
			edgeForm = { from_concept_id: '', to_concept_id: '', edge_type: 'required' };
			await load();
		} catch (err) {
			pushToast('Edge rejected', err.message, 'error');
		}
	}

	async function removeEdge(edge) {
		try {
			await del(`/admin/edges/${edge.id}`);
			await load();
		} catch (err) {
			pushToast('Delete failed', err.message, 'error');
		}
	}
</script>

<svelte:head><title>Graph editor — Upvex</title></svelte:head>

<a href="/admin/topics" class="back">Back to topics</a>

{#if loading}
	<p class="faint">Loading graph...</p>
{:else if graph}
	<div class="cols">
		<div>
			<div class="toolbar">
				<h2>Concept nodes ({graph.nodes.length})</h2>
				<button class="btn btn-primary" onclick={() => startEdit('new')}>Add concept</button>
			</div>

			{#if editingNode !== null}
				<div class="card form">
					<label class="label" for="n-title">Title</label>
					<input id="n-title" class="input" bind:value={nodeForm.title} />
					<label class="label" for="n-obj">Learning objective</label>
					<textarea id="n-obj" class="input" bind:value={nodeForm.learning_objective}></textarea>
					<div class="grid-3">
						<div>
							<label class="label" for="n-diff">Difficulty</label>
							<select id="n-diff" class="input" bind:value={nodeForm.difficulty_tag}>
								<option>beginner</option><option>intermediate</option><option>advanced</option>
							</select>
						</div>
						<div>
							<label class="label" for="n-bloom">Bloom level</label>
							<select id="n-bloom" class="input" bind:value={nodeForm.bloom_level}>
								<option>remember</option><option>understand</option>
								<option>apply</option><option>analyse</option>
							</select>
						</div>
						<div>
							<label class="label" for="n-dur">Duration (min)</label>
							<input
								id="n-dur"
								class="input"
								type="number"
								min="1"
								bind:value={nodeForm.estimated_duration_mins}
							/>
						</div>
					</div>
					<label class="check-label">
						<input type="checkbox" bind:checked={nodeForm.is_root} />
						Root node (entry point, no prerequisites)
					</label>
					<div class="form-actions">
						<button class="btn" onclick={() => (editingNode = null)}>Cancel</button>
						<button
							class="btn btn-primary"
							disabled={!nodeForm.title.trim() || !nodeForm.learning_objective.trim()}
							onclick={saveNode}
						>
							Save
						</button>
					</div>
				</div>
			{/if}

			<div class="node-list">
				{#each graph.nodes as node (node.id)}
					<div class="card node-row">
						<div class="n-info">
							<span class="n-title">
								{node.title}
								{#if node.is_root}<span class="tag tag-accent">root</span>{/if}
							</span>
							<span class="muted n-obj">{node.learning_objective}</span>
							<span class="faint n-meta">
								{node.difficulty_tag} · {node.bloom_level} · {node.estimated_duration_mins} min
							</span>
						</div>
						<div class="n-actions">
							<button class="btn btn-xs" onclick={() => startEdit(node)}>Edit</button>
							<button class="btn btn-xs danger" onclick={() => removeNode(node)}>Delete</button>
						</div>
					</div>
				{/each}
			</div>
		</div>

		<div>
			<h2>Prerequisite edges ({graph.edges.length})</h2>
			<div class="card form">
				<label class="label" for="e-from">Prerequisite (from)</label>
				<select id="e-from" class="input" bind:value={edgeForm.from_concept_id}>
					<option value="">Select...</option>
					{#each graph.nodes as n (n.id)}<option value={n.id}>{n.title}</option>{/each}
				</select>
				<label class="label" for="e-to">Unlocks (to)</label>
				<select id="e-to" class="input" bind:value={edgeForm.to_concept_id}>
					<option value="">Select...</option>
					{#each graph.nodes as n (n.id)}<option value={n.id}>{n.title}</option>{/each}
				</select>
				<label class="label" for="e-type">Type</label>
				<select id="e-type" class="input" bind:value={edgeForm.edge_type}>
					<option value="required">required (hard gate)</option>
					<option value="recommended">recommended (soft nudge)</option>
				</select>
				<button
					class="btn btn-primary save"
					disabled={!edgeForm.from_concept_id || !edgeForm.to_concept_id}
					onclick={addEdge}
				>
					Add edge
				</button>
				<p class="faint hint">Cycles are rejected automatically — the graph stays a DAG.</p>
			</div>

			<div class="edge-list">
				{#each graph.edges as edge (edge.id)}
					<div class="edge-row">
						<span class="e-text">
							{titleOf(edge.from)} <span class="arrow">→</span> {titleOf(edge.to)}
							<span class="tag {edge.type === 'required' ? 'tag-accent' : 'tag-dim'}">{edge.type}</span>
						</span>
						<button class="btn btn-xs danger" onclick={() => removeEdge(edge)}>Remove</button>
					</div>
				{/each}
			</div>
		</div>
	</div>
{/if}

<style>
	.back {
		display: inline-block;
		margin-bottom: 16px;
		color: var(--text-dim);
		font-size: 14px;
	}

	.cols {
		display: grid;
		grid-template-columns: 1.2fr 1fr;
		gap: 24px;
	}

	@media (max-width: 960px) {
		.cols {
			grid-template-columns: 1fr;
		}
	}

	.toolbar {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 14px;
	}

	.toolbar h2 {
		margin: 0;
	}

	.form {
		margin-bottom: 16px;
	}

	.form .label {
		margin-top: 12px;
	}

	.form .label:first-child {
		margin-top: 0;
	}

	.grid-3 {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 12px;
	}

	.check-label {
		display: flex;
		align-items: center;
		gap: 8px;
		margin-top: 14px;
		font-size: 14px;
		color: var(--text-dim);
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 10px;
		margin-top: 16px;
	}

	.save {
		margin-top: 16px;
	}

	.hint {
		font-size: 12.5px;
		margin: 10px 0 0;
	}

	.node-list,
	.edge-list {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-top: 14px;
	}

	.node-row {
		display: flex;
		justify-content: space-between;
		gap: 14px;
		padding: 14px 18px;
	}

	.n-info {
		display: flex;
		flex-direction: column;
		gap: 3px;
	}

	.n-title {
		font-weight: 640;
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.n-obj {
		font-size: 13.5px;
	}

	.n-meta {
		font-size: 12px;
	}

	.n-actions {
		display: flex;
		flex-direction: column;
		gap: 6px;
		flex-shrink: 0;
	}

	.btn-xs {
		padding: 4px 10px;
		font-size: 12.5px;
	}

	.danger {
		color: var(--danger);
	}

	.edge-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		padding: 9px 14px;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		font-size: 13.5px;
	}

	.e-text {
		display: flex;
		align-items: center;
		gap: 7px;
		flex-wrap: wrap;
	}

	.arrow {
		color: var(--text-faint);
	}
</style>
