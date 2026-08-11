<script>
	/**
	 * Pan / zoom viewport for knowledge-graph canvases.
	 * Content should be absolutely positioned inside the inner layer at graph coords.
	 */
	let {
		width = 800,
		height = 600,
		minScale = 0.35,
		maxScale = 2.2,
		/** Optional { x, y, w, h } in graph space to center on after mount / change */
		focus = null,
		class: className = '',
		children
	} = $props();

	/** @type {HTMLDivElement | undefined} */
	let viewport = $state();
	let scale = $state(1);
	let tx = $state(0);
	let ty = $state(0);
	let panning = $state(false);
	let spaceDown = $state(false);

	let lastX = 0;
	let lastY = 0;
	let fittedOnce = false;
	let lastFocusKey = '';

	$effect(() => {
		if (!viewport || !width || !height) return;
		if (!fittedOnce) {
			fit();
			fittedOnce = true;
		}
	});

	$effect(() => {
		if (!focus || !viewport) return;
		const key = `${focus.x},${focus.y},${focus.w ?? 0},${focus.h ?? 0}`;
		if (key === lastFocusKey) return;
		lastFocusKey = key;
		centerOn(focus.x, focus.y, focus.w ?? 0, focus.h ?? 0);
	});

	function fit() {
		if (!viewport) return;
		const pad = 48;
		const vw = viewport.clientWidth;
		const vh = viewport.clientHeight;
		const sx = (vw - pad * 2) / Math.max(width, 1);
		const sy = (vh - pad * 2) / Math.max(height, 1);
		scale = Math.min(maxScale, Math.max(minScale, Math.min(sx, sy, 1)));
		tx = (vw - width * scale) / 2;
		ty = (vh - height * scale) / 2;
	}

	function centerOn(x, y, w = 0, h = 0) {
		if (!viewport) return;
		const vw = viewport.clientWidth;
		const vh = viewport.clientHeight;
		const cx = x + w / 2;
		const cy = y + h / 2;
		tx = vw / 2 - cx * scale;
		ty = vh / 2 - cy * scale;
	}

	function clampScale(s) {
		return Math.min(maxScale, Math.max(minScale, s));
	}

	function onWheel(e) {
		e.preventDefault();
		if (!viewport) return;
		const rect = viewport.getBoundingClientRect();
		const mx = e.clientX - rect.left;
		const my = e.clientY - rect.top;
		const before = scale;
		const delta = e.deltaY > 0 ? 0.9 : 1.1;
		scale = clampScale(before * delta);
		// Zoom toward cursor
		tx = mx - ((mx - tx) / before) * scale;
		ty = my - ((my - ty) / before) * scale;
	}

	function onPointerDown(e) {
		if (e.button !== 0 && e.button !== 1) return;
		// Pan with middle button, space+drag, or drag on empty canvas (data-pan)
		const target = e.target;
		const allow =
			e.button === 1 ||
			spaceDown ||
			(target instanceof Element && target.closest('[data-graph-pan]'));
		if (!allow) return;
		panning = true;
		lastX = e.clientX;
		lastY = e.clientY;
		viewport?.setPointerCapture(e.pointerId);
	}

	function onPointerMove(e) {
		if (!panning) return;
		tx += e.clientX - lastX;
		ty += e.clientY - lastY;
		lastX = e.clientX;
		lastY = e.clientY;
	}

	function onPointerUp(e) {
		if (!panning) return;
		panning = false;
		try {
			viewport?.releasePointerCapture(e.pointerId);
		} catch {
			/* ignore */
		}
	}

	function zoomBy(factor) {
		if (!viewport) return;
		const vw = viewport.clientWidth;
		const vh = viewport.clientHeight;
		const mx = vw / 2;
		const my = vh / 2;
		const before = scale;
		scale = clampScale(before * factor);
		tx = mx - ((mx - tx) / before) * scale;
		ty = my - ((my - ty) / before) * scale;
	}

	function onKeyDown(e) {
		if (e.code === 'Space') {
			spaceDown = true;
			e.preventDefault();
		}
		if (e.key === '0' && (e.metaKey || e.ctrlKey)) {
			e.preventDefault();
			fit();
		}
		if ((e.key === '=' || e.key === '+') && (e.metaKey || e.ctrlKey)) {
			e.preventDefault();
			zoomBy(1.15);
		}
		if (e.key === '-' && (e.metaKey || e.ctrlKey)) {
			e.preventDefault();
			zoomBy(1 / 1.15);
		}
	}

	function onKeyUp(e) {
		if (e.code === 'Space') spaceDown = false;
	}
</script>

<svelte:window onkeydown={onKeyDown} onkeyup={onKeyUp} />

<div class="graph-shell {className}">
	<div class="controls" aria-label="Graph controls">
		<button type="button" class="ctrl" title="Zoom out" onclick={() => zoomBy(1 / 1.15)}>−</button>
		<button type="button" class="ctrl" title="Fit to view" onclick={fit}>Fit</button>
		<button type="button" class="ctrl" title="Zoom in" onclick={() => zoomBy(1.15)}>+</button>
		<span class="pct">{Math.round(scale * 100)}%</span>
	</div>

	<div
		class="viewport"
		class:panning
		class:space={spaceDown}
		bind:this={viewport}
		onwheel={onWheel}
		onpointerdown={onPointerDown}
		onpointermove={onPointerMove}
		onpointerup={onPointerUp}
		onpointercancel={onPointerUp}
		role="region"
		aria-label="Knowledge graph canvas"
	>
		<div
			class="world"
			style="width: {width}px; height: {height}px; transform: translate({tx}px, {ty}px) scale({scale})"
		>
			<div class="pan-layer" data-graph-pan></div>
			<div class="graph-content">
				{@render children?.()}
			</div>
		</div>
	</div>
</div>

<style>
	.graph-shell {
		position: relative;
		display: flex;
		flex-direction: column;
		min-height: 0;
		flex: 1;
	}

	.controls {
		position: absolute;
		top: 10px;
		right: 10px;
		z-index: 4;
		display: flex;
		align-items: center;
		gap: 4px;
		padding: 4px;
		border-radius: var(--radius-sm);
		background: color-mix(in srgb, var(--bg-elevated) 92%, transparent);
		border: 1px solid var(--border);
		backdrop-filter: blur(8px);
	}

	.ctrl {
		width: 32px;
		height: 28px;
		border-radius: 6px;
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text);
		font-weight: 700;
		font-size: 15px;
		cursor: pointer;
		line-height: 1;
	}

	.ctrl:hover {
		border-color: var(--accent);
		color: var(--accent-bright);
	}

	.pct {
		min-width: 42px;
		text-align: center;
		font-size: 11.5px;
		font-weight: 650;
		color: var(--text-faint);
		font-variant-numeric: tabular-nums;
	}

	.viewport {
		overflow: hidden;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background:
			radial-gradient(circle, var(--border) 1px, transparent 1px) 0 0 / 26px 26px,
			var(--bg-elevated);
		min-height: 420px;
		height: min(62vh, 640px);
		cursor: default;
		touch-action: none;
		position: relative;
	}

	.viewport.space,
	.viewport.panning {
		cursor: grab;
	}

	.viewport.panning {
		cursor: grabbing;
	}

	.world {
		position: absolute;
		top: 0;
		left: 0;
		transform-origin: 0 0;
		will-change: transform;
	}

	.pan-layer {
		position: absolute;
		inset: 0;
		z-index: 0;
	}

	.world :global(.graph-content) {
		position: relative;
		z-index: 1;
		width: 100%;
		height: 100%;
	}
</style>
