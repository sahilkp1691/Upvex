<script>
	/** @type {{ visual: Record<string, any> }} */
	let { visual } = $props();

	const W = 560;
	const H = 220;
	const PAD = { t: 28, r: 16, b: 44, l: 48 };

	let type = $derived(visual?.type);
	let title = $derived(visual?.title || '');
	let caption = $derived(visual?.caption || '');

	let barLayout = $derived.by(() => {
		if (type !== 'bar' || !Array.isArray(visual?.bars)) return null;
		const bars = visual.bars;
		const max = Math.max(...bars.map((b) => Number(b.value) || 0), 1);
		const plotW = W - PAD.l - PAD.r;
		const plotH = H - PAD.t - PAD.b;
		const gap = 10;
		const bw = Math.max(12, (plotW - gap * (bars.length - 1)) / bars.length);
		return bars.map((b, i) => {
			const v = Number(b.value) || 0;
			const h = (v / max) * plotH;
			const x = PAD.l + i * (bw + gap);
			const y = PAD.t + plotH - h;
			return { ...b, x, y, w: bw, h, value: v };
		});
	});

	let lineLayout = $derived.by(() => {
		if (type !== 'line' || !Array.isArray(visual?.points)) return null;
		const points = visual.points;
		const vals = points.map((p) => Number(p.value) || 0);
		const max = Math.max(...vals, 1);
		const min = Math.min(...vals, 0);
		const span = max - min || 1;
		const plotW = W - PAD.l - PAD.r;
		const plotH = H - PAD.t - PAD.b;
		const coords = points.map((p, i) => {
			const v = Number(p.value) || 0;
			const x = PAD.l + (points.length === 1 ? plotW / 2 : (i / (points.length - 1)) * plotW);
			const y = PAD.t + plotH - ((v - min) / span) * plotH;
			return { ...p, x, y, value: v };
		});
		const path = coords.map((c, i) => `${i === 0 ? 'M' : 'L'} ${c.x} ${c.y}`).join(' ');
		const area =
			path +
			` L ${coords[coords.length - 1].x} ${PAD.t + plotH}` +
			` L ${coords[0].x} ${PAD.t + plotH} Z`;
		return { coords, path, area, min, max };
	});

	let stackLayout = $derived.by(() => {
		if (type !== 'stack' || !Array.isArray(visual?.segments)) return null;
		const segs = visual.segments;
		const total = segs.reduce((s, g) => s + (Number(g.value) || 0), 0) || 1;
		const colors = ['var(--accent)', 'var(--up)', 'var(--warn)', 'var(--gold)', 'var(--text-dim)'];
		let x = 0;
		return segs.map((g, i) => {
			const v = Number(g.value) || 0;
			const pct = (v / total) * 100;
			const item = { ...g, pct, color: colors[i % colors.length], x };
			x += pct;
			return item;
		});
	});
</script>

