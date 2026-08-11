<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { get, patch } from '$lib/api.js';
	import { layoutDag, DEFAULT_NODE_W as NODE_W, DEFAULT_NODE_H as NODE_H } from '$lib/graphLayout.js';
	import GraphCanvas from '$lib/GraphCanvas.svelte';
	import { pushToast } from '$lib/stores.js';
	import { browser } from '$app/environment';

	const goalId = page.params.goalId;

	let roadmap = $state(null);
	let loading = $state(true);
	let pacingBusy = $state(false);
	let viewMode = $state('auto'); // auto | graph | list
	let previewId = $state(null);
	let celebrateId = $state(null);
	let rootResolved = $state(false);
	let showReaction = $state(false);

	const VIEW_KEY = 'upvex-roadmap-view';

	$effect(() => {
		if (browser) {
			try {
				const stored = localStorage.getItem(VIEW_KEY);
				if (stored === 'graph' || stored === 'list') viewMode = stored;
			} catch {
				/* ignore */
			}
		}
		const params = page.url.searchParams;
		celebrateId = params.get('celebrate');
		rootResolved = params.get('root') === '1';
		if (celebrateId || params.get('fresh') === '1') showReaction = true;
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

	let layout = $derived(roadmap ? layoutDag(roadmap) : null);

	let nextNode = $derived(
		roadmap?.nodes?.find((n) => n.state === 'recommended_next') ??
			roadmap?.nodes?.find((n) => n.state === 'available') ??
			null
	);

	let listNodes = $derived.by(() => {
		if (!roadmap) return [];
		const order = { recommended_next: 0, available: 1, locked: 2, completed: 3, tested_out: 4 };
		return [...roadmap.nodes].sort((a, b) => {
			const d = (order[a.state] ?? 9) - (order[b.state] ?? 9);
			if (d !== 0) return d;
			return a.title.localeCompare(b.title);
		});
	});

	let effectiveMode = $derived.by(() => {
		if (viewMode === 'graph' || viewMode === 'list') return viewMode;
		if (browser && window.matchMedia('(max-width: 720px)').matches) return 'list';
		return 'graph';
	});

	let focus = $derived.by(() => {
		if (!layout || !nextNode) return null;
		const p = layout.pos[nextNode.id];
		if (!p) return null;
		return { x: p.x, y: p.y, w: NODE_W, h: NODE_H };
	});

	let previewNode = $derived(
		previewId && roadmap ? roadmap.nodes.find((n) => n.id === previewId) : null
	);

	function setView(mode) {
		viewMode = mode;
		if (browser) {
			try {
				localStorage.setItem(VIEW_KEY, mode);
			} catch {
				/* ignore */
			}
		}
	}

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

	function dismissReaction() {
		showReaction = false;
		if (browser) {
			const url = new URL(page.url);
			url.searchParams.delete('celebrate');
			url.searchParams.delete('root');
			url.searchParams.delete('fresh');
			history.replaceState({}, '', url.pathname + url.search);
		}
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
		<div class="skeleton-stack" aria-busy="true">
			<div class="skel skel-title"></div>
			<div class="skel skel-line"></div>
			<div class="skel skel-graph"></div>
		</div>
	{:else if roadmap}
		{#if showReaction}
			<div class="reaction" class:root={rootResolved}>
				<div class="reaction-copy">
					{#if !celebrateId}
						<strong>Your personal map is ready.</strong>
						<span>Start with the highlighted concepts — root gaps unlock the most.</span>
					{:else if rootResolved}
						<strong>Root gap closed.</strong>
						<span>Concepts that depended on this just moved closer.</span>
					{:else}
						<strong>Knowledge map updated.</strong>
						<span>Your scores and unlocks refreshed after that quiz.</span>
					{/if}
				</div>
				{#if nextNode}
					<button class="btn btn-primary btn-sm" onclick={() => openConcept(nextNode)}>
						Continue: {nextNode.title}
					</button>
				{/if}
				<button class="btn btn-ghost btn-sm" onclick={dismissReaction}>Dismiss</button>
			</div>
		{/if}

		<div class="top-row">
			<div>
				<h1>{roadmap.topic_name}</h1>
				<p class="muted">
					Skill {Math.round(roadmap.level_score ?? 0)} · close root gaps first — they unlock the
					most of the map.
				</p>
			</div>
			<div class="top-actions">
				{#if nextNode}
					<button class="btn btn-primary continue" onclick={() => openConcept(nextNode)}>
						Continue
						<span class="cont-title">{nextNode.title}</span>
					</button>
				{/if}
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
		</div>

		<div class="toolbar-row">
			<div class="legend">
				<span class="dot next"></span> Up next
				<span class="dot avail"></span> Available
				<span class="dot done"></span> Completed / tested out
				<span class="dot lock"></span> Locked
			</div>
			<div class="view-toggle" role="group" aria-label="Roadmap view">
				<button class="vt" class:active={effectiveMode === 'graph'} onclick={() => setView('graph')}
					>Map</button
				>
				<button class="vt" class:active={effectiveMode === 'list'} onclick={() => setView('list')}
					>List</button
				>
			</div>
		</div>

		{#if effectiveMode === 'list'}
			<div class="list-view">
				{#each listNodes as node (node.id)}
					<button
						class="list-row {node.state}"
						class:celebrate={celebrateId === node.id}
						onclick={() => openConcept(node)}
						onmouseenter={() => (previewId = node.id)}
						onmouseleave={() => (previewId = null)}
					>
						<span class="lr-main">
							<span class="lr-title">{node.title}</span>
							<span class="lr-state">{stateLabels[node.state]}</span>
							{#if node.is_root_gap}<span class="n-gap">root gap</span>{/if}
						</span>
						<span class="lr-meta">
							{#if node.score !== null}<span>{Math.round(node.score)}</span>{/if}
							<span class="faint">{node.estimated_duration_mins} min</span>
						</span>
					</button>
				{/each}
			</div>
		{:else if layout}
			<GraphCanvas width={layout.width} height={layout.height} {focus}>
				<div class="graph" style="width: {layout.width}px; height: {layout.height}px">
					<svg width={layout.width} height={layout.height}>
						{#each layout.paths as p, i (i)}
							{@const toNext = nextNode && p.to === nextNode.id}
							{@const fromCelebrate = celebrateId && p.from === celebrateId}
							<path
								class="edge"
								class:required={p.type === 'required'}
								class:recommended={p.type === 'recommended'}
								class:path-pulse={toNext || fromCelebrate}
								d={p.d}
								fill="none"
							/>
						{/each}
					</svg>
					{#each layout.nodes as node (node.id)}
						{@const p = layout.pos[node.id]}
						<button
							class="node {node.state}"
							class:celebrate={celebrateId === node.id}
							class:preview={previewId === node.id}
							style="left: {p.x}px; top: {p.y}px; width: {NODE_W}px; height: {NODE_H}px"
							onclick={() => openConcept(node)}
							onmouseenter={() => (previewId = node.id)}
							onmouseleave={() => (previewId = null)}
							onfocus={() => (previewId = node.id)}
							onblur={() => (previewId = null)}
						>
							<span class="n-title">{node.title}</span>
							<span class="n-meta">
								<span class="n-state">{stateLabels[node.state]}</span>
								{#if node.is_root_gap}<span class="n-gap">root gap</span>{/if}
								{#if node.score !== null}<span class="n-score">{Math.round(node.score)}</span>{/if}
							</span>
						</button>
					{/each}
				</div>
			</GraphCanvas>

			{#if previewNode}
				<div class="hover-card" role="tooltip">
					<strong>{previewNode.title}</strong>
					<p>{previewNode.learning_objective || 'Open to learn this concept.'}</p>
					<div class="hc-meta">
						<span class="tag tag-dim">{stateLabels[previewNode.state]}</span>
						{#if previewNode.is_root_gap}<span class="tag tag-warn">root gap</span>{/if}
						<span class="faint"
							>{previewNode.estimated_duration_mins} min · {previewNode.difficulty_tag}</span
						>
					</div>
					{#if previewNode.state === 'locked' && previewNode.blocked_by_titles?.length}
						<p class="blocked">Blocked by: {previewNode.blocked_by_titles.join(', ')}</p>
					{/if}
				</div>
			{/if}
		{:else}
			<div class="empty-state">
				<h3>No concepts on this map yet</h3>
				<p class="muted">This topic’s knowledge graph is empty — check back after an admin seeds it.</p>
			</div>
		{/if}
	{/if}
</div>

<style>
	.wide {
		max-width: 1280px;
	}

	.skeleton-stack {
		display: flex;
		flex-direction: column;
		gap: 14px;
		padding-top: 8px;
	}

	.skel {
		border-radius: var(--radius-sm);
		background: linear-gradient(
			90deg,
			var(--bg-card) 0%,
			var(--bg-hover) 45%,
			var(--bg-card) 90%
		);
		background-size: 200% 100%;
		animation: skel-shine 1.2s ease-in-out infinite;
	}

	.skel-title {
		height: 36px;
		width: 42%;
	}

	.skel-line {
		height: 16px;
		width: 64%;
	}

	.skel-graph {
		height: 420px;
		width: 100%;
		border-radius: var(--radius);
	}

	@keyframes skel-shine {
		0% {
			background-position: 100% 0;
		}
		100% {
			background-position: -100% 0;
		}
	}

	.reaction {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 10px 14px;
		margin-bottom: 18px;
		padding: 12px 16px;
		border-radius: var(--radius);
		border: 1px solid color-mix(in srgb, var(--up) 45%, var(--border));
		background: var(--up-soft);
		animation: reaction-in 0.45s ease-out;
	}

	.reaction.root {
		border-color: color-mix(in srgb, var(--gold) 50%, var(--border));
		background: var(--gold-soft);
	}

	.reaction-copy {
		flex: 1;
		min-width: 200px;
		display: flex;
		flex-direction: column;
		gap: 2px;
		font-size: 14px;
		color: var(--text-dim);
	}

	.reaction-copy strong {
		color: var(--text);
		font-size: 14.5px;
	}

	@keyframes reaction-in {
		from {
			opacity: 0;
			transform: translateY(-8px);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}

	.top-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 24px;
		flex-wrap: wrap;
	}

	.top-actions {
		display: flex;
		flex-direction: column;
		align-items: flex-end;
		gap: 12px;
	}

	.continue {
		display: inline-flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 2px;
		padding: 10px 18px;
		line-height: 1.2;
	}

	.cont-title {
		font-size: 12px;
		font-weight: 550;
		opacity: 0.9;
		max-width: 220px;
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
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
		background: var(--up-soft);
		border-color: var(--up);
		color: var(--up);
	}

	.deadline {
		display: block;
		margin-top: 6px;
		font-size: 12.5px;
	}

	.toolbar-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
		margin: 16px 0 10px;
	}

	.legend {
		display: flex;
		align-items: center;
		gap: 8px;
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
		background: var(--up);
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

	.view-toggle {
		display: inline-flex;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.vt {
		padding: 6px 14px;
		border: none;
		background: var(--bg-card);
		color: var(--text-dim);
		font-weight: 600;
		font-size: 13px;
		cursor: pointer;
	}

	.vt.active {
		background: var(--accent-soft);
		color: var(--accent-bright);
	}

	.graph {
		position: relative;
	}

	svg {
		position: absolute;
		inset: 0;
		pointer-events: none;
	}

	.edge {
		stroke: var(--border);
		stroke-width: 1.5;
	}

	.edge.required {
		stroke: var(--border-strong);
		stroke-width: 2;
	}

	.edge.recommended {
		stroke-dasharray: 5 5;
	}

	.edge.path-pulse {
		stroke: var(--up);
		stroke-width: 2.4;
		animation: edge-draw 0.9s ease-out;
	}

	@keyframes edge-draw {
		from {
			stroke-opacity: 0.15;
		}
		to {
			stroke-opacity: 1;
		}
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
		z-index: 1;
	}

	.node:hover,
	.node.preview {
		transform: translateY(-2px);
		box-shadow: var(--shadow);
		z-index: 2;
	}

	.node.recommended_next {
		border-color: var(--up);
		box-shadow: 0 0 0 1px var(--up), 0 0 22px color-mix(in srgb, var(--up) 28%, transparent);
		animation: next-pulse 2.2s ease-in-out infinite;
	}

	.node.celebrate {
		animation: celebrate-pop 0.7s ease-out;
		border-color: var(--gold);
		box-shadow: 0 0 0 2px var(--gold);
	}

	@keyframes next-pulse {
		0%,
		100% {
			box-shadow: 0 0 0 1px var(--up), 0 0 16px color-mix(in srgb, var(--up) 22%, transparent);
		}
		50% {
			box-shadow: 0 0 0 2px var(--up), 0 0 28px color-mix(in srgb, var(--up) 38%, transparent);
		}
	}

	@keyframes celebrate-pop {
		0% {
			transform: scale(0.92);
			opacity: 0.6;
		}
		60% {
			transform: scale(1.04);
		}
		100% {
			transform: scale(1);
			opacity: 1;
		}
	}

	.node.completed,
	.node.tested_out {
		border-color: color-mix(in srgb, var(--up) 50%, transparent);
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
		color: var(--up);
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

	.hover-card {
		margin-top: 12px;
		padding: 14px 16px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		background: var(--bg-card);
		animation: reaction-in 0.2s ease-out;
	}

	.hover-card p {
		margin: 6px 0 10px;
		color: var(--text-dim);
		font-size: 14px;
	}

	.hc-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
	}

	.blocked {
		margin: 10px 0 0 !important;
		font-size: 13px !important;
		color: var(--danger) !important;
	}

	.list-view {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-top: 4px;
	}

	.list-row {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		padding: 14px 16px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text);
		text-align: left;
		cursor: pointer;
	}

	.list-row:hover {
		border-color: var(--accent);
	}

	.list-row.recommended_next {
		border-color: var(--up);
		background: var(--up-soft);
	}

	.list-row.locked {
		opacity: 0.55;
		cursor: not-allowed;
	}

	.list-row.celebrate {
		animation: celebrate-pop 0.7s ease-out;
		border-color: var(--gold);
	}

	.lr-main {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 8px 12px;
	}

	.lr-title {
		font-weight: 650;
	}

	.lr-state {
		font-size: 11px;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-faint);
		font-weight: 650;
	}

	.lr-meta {
		display: flex;
		gap: 10px;
		align-items: center;
		font-size: 13px;
		font-weight: 600;
		color: var(--text-dim);
		flex-shrink: 0;
	}

	.empty-state {
		padding: 48px 24px;
		text-align: center;
		border: 1px dashed var(--border);
		border-radius: var(--radius);
		background: var(--bg-elevated);
	}
</style>
