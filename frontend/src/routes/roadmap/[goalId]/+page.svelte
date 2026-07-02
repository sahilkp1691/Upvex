<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { get, patch } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	const goalId = page.params.goalId;

	let roadmap = $state(null);
	let loading = $state(true);
	let pacingBusy = $state(false);

	const NODE_W = 230;
	const NODE_H = 96;
	const GAP_X = 26;
	const GAP_Y = 70;

	$effect(() => {
		load();
	});

	async function load() {
		try {
			roadmap = await get(`/roadmap/${goalId}`);
		} catch (err) {
			pushToast('Could not load roadmap', err.message, 'error');
			goto('/topics');
		} finally {
			loading = false;
		}
	}

	/** Longest-path layering: layer(n) = 1 + max(layer of prerequisites). */
	let layout = $derived.by(() => {
		if (!roadmap) return null;
		const nodes = roadmap.nodes;
		const preds = {};
		for (const e of roadmap.edges) (preds[e.to] ??= []).push(e.from);

		const layerOf = {};
		const resolve = (id, seen = new Set()) => {
			if (layerOf[id] !== undefined) return layerOf[id];
			if (seen.has(id)) return 0; // defensive: cycles shouldn't exist
			seen.add(id);
			const ps = preds[id] || [];
			const layer = ps.length ? 1 + Math.max(...ps.map((p) => resolve(p, seen))) : 0;
			layerOf[id] = layer;
			return layer;
		};
		nodes.forEach((n) => resolve(n.id));

		const layers = [];
		for (const n of nodes) (layers[layerOf[n.id]] ??= []).push(n);
		layers.forEach((l) => l.sort((a, b) => a.title.localeCompare(b.title)));

		const maxPerLayer = Math.max(...layers.map((l) => l.length));
		const width = maxPerLayer * (NODE_W + GAP_X) + GAP_X;
		const height = layers.length * (NODE_H + GAP_Y) + GAP_Y;

		const pos = {};
		layers.forEach((layerNodes, li) => {
			const rowWidth = layerNodes.length * (NODE_W + GAP_X) - GAP_X;
			const startX = (width - rowWidth) / 2;
			layerNodes.forEach((n, i) => {
				pos[n.id] = {
					x: startX + i * (NODE_W + GAP_X),
					y: GAP_Y / 2 + li * (NODE_H + GAP_Y)
				};
			});
		});

		const paths = roadmap.edges
			.filter((e) => pos[e.from] && pos[e.to])
			.map((e) => {
				const a = pos[e.from];
				const b = pos[e.to];
				const x1 = a.x + NODE_W / 2;
				const y1 = a.y + NODE_H;
				const x2 = b.x + NODE_W / 2;
				const y2 = b.y;
				const my = (y1 + y2) / 2;
				return {
					d: `M ${x1} ${y1} C ${x1} ${my}, ${x2} ${my}, ${x2} ${y2}`,
					type: e.type
				};
			});

		return { pos, paths, width, height, nodes };
	});

	async function setPacing(choice) {
		pacingBusy = true;
		try {
			const updated = await patch(`/goals/${goalId}/pacing`, { pacing_choice: choice });
			roadmap = { ...roadmap, pacing_choice: updated.pacing_choice, target_deadline: updated.target_deadline };
			pushToast('Pacing updated', updated.target_deadline ? `Target: ${updated.target_deadline}` : '', 'info');
		} catch (err) {
			pushToast('Pacing update failed', err.message, 'error');
		} finally {
			pacingBusy = false;
		}
	}

	function openConcept(node) {
		if (node.state === 'locked') {
			pushToast('Locked', `Finish first: ${node.blocked_by_titles.join(', ')}`, 'error');
			return;
		}
		goto(`/lesson/${goalId}/${node.id}`);
	}

	const stateLabels = {
		recommended_next: 'Up next',
		available: 'Available',
		locked: 'Locked',
		tested_out: 'Tested out',
		completed: 'Completed'
	};
</script>

<svelte:head><title>{roadmap ? roadmap.topic_name : 'Roadmap'} — Upvex</title></svelte:head>

