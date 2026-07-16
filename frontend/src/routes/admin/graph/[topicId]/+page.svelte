<script>
	import { page } from '$app/state';
	import { get, post, patch, del } from '$lib/api.js';
	import { layoutDag, DEFAULT_NODE_W as NODE_W, DEFAULT_NODE_H as NODE_H } from '$lib/graphLayout.js';
	import { pushToast } from '$lib/stores.js';

	const topicId = page.params.topicId;

	let graph = $state(null);
	let loading = $state(true);
	let saving = $state(false);

	/** @type {null | 'idle' | 'node' | 'edge' | 'new'} */
	let panelMode = $state('idle');
	let selectedNodeId = $state(null);
	let selectedEdgeId = $state(null);

	let nodeForm = $state(blankNode());
	let edgeType = $state('required');

	let linkMode = $state(false);
	let linkFromId = $state(null);

	let search = $state('');

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

	let layout = $derived(graph ? layoutDag(graph) : null);

	let filteredNodes = $derived.by(() => {
		if (!graph) return [];
		const q = search.trim().toLowerCase();
		if (!q) return graph.nodes;
		return graph.nodes.filter(
			(n) =>
				n.title.toLowerCase().includes(q) ||
				(n.learning_objective || '').toLowerCase().includes(q)
		);
	});

	function titleOf(id) {
		return graph?.nodes.find((n) => n.id === id)?.title ?? id;
	}

	function clearSelection() {
		panelMode = 'idle';
		selectedNodeId = null;
		selectedEdgeId = null;
		linkFromId = null;
		nodeForm = blankNode();
	}

	function selectNode(node) {
		if (linkMode) {
			handleLinkClick(node.id);
			return;
		}
		selectedNodeId = node.id;
		selectedEdgeId = null;
		panelMode = 'node';
		nodeForm = { ...node };
	}

	function selectEdge(edgePath) {
		if (linkMode) return;
		const edge = graph.edges.find((e) => e.id === edgePath.id);
		if (!edge) return;
		selectedEdgeId = edge.id;
		selectedNodeId = null;
		panelMode = 'edge';
		edgeType = edge.type;
	}

	function startNew() {
		linkMode = false;
		linkFromId = null;
		selectedNodeId = null;
		selectedEdgeId = null;
		panelMode = 'new';
		nodeForm = blankNode();
	}

	function toggleLinkMode() {
		linkMode = !linkMode;
		linkFromId = null;
		if (linkMode) {
			panelMode = 'idle';
			selectedNodeId = null;
			selectedEdgeId = null;
		}
	}

	async function handleLinkClick(nodeId) {
		if (!linkFromId) {
			linkFromId = nodeId;
			pushToast('Link start', 'Now click the concept this unlocks', 'info');
			return;
		}
		if (linkFromId === nodeId) {
			linkFromId = null;
			return;
		}
		saving = true;
		try {
			await post(`/admin/topics/${topicId}/edges`, {
				from_concept_id: linkFromId,
				to_concept_id: nodeId,
				edge_type: 'required'
			});
			pushToast('Prerequisite linked', `${titleOf(linkFromId)} → ${titleOf(nodeId)}`);
			linkFromId = null;
			await load();
		} catch (err) {
			pushToast('Edge rejected', err.message, 'error');
			linkFromId = null;
		} finally {
			saving = false;
		}
	}

	async function saveNode() {
		saving = true;
		try {
			if (panelMode === 'new') {
				const res = await post(`/admin/topics/${topicId}/nodes`, nodeForm);
				pushToast('Concept created', nodeForm.title);
				await load();
				selectedNodeId = res.id;
				selectedEdgeId = null;
				panelMode = 'node';
				const created = graph?.nodes.find((n) => n.id === res.id);
				if (created) nodeForm = { ...created };
				else nodeForm = blankNode();
			} else {
				const { id, ...body } = nodeForm;
				await patch(`/admin/nodes/${id}`, body);
				pushToast('Concept updated', nodeForm.title);
				await load();
				const updated = graph.nodes.find((n) => n.id === id);
				if (updated) selectNode(updated);
			}
		} catch (err) {
			pushToast('Save failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	async function removeNode() {
		const node = graph.nodes.find((n) => n.id === selectedNodeId);
		if (!node) return;
		if (!confirm(`Delete "${node.title}" and all its edges?`)) return;
		saving = true;
		try {
			await del(`/admin/nodes/${node.id}`);
			pushToast('Concept deleted', node.title);
			clearSelection();
			await load();
		} catch (err) {
			pushToast('Delete failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	async function saveEdgeType() {
		if (!selectedEdgeId) return;
		saving = true;
		try {
			await patch(`/admin/edges/${selectedEdgeId}`, { edge_type: edgeType });
			pushToast('Edge updated', edgeType);
			await load();
		} catch (err) {
			pushToast('Update failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	async function removeEdge() {
		if (!selectedEdgeId) return;
		saving = true;
		try {
			await del(`/admin/edges/${selectedEdgeId}`);
			pushToast('Edge removed');
			clearSelection();
			await load();
		} catch (err) {
			pushToast('Delete failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	let selectedEdge = $derived(
		selectedEdgeId && graph ? graph.edges.find((e) => e.id === selectedEdgeId) : null
	);

	function nodeClass(node) {
		const classes = ['g-node'];
		if (selectedNodeId === node.id) classes.push('selected');
		if (linkFromId === node.id) classes.push('link-from');
		if (linkMode && selectedNodeId !== node.id && linkFromId !== node.id) classes.push('linkable');
		if (panelMode !== 'idle' && selectedNodeId && selectedNodeId !== node.id && !linkMode) {
			classes.push('dim');
		}
		if (node.is_root) classes.push('root');
		return classes.join(' ');
	}
</script>

<svelte:head>
	<title>{graph?.topic_name ? `${graph.topic_name} graph` : 'Graph editor'} — Upvex</title>
</svelte:head>

<a href="/admin/topics" class="back">Back to topics</a>

{#if loading}
	<p class="faint">Loading graph...</p>
{:else if graph}
	<header class="page-head">
		<div>
			<h1>{graph.topic_name}</h1>
			<p class="muted">
				{graph.nodes.length} concepts · {graph.edges.length} prerequisites
			</p>
		</div>
		<div class="toolbar">
			<input
				class="input search"
				type="search"
				placeholder="Find concept..."
				bind:value={search}
			/>
			<button class="btn" class:active={linkMode} onclick={toggleLinkMode}>
				{linkMode ? 'Cancel linking' : 'Link prerequisites'}
			</button>
			<button class="btn btn-primary" onclick={startNew}>Add concept</button>
		</div>
	</header>

	{#if linkMode}
		<p class="link-hint">
			{#if linkFromId}
				Linking from <strong>{titleOf(linkFromId)}</strong> — click the concept it unlocks.
			{:else}
				Click a prerequisite concept, then the concept it unlocks. Cycles are rejected automatically.
			{/if}
		</p>
	{/if}

	{#if search.trim() && filteredNodes.length}
		<div class="jump-list">
			{#each filteredNodes.slice(0, 8) as n (n.id)}
				<button class="jump" onclick={() => selectNode(n)}>{n.title}</button>
			{/each}
		</div>
	{/if}

	<div class="editor">
		<div class="canvas-pane">
			{#if layout && graph.nodes.length}
				<div class="graph-scroll">
					<div class="graph" style="width: {layout.width}px; height: {layout.height}px">
						<svg width={layout.width} height={layout.height}>
							{#each layout.paths as p (p.id ?? `${p.from}-${p.to}`)}
								<path
									class="edge-path"
									class:selected={selectedEdgeId === p.id}
									class:dim={selectedEdgeId && selectedEdgeId !== p.id}
									d={p.d}
									fill="none"
									stroke={p.type === 'required' ? 'var(--border-strong)' : 'var(--border)'}
									stroke-width={selectedEdgeId === p.id ? 2.8 : 1.8}
									stroke-dasharray={p.type === 'recommended' ? '5 5' : 'none'}
									role="button"
									tabindex="0"
									onclick={() => selectEdge(p)}
									onkeydown={(e) => e.key === 'Enter' && selectEdge(p)}
								/>
							{/each}
						</svg>
						{#each layout.nodes as node (node.id)}
							{@const p = layout.pos[node.id]}
							<button
								class={nodeClass(node)}
								style="left: {p.x}px; top: {p.y}px; width: {NODE_W}px; height: {NODE_H}px"
								onclick={() => selectNode(node)}
							>
								<span class="n-title">
									{node.title}
									{#if node.is_root}<span class="tag tag-accent">root</span>{/if}
								</span>
								<span class="n-meta">
									{node.difficulty_tag} · {node.bloom_level} · {node.estimated_duration_mins} min
								</span>
							</button>
						{/each}
					</div>
				</div>
			{:else}
				<div class="empty-canvas card">
					<p>No concepts yet. Add a concept to start building this topic's graph.</p>
					<button class="btn btn-primary" onclick={startNew}>Add concept</button>
				</div>
			{/if}
		</div>

		<aside class="side-panel card">
			{#if panelMode === 'idle'}
				<h2>Edit graph</h2>
				<p class="muted help">
					Click a concept to edit it. Click an edge to change its type or remove it. Use
					<strong>Link prerequisites</strong> to connect concepts on the canvas.
				</p>
				<ul class="tips">
					<li>Required edges are solid; recommended edges are dashed.</li>
					<li>Root concepts are entry points with no hard prerequisites.</li>
					<li>The graph must stay a DAG — cycles are blocked.</li>
				</ul>
			{:else if panelMode === 'new' || panelMode === 'node'}
				<div class="panel-head">
					<h2>{panelMode === 'new' ? 'New concept' : 'Edit concept'}</h2>
					<button class="btn btn-xs" onclick={clearSelection}>Close</button>
				</div>

				<label class="label" for="n-title">Title</label>
				<input id="n-title" class="input" bind:value={nodeForm.title} />

				<label class="label" for="n-obj">Learning objective</label>
				<textarea id="n-obj" class="input" rows="4" bind:value={nodeForm.learning_objective}></textarea>

				<div class="grid-2">
					<div>
						<label class="label" for="n-diff">Difficulty</label>
						<select id="n-diff" class="input" bind:value={nodeForm.difficulty_tag}>
							<option>beginner</option>
							<option>intermediate</option>
							<option>advanced</option>
						</select>
					</div>
					<div>
						<label class="label" for="n-bloom">Bloom level</label>
						<select id="n-bloom" class="input" bind:value={nodeForm.bloom_level}>
							<option>remember</option>
							<option>understand</option>
							<option>apply</option>
							<option>analyse</option>
						</select>
					</div>
				</div>

				<label class="label" for="n-dur">Duration (min)</label>
				<input
					id="n-dur"
					class="input"
					type="number"
					min="1"
					bind:value={nodeForm.estimated_duration_mins}
				/>

				<label class="check-label">
					<input type="checkbox" bind:checked={nodeForm.is_root} />
					Root node (entry point)
				</label>

				<div class="form-actions">
					{#if panelMode === 'node'}
						<button class="btn danger" disabled={saving} onclick={removeNode}>Delete</button>
					{/if}
					<button
						class="btn btn-primary"
						disabled={saving || !nodeForm.title.trim() || !nodeForm.learning_objective.trim()}
						onclick={saveNode}
					>
						{saving ? 'Saving...' : 'Save'}
					</button>
				</div>
			{:else if panelMode === 'edge' && selectedEdge}
				<div class="panel-head">
					<h2>Edit edge</h2>
					<button class="btn btn-xs" onclick={clearSelection}>Close</button>
				</div>
				<p class="edge-summary">
					<strong>{titleOf(selectedEdge.from)}</strong>
					<span class="arrow">→</span>
					<strong>{titleOf(selectedEdge.to)}</strong>
				</p>

				<label class="label" for="e-type">Type</label>
				<select id="e-type" class="input" bind:value={edgeType}>
					<option value="required">required (hard gate)</option>
					<option value="recommended">recommended (soft nudge)</option>
				</select>

				<div class="form-actions">
					<button class="btn danger" disabled={saving} onclick={removeEdge}>Remove</button>
					<button
						class="btn btn-primary"
						disabled={saving || edgeType === selectedEdge.type}
						onclick={saveEdgeType}
					>
						{saving ? 'Saving...' : 'Save type'}
					</button>
				</div>
			{/if}
		</aside>
	</div>
{/if}

<style>
	.back {
		display: inline-block;
		margin-bottom: 14px;
		color: var(--text-dim);
		font-size: 14px;
	}

	.page-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
		margin-bottom: 12px;
	}

	.page-head h1 {
		margin: 0 0 4px;
		font-size: 1.55rem;
	}

	.toolbar {
		display: flex;
		gap: 8px;
		align-items: center;
		flex-wrap: wrap;
	}

	.search {
		min-width: 180px;
		width: 200px;
	}

	.btn.active {
		border-color: var(--accent);
		background: var(--accent-soft);
		color: var(--accent-bright);
	}

	.link-hint {
		margin: 0 0 10px;
		padding: 10px 14px;
		border-radius: var(--radius-sm);
		background: var(--accent-soft);
		border: 1px solid var(--accent);
		color: var(--text-dim);
		font-size: 13.5px;
	}

	.jump-list {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 10px;
	}

	.jump {
		padding: 5px 10px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text-dim);
		font-size: 12.5px;
		cursor: pointer;
	}

	.jump:hover {
		border-color: var(--accent);
		color: var(--text);
	}

	.editor {
		display: grid;
		grid-template-columns: 1fr min(340px, 36vw);
		gap: 16px;
		align-items: start;
		min-height: 520px;
	}

	@media (max-width: 960px) {
		.editor {
			grid-template-columns: 1fr;
		}
	}

	.canvas-pane {
		min-width: 0;
	}

	.graph-scroll {
		overflow: auto;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background:
			radial-gradient(circle, var(--border) 1px, transparent 1px) 0 0 / 26px 26px,
			var(--bg-elevated);
		min-height: 480px;
		max-height: calc(100vh - 220px);
	}

	.graph {
		position: relative;
		margin: 0 auto;
	}

	svg {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.edge-path {
		pointer-events: stroke;
		cursor: pointer;
	}

	.edge-path.selected {
		stroke: var(--accent) !important;
	}

	.edge-path.dim {
		opacity: 0.35;
	}

	.g-node {
		position: absolute;
		display: flex;
		flex-direction: column;
		justify-content: center;
		gap: 4px;
		padding: 10px 14px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-card);
		color: var(--text);
		text-align: left;
		cursor: pointer;
		transition:
			border-color 0.12s,
			opacity 0.12s,
			box-shadow 0.12s,
			transform 0.1s;
	}

	.g-node:hover {
		transform: translateY(-1px);
		border-color: var(--accent);
	}

	.g-node.selected {
		border-color: var(--accent);
		box-shadow: 0 0 0 1px var(--accent), 0 0 18px rgba(79, 124, 255, 0.22);
		z-index: 2;
	}

	.g-node.link-from {
		border-color: var(--up);
		box-shadow: 0 0 0 1px var(--up);
	}

	.g-node.linkable:hover {
		border-color: var(--up);
	}

	.g-node.dim {
		opacity: 0.45;
	}

	.g-node.root {
		border-color: rgba(79, 124, 255, 0.55);
	}

	.n-title {
		font-weight: 640;
		font-size: 13.5px;
		line-height: 1.25;
		display: flex;
		align-items: center;
		gap: 6px;
		flex-wrap: wrap;
	}

	.n-meta {
		font-size: 11.5px;
		color: var(--text-faint);
	}

	.empty-canvas {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 12px;
		padding: 28px;
		min-height: 280px;
		justify-content: center;
	}

	.side-panel {
		position: sticky;
		top: 16px;
		padding: 18px;
		display: flex;
		flex-direction: column;
		gap: 0;
		max-height: calc(100vh - 120px);
		overflow: auto;
	}

	.side-panel h2 {
		margin: 0 0 8px;
		font-size: 1.1rem;
	}

	.help {
		font-size: 13.5px;
		line-height: 1.45;
		margin: 0 0 12px;
	}

	.tips {
		margin: 0;
		padding-left: 18px;
		color: var(--text-dim);
		font-size: 13px;
		line-height: 1.5;
	}

	.panel-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 8px;
		margin-bottom: 8px;
	}

	.panel-head h2 {
		margin: 0;
	}

	.label {
		margin-top: 12px;
	}

	.grid-2 {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 10px;
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
		margin-top: 18px;
	}

	.btn-xs {
		padding: 4px 10px;
		font-size: 12.5px;
	}

	.danger {
		color: var(--danger);
		margin-right: auto;
	}

	.edge-summary {
		display: flex;
		align-items: center;
		gap: 8px;
		flex-wrap: wrap;
		font-size: 14px;
		margin: 4px 0 8px;
	}

	.arrow {
		color: var(--text-faint);
	}
</style>