{#if visual && type}
	<figure class="lesson-visual" data-type={type}>
		{#if title}
			<figcaption class="v-title">{title}</figcaption>
		{/if}

		{#if type === 'bar' && barLayout}
			<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label={title || 'Bar chart'}>
				{#if visual.y_label}
					<text
						class="axis-label"
						x="14"
						y={H / 2}
						transform="rotate(-90 14 {H / 2})"
						text-anchor="middle">{visual.y_label}</text
					>
				{/if}
				<line
					class="axis"
					x1={PAD.l}
					y1={PAD.t + (H - PAD.t - PAD.b)}
					x2={W - PAD.r}
					y2={PAD.t + (H - PAD.t - PAD.b)}
				/>
				{#each barLayout as b, i (i)}
					<rect class="bar" x={b.x} y={b.y} width={b.w} height={Math.max(b.h, 1)} rx="4">
						<title>{b.label}: {b.value}</title>
					</rect>
					<text class="tick" x={b.x + b.w / 2} y={H - 14} text-anchor="middle">{b.label}</text>
					{#if b.h > 18}
						<text class="val" x={b.x + b.w / 2} y={b.y - 6} text-anchor="middle">{b.value}</text>
					{/if}
				{/each}
			</svg>
		{:else if type === 'line' && lineLayout}
			<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label={title || 'Line chart'}>
				{#if visual.y_label}
					<text
						class="axis-label"
						x="14"
						y={H / 2}
						transform="rotate(-90 14 {H / 2})"
						text-anchor="middle">{visual.y_label}</text
					>
				{/if}
				<line
					class="axis"
					x1={PAD.l}
					y1={PAD.t + (H - PAD.t - PAD.b)}
					x2={W - PAD.r}
					y2={PAD.t + (H - PAD.t - PAD.b)}
				/>
				<path class="area" d={lineLayout.area} />
				<path class="line" d={lineLayout.path} fill="none" />
				{#each lineLayout.coords as c, i (i)}
					<circle class="dot" cx={c.x} cy={c.y} r="4.5">
						<title>{c.label}: {c.value}</title>
					</circle>
					<text class="tick" x={c.x} y={H - 14} text-anchor="middle">{c.label}</text>
				{/each}
			</svg>
		{:else if type === 'flow' && Array.isArray(visual.steps)}
			<div class="flow" role="list">
				{#each visual.steps as step, i (i)}
					{#if i > 0}
						<span class="flow-arrow" aria-hidden="true">
							<svg width="20" height="12" viewBox="0 0 20 12">
								<path d="M0 6 H16 M12 1 L17 6 L12 11" fill="none" stroke="currentColor" stroke-width="1.6" />
							</svg>
						</span>
					{/if}
					<div class="flow-step" role="listitem">
						<span class="flow-label">{step.label}</span>
						{#if step.detail}
							<span class="flow-detail">{step.detail}</span>
						{/if}
					</div>
				{/each}
			</div>
		{:else if type === 'compare' && Array.isArray(visual.columns)}
			<div class="compare" style="--cols: {visual.columns.length}">
				{#each visual.columns as col, i (i)}
					<div class="compare-col">
						<span class="compare-title">{col.title}</span>
						<ul>
							{#each col.items as item, j (j)}
								<li>{item}</li>
							{/each}
						</ul>
					</div>
				{/each}
			</div>
		{:else if type === 'stack' && stackLayout}
			<div class="stack-wrap">
				{#if visual.total_label}
					<span class="stack-total">{visual.total_label}</span>
				{/if}
				<div class="stack-bar" role="img" aria-label={title || 'Stacked composition'}>
					{#each stackLayout as seg, i (i)}
						<span class="stack-seg" style="width: {seg.pct}%; background: {seg.color}" title="{seg.label}: {Math.round(seg.pct)}%">
							{#if seg.pct >= 14}
								<span class="stack-pct">{Math.round(seg.pct)}%</span>
							{/if}
						</span>
					{/each}
				</div>
				<ul class="stack-legend">
					{#each stackLayout as seg, i (i)}
						<li>
							<span class="swatch" style="background: {seg.color}"></span>
							{seg.label}
							<span class="faint">({Math.round(seg.pct)}%)</span>
						</li>
					{/each}
				</ul>
			</div>
		{/if}

		{#if caption}
			<p class="v-caption">{caption}</p>
		{/if}
	</figure>
{/if}

<style>
	.lesson-visual {
		margin: 1.1rem 0 0.35rem;
		padding: 1rem 1.1rem 0.95rem;
		border: 1px solid var(--border);
		border-radius: var(--radius);
		background: var(--bg-elevated);
		animation: visual-in 0.45s ease both;
	}

	@keyframes visual-in {
		from {
			opacity: 0;
			transform: translateY(6px);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}

	.v-title {
		font-family: var(--font-display);
		font-weight: 650;
		font-size: 0.95rem;
		color: var(--text);
		margin: 0 0 0.65rem;
	}

	.v-caption {
		margin: 0.75rem 0 0;
		font-size: 0.88rem;
		line-height: 1.45;
		color: var(--text-dim);
	}

	.chart {
		display: block;
		width: 100%;
		height: auto;
		max-height: 240px;
	}

	.axis {
		stroke: var(--border-strong);
		stroke-width: 1;
	}

	.axis-label {
		fill: var(--text-faint);
		font-size: 11px;
	}

	.bar {
		fill: var(--accent);
		opacity: 0.92;
		transition: opacity 0.15s ease;
	}

	.bar:hover {
		opacity: 1;
	}

	.tick {
		fill: var(--text-dim);
		font-size: 11px;
	}

	.val {
		fill: var(--text-faint);
		font-size: 11px;
	}

	.area {
		fill: var(--accent-soft);
	}

	.line {
		stroke: var(--accent);
		stroke-width: 2.5;
		stroke-linejoin: round;
		stroke-linecap: round;
	}

	.dot {
		fill: var(--accent-bright);
		stroke: var(--bg-elevated);
		stroke-width: 2;
	}

	.flow {
		display: flex;
		flex-wrap: wrap;
		align-items: stretch;
		gap: 0.35rem 0.15rem;
	}

	.flow-step {
		flex: 1 1 120px;
		min-width: 100px;
		padding: 0.7rem 0.75rem;
		border-radius: var(--radius-sm);
		background: var(--accent-soft);
		border: 1px solid color-mix(in srgb, var(--accent) 28%, var(--border));
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.flow-label {
		font-weight: 650;
		font-size: 0.9rem;
		color: var(--text);
	}

	.flow-detail {
		font-size: 0.8rem;
		color: var(--text-dim);
		line-height: 1.35;
	}

	.flow-arrow {
		display: flex;
		align-items: center;
		color: var(--text-faint);
		flex: 0 0 auto;
		padding: 0 0.1rem;
	}

	.compare {
		display: grid;
		grid-template-columns: repeat(var(--cols, 2), minmax(0, 1fr));
		gap: 0.75rem;
	}

	.compare-col {
		padding: 0.75rem 0.85rem;
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		border: 1px solid var(--border);
	}

	.compare-title {
		display: block;
		font-weight: 650;
		font-size: 0.88rem;
		margin-bottom: 0.45rem;
		color: var(--accent-bright);
	}

	.compare-col ul {
		margin: 0;
		padding-left: 1.05rem;
	}

	.compare-col li {
		font-size: 0.86rem;
		color: var(--text-dim);
		margin: 0.28rem 0;
		line-height: 1.4;
	}

	.stack-wrap {
		display: flex;
		flex-direction: column;
		gap: 0.55rem;
	}

	.stack-total {
		font-size: 0.8rem;
		color: var(--text-faint);
		font-weight: 550;
	}

	.stack-bar {
		display: flex;
		height: 36px;
		border-radius: 999px;
		overflow: hidden;
		border: 1px solid var(--border);
		background: var(--bg-card);
	}

	.stack-seg {
		display: flex;
		align-items: center;
		justify-content: center;
		min-width: 0;
		transition: filter 0.15s ease;
	}

	.stack-seg:hover {
		filter: brightness(1.08);
	}

	.stack-pct {
		font-size: 0.72rem;
		font-weight: 650;
		color: var(--accent-fg);
		text-shadow: 0 1px 2px rgba(0, 0, 0, 0.35);
	}

	.stack-legend {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 0.45rem 1rem;
		font-size: 0.82rem;
		color: var(--text-dim);
	}

	.stack-legend li {
		display: inline-flex;
		align-items: center;
		gap: 0.4rem;
	}

	.swatch {
		width: 10px;
		height: 10px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.faint {
		color: var(--text-faint);
	}

	@media (max-width: 560px) {
		.compare {
			grid-template-columns: 1fr;
		}

		.flow-arrow {
			width: 100%;
			justify-content: center;
			transform: rotate(90deg);
			padding: 0.15rem 0;
		}
	}
</style>