<div class="page wide">
	{#if loading}
		<p class="faint">Loading your roadmap...</p>
	{:else if roadmap}
		<div class="top-row">
			<div>
				<h1>{roadmap.topic_name}</h1>
				<p class="muted">
					Level {Math.round(roadmap.level_score ?? 0)} · pick any unlocked concept — root gaps
					marked first unlock the most.
				</p>
			</div>
			<div class="pacing">
				<span class="label">Pacing</span>
				<div class="pace-btns">
					{#each ['casual', 'regular', 'intense'] as p (p)}
						<button
							class="pace"
							class:active={roadmap.pacing_choice === p}
							disabled={pacingBusy}
							onclick={() => setPacing(p)}
						>
							{p}
						</button>
					{/each}
				</div>
				{#if roadmap.target_deadline}
					<span class="faint deadline">Target: {roadmap.target_deadline}</span>
				{/if}
			</div>
		</div>

		<div class="legend">
			<span class="dot next"></span> Up next
			<span class="dot avail"></span> Available
			<span class="dot done"></span> Completed / tested out
			<span class="dot lock"></span> Locked
		</div>

		{#if layout}
			<div class="graph-scroll">
				<div class="graph" style="width: {layout.width}px; height: {layout.height}px">
					<svg width={layout.width} height={layout.height}>
						{#each layout.paths as p, i (i)}
							<path
								d={p.d}
								fill="none"
								stroke={p.type === 'required' ? 'var(--border-strong)' : 'var(--border)'}
								stroke-width="1.6"
								stroke-dasharray={p.type === 'recommended' ? '5 5' : 'none'}
							/>
						{/each}
					</svg>
					{#each layout.nodes as node (node.id)}
						{@const p = layout.pos[node.id]}
						<button
							class="node {node.state}"
							style="left: {p.x}px; top: {p.y}px; width: {NODE_W}px; height: {NODE_H}px"
							onclick={() => openConcept(node)}
						>
							<span class="n-title">{node.title}</span>
							<span class="n-meta">
								<span class="n-state">{stateLabels[node.state]}</span>
								{#if node.is_root_gap}<span class="n-gap">root gap</span>{/if}
								{#if node.score !== null}<span class="n-score">{Math.round(node.score)}</span>{/if}
							</span>
							<span class="n-dur">{node.estimated_duration_mins} min · {node.difficulty_tag}</span>
						</button>
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.wide {
		max-width: 1280px;
	}

	.top-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 24px;
		flex-wrap: wrap;
	}

	.pacing {
		text-align: right;
	}

	.pace-btns {
		display: flex;
		gap: 6px;
	}

	.pace {
		padding: 7px 15px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-card);
		color: var(--text-dim);
		cursor: pointer;
		text-transform: capitalize;
		font-weight: 550;
	}

	.pace.active {
		background: var(--accent-soft);
		border-color: var(--accent);
		color: var(--accent-bright);
	}

	.deadline {
		display: block;
		margin-top: 6px;
		font-size: 12.5px;
	}

	.legend {
		display: flex;
		align-items: center;
		gap: 8px;
		margin: 16px 0 10px;
		color: var(--text-dim);
		font-size: 13px;
		flex-wrap: wrap;
	}

	.legend .dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		margin-left: 14px;
	}

	.legend .dot:first-child {
		margin-left: 0;
	}

	.dot.next {
		background: var(--accent);
	}

	.dot.avail {
		background: var(--text-faint);
	}

	.dot.done {
		background: var(--up);
	}

	.dot.lock {
		background: var(--border-strong);
	}

	.graph-scroll {
		overflow: auto;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background:
			radial-gradient(circle, var(--border) 1px, transparent 1px) 0 0 / 26px 26px,
			var(--bg-elevated);
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

	.node {
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
			transform 0.1s,
			box-shadow 0.12s;
	}

	.node:hover {
		transform: translateY(-2px);
		box-shadow: 0 6px 20px rgba(0, 0, 0, 0.35);
	}

	.node.recommended_next {
		border-color: var(--accent);
		box-shadow: 0 0 0 1px var(--accent), 0 0 22px rgba(79, 124, 255, 0.25);
	}

	.node.completed,
	.node.tested_out {
		border-color: rgba(52, 211, 153, 0.5);
		opacity: 0.82;
	}

	.node.locked {
		opacity: 0.45;
		cursor: not-allowed;
	}

	.n-title {
		font-weight: 640;
		font-size: 14px;
		line-height: 1.25;
	}

	.n-meta {
		display: flex;
		gap: 8px;
		align-items: center;
		font-size: 11.5px;
	}

	.n-state {
		color: var(--text-dim);
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-weight: 650;
		font-size: 10.5px;
	}

	.node.recommended_next .n-state {
		color: var(--accent-bright);
	}

	.node.completed .n-state,
	.node.tested_out .n-state {
		color: var(--up);
	}

	.n-gap {
		color: var(--warn);
		font-weight: 650;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		font-size: 10.5px;
	}

	.n-score {
		color: var(--text-faint);
		font-weight: 600;
	}

	.n-dur {
		color: var(--text-faint);
		font-size: 11.5px;
	}
</style>
