<script>
	import { goto } from '$app/navigation';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	$effect(() => {
		if ($userLoaded && $currentUser) {
			goto($currentUser.onboarded ? '/topics' : '/onboarding');
		}
	});

	const steps = [
		{
			n: '01',
			title: 'Diagnose',
			body: 'An adaptive quiz branches on every answer and tags each question to a concept node, not just a topic.'
		},
		{
			n: '02',
			title: 'Trace the root',
			body: 'A recursive walk up the prerequisite graph finds the upstream concept actually causing the gap.'
		},
		{
			n: '03',
			title: 'Generate the lesson',
			body: 'Content is assembled live against your skill, gaps, learning style, and tone — then cached for reuse.'
		},
		{
			n: '04',
			title: 'Climb with momentum',
			body: 'XP, streaks, levels, and badges mark checkpoints that matter, like resolving a root gap.'
		}
	];

	const pillars = [
		{
			n: '01',
			title: 'Real diagnosis',
			body: 'An adaptive quiz maps skill per concept, then traces weaknesses upstream to the foundation.',
			icon: 'diagnose'
		},
		{
			n: '02',
			title: 'Lessons for you',
			body: 'Content is generated against your profile — skill, gaps, style, tone — not a static course for everyone.',
			icon: 'lesson'
		},
		{
			n: '03',
			title: 'Momentum that sticks',
			body: 'XP, streaks, levels, and badges for checkpoints that matter, like resolving a root gap.',
			icon: 'momentum'
		}
	];

	const useCases = [
		{
			href: '/solutions#teams',
			label: 'Teams & companies',
			body: 'Diagnose real skill gaps across engineers and data teams before they become incidents.'
		},
		{
			href: '/solutions#schools',
			label: 'Schools & nonprofits',
			body: 'Trace students back to the exact earlier concept that never stuck, with sponsored access options.'
		},
		{
			href: '/solutions#individuals',
			label: 'Individual learners',
			body: 'Skip what you already know. Spend time only on the concept actually blocking your progress.'
		}
	];

	const stats = [
		{ k: '2', v: 'full tracks live — SQL & Spark' },
		{ k: '60+', v: 'diagnostic questions seeded' },
		{ k: '100%', v: 'lessons generated per profile' },
		{ k: '1', v: 'prerequisite graph behind it all' }
	];
</script>

<svelte:head>
	<title>Upvex — learning that points up</title>
	<meta
		name="description"
		content="Upvex diagnoses what you actually know, traces weaknesses to the root, and generates the exact lesson you need next."
	/>
</svelte:head>

<div class="mkt landing">
	<div class="grain" aria-hidden="true"></div>
	<MarketingNav />

	<section class="hero">
		<div class="hero-copy" use:reveal data-reveal>
			<p class="eyebrow"><span class="br">[</span>01 // Diagnostic engine<span class="br">]</span></p>
			<h1>
				Skills on an<br />
				<span class="stamp">upward vector.</span>
			</h1>
			<p class="sub">
				Diagnose what you actually know, trace weaknesses to the root, then climb a graph of
				lessons generated for you — not a static course built for everyone.
			</p>
			<div class="cta-row">
				<a href="/auth" class="mkt-btn">Start learning</a>
				<a href="#how-it-works" class="mkt-link">See how it works <span class="arrow">&darr;</span></a>
			</div>
		</div>

		<div class="hero-visual" use:reveal={{ delay: 120 }} data-reveal aria-hidden="true">
			<span class="v-label v-label-top">TRAJECTORY</span>
			<svg class="ascend" viewBox="0 0 460 320" fill="none" preserveAspectRatio="xMidYMid meet">
				<defs>
					<pattern id="grid" width="23" height="23" patternUnits="userSpaceOnUse">
						<path d="M0 23 L0 0 L23 0" class="grid-line" />
					</pattern>
				</defs>
				<rect x="0" y="0" width="460" height="280" fill="url(#grid)" />
				<line x1="20" y1="270" x2="440" y2="270" class="axis" />
				<path
					class="ascend-line"
					d="M20 250 C 100 245, 140 200, 190 190 S 280 130, 330 95 S 400 45, 430 30"
				/>
				<circle class="pt done" cx="20" cy="250" r="5" />
				<circle class="pt done" cx="190" cy="190" r="5" />
				<circle class="pt gap" cx="330" cy="95" r="6" />
				<circle class="pt next" cx="430" cy="30" r="8" />
				<text x="20" y="292" class="tick-lbl">T0</text>
				<text x="190" y="292" class="tick-lbl">T1</text>
				<text x="330" y="292" class="tick-lbl">T2</text>
				<text x="418" y="292" class="tick-lbl">T3</text>
			</svg>
			<div class="tag tag-gap-lbl">ROOT GAP FOUND</div>
			<div class="tag tag-next-lbl">MASTERY</div>
			<div class="stamp-badge">TRAJECTORY&nbsp;LOCKED</div>
		</div>
	</section>

	<section class="stats" use:reveal data-reveal>
		{#each stats as s, i (s.v)}
			<div class="stat">
				<span class="stat-idx">{String(i + 1).padStart(2, '0')}</span>
				<span class="stat-k">{s.k}</span>
				<span class="stat-v">{s.v}</span>
			</div>
		{/each}
	</section>

	<section class="how" id="how-it-works">
		<p class="section-eyebrow" use:reveal data-reveal><span class="br">[</span>02 // How it works<span class="br">]</span></p>
		<h2 use:reveal={{ delay: 40 }} data-reveal>From guesswork to a graph you can climb.</h2>
		<div class="steps">
			{#each steps as s, i (s.n)}
				<div class="step" style="--i: {i}" use:reveal={{ delay: i * 90 }} data-reveal>
					<span class="ghost-num" aria-hidden="true">{s.n}</span>
					<span class="step-n">{s.n}</span>
					<h3>{s.title}</h3>
					<p>{s.body}</p>
				</div>
			{/each}
		</div>
	</section>

	<section class="pillars" id="product">
		<p class="section-eyebrow" use:reveal data-reveal><span class="br">[</span>03 // What&rsquo;s inside<span class="br">]</span></p>
		<h2 use:reveal={{ delay: 40 }} data-reveal>Built as a real diagnostic system, not a quiz app.</h2>
		<div class="pillar-grid">
			{#each pillars as p, i (p.n)}
				<article class="pillar bracket-card" style="--i: {i}" use:reveal={{ delay: i * 90 }} data-reveal>
					<div class="pillar-icon" aria-hidden="true">
						{#if p.icon === 'diagnose'}
							<svg viewBox="0 0 32 32" fill="none">
								<circle cx="9" cy="16" r="4" />
								<circle cx="22" cy="9" r="4" />
								<circle cx="22" cy="23" r="4" />
								<path d="M13 16h4M18.5 11.5l-4.5 3M18.5 20.5l-4.5-3" />
							</svg>
						{:else if p.icon === 'lesson'}
							<svg viewBox="0 0 32 32" fill="none">
								<path d="M8 23 V12 h6 v11 M18 23 V8 h6 v15" />
							</svg>
						{:else}
							<svg viewBox="0 0 32 32" fill="none">
								<path d="M8 21 L16 8 L24 21 L16 17 Z" />
							</svg>
						{/if}
					</div>
					<span class="p-num">{p.n}</span>
					<h3>{p.title}</h3>
					<p>{p.body}</p>
				</article>
			{/each}
		</div>
	</section>

	<section class="usecases" id="use-cases">
		<div class="usecases-head">
			<div>
				<p class="section-eyebrow" use:reveal data-reveal><span class="br">[</span>04 // Who it&rsquo;s for<span class="br">]</span></p>
				<h2 use:reveal={{ delay: 40 }} data-reveal>Built for more than one kind of learner.</h2>
			</div>
			<a href="/solutions" class="mkt-link">See all solutions <span class="arrow">&rarr;</span></a>
		</div>
		<div class="usecase-grid">
			{#each useCases as u, i (u.href)}
				<a class="usecase" href={u.href} use:reveal={{ delay: i * 90 }} data-reveal>
					<span class="usecase-idx">TARGET {String(i + 1).padStart(2, '0')}</span>
					<h3>{u.label}</h3>
					<p>{u.body}</p>
					<span class="usecase-link">Explore <span class="arrow">&rarr;</span></span>
				</a>
			{/each}
		</div>
	</section>

	<section class="quote" use:reveal data-reveal>
		<span class="quote-mark" aria-hidden="true">&ldquo;</span>
		<blockquote>
			Competence should be measured by what you can do next &mdash; not which course you finished.
		</blockquote>
		<p class="quote-attr">&mdash; The Upvex approach</p>
	</section>

	<section class="final-cta" use:reveal data-reveal>
		<div class="final-cta-inner">
			<h2>Start on your vector today.</h2>
			<p>Free adaptive diagnostic. No static syllabus.</p>
			<a href="/auth" class="mkt-btn mkt-btn-dark">Start learning</a>
		</div>
	</section>

	<MarketingFooter />
</div>

<style>
	.mkt {
		--mkt-signal: var(--warn);
		--mkt-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace;
		--mkt-display: 'Fraunces', Georgia, serif;
		--sig: var(--mkt-signal);
	}

	.landing {
		position: relative;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg);
		overflow-x: clip;
	}

	.grain {
		position: fixed;
		inset: 0;
		z-index: 0;
		pointer-events: none;
		opacity: 0.05;
		mix-blend-mode: overlay;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
		background-size: 180px 180px;
	}

	section {
		width: 100%;
		position: relative;
		z-index: 1;
	}

	/* Reveal */
	:global(.mkt [data-reveal]) {
		opacity: 0;
		transform: translateY(26px);
		transition:
			opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1),
			transform 0.7s cubic-bezier(0.16, 1, 0.3, 1);
		transition-delay: var(--reveal-delay, 0ms);
	}

	:global(.mkt [data-reveal].is-in) {
		opacity: 1;
		transform: none;
	}

	.eyebrow,
	.section-eyebrow {
		display: inline-flex;
		align-items: baseline;
		gap: 2px;
		font-family: var(--mkt-mono);
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.02em;
		color: var(--sig);
		margin-bottom: 20px;
	}

	.br {
		color: var(--text-faint);
	}

	/* Hero */
	.hero {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 40px;
		align-items: center;
		max-width: 1180px;
		margin: 0 auto;
		padding: clamp(48px, 8vw, 100px) clamp(20px, 4vw, 48px) 64px;
	}

	h1 {
		font-family: var(--mkt-display);
		font-optical-sizing: auto;
		font-size: clamp(2.9rem, 6vw, 4.6rem);
		font-weight: 600;
		letter-spacing: -0.01em;
		line-height: 1.02;
		margin: 0 0 22px;
		color: var(--text);
	}

	.stamp {
		display: inline-block;
		margin-top: 8px;
		padding: 4px 14px 8px;
		background: var(--sig);
		color: var(--bg);
		font-style: italic;
		transform: rotate(-1.4deg);
	}

	.sub {
		color: var(--text-dim);
		font-size: 17.5px;
		line-height: 1.6;
		max-width: 44ch;
		margin: 0 0 32px;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 24px;
	}

	.mkt-link {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		font-family: var(--mkt-mono);
		font-size: 13.5px;
		font-weight: 600;
		color: var(--text-dim);
	}

	.mkt-link:hover {
		color: var(--text);
		text-decoration: none;
	}

	.mkt-link .arrow {
		transition: transform 0.2s ease;
		display: inline-block;
	}

	.mkt-link:hover .arrow {
		transform: translateX(3px);
	}

	.mkt-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 14px 30px;
		background: var(--sig);
		color: var(--bg);
		font-weight: 700;
		font-size: 15.5px;
		letter-spacing: -0.005em;
		text-decoration: none;
		clip-path: polygon(0 0, 100% 0, 100% calc(100% - 12px), calc(100% - 12px) 100%, 0 100%);
		transition:
			transform 0.18s ease,
			box-shadow 0.18s ease;
	}

	.mkt-btn:hover {
		text-decoration: none;
		transform: translateY(-2px);
		box-shadow: 6px 8px 0 0 color-mix(in srgb, var(--sig) 35%, transparent);
	}

	.mkt-btn:active {
		transform: translateY(0);
		box-shadow: none;
	}

	.mkt-btn-dark {
		background: var(--bg);
		color: var(--sig);
		box-shadow: 6px 8px 0 0 color-mix(in srgb, var(--bg) 55%, transparent);
	}

	.mkt-btn-dark:hover {
		box-shadow: 6px 8px 0 0 color-mix(in srgb, var(--bg) 75%, transparent);
	}

	.hero-visual {
		position: relative;
		justify-self: end;
		width: 100%;
		max-width: 480px;
	}

	.v-label {
		position: absolute;
		font-family: var(--mkt-mono);
		font-size: 10.5px;
		font-weight: 600;
		letter-spacing: 0.12em;
		color: var(--text-faint);
	}

	.v-label-top {
		top: -22px;
		left: 0;
	}

	.ascend {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}

	.grid-line {
		stroke: var(--border);
		stroke-width: 1;
		fill: none;
	}

	.axis {
		stroke: var(--border-strong);
		stroke-width: 1.5;
	}

	.ascend-line {
		stroke: var(--sig);
		stroke-width: 2.5;
		fill: none;
		stroke-linecap: round;
		stroke-dasharray: 620;
		stroke-dashoffset: 620;
		animation: draw 1.6s ease 0.4s forwards;
	}

	.pt {
		fill: var(--bg);
		stroke: var(--border-strong);
		stroke-width: 2;
	}

	.pt.done {
		fill: color-mix(in srgb, var(--up) 30%, var(--bg));
		stroke: var(--up);
	}

	.pt.gap {
		fill: color-mix(in srgb, var(--sig) 35%, var(--bg));
		stroke: var(--sig);
	}

	.pt.next {
		fill: var(--sig);
		stroke: var(--sig);
		filter: drop-shadow(0 0 8px color-mix(in srgb, var(--sig) 65%, transparent));
	}

	.tick-lbl {
		font-family: var(--mkt-mono);
		font-size: 9px;
		fill: var(--text-faint);
	}

	.tag {
		position: absolute;
		padding: 4px 9px;
		background: var(--bg);
		border: 1px solid var(--border-strong);
		font-family: var(--mkt-mono);
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.04em;
		white-space: nowrap;
	}

	.tag-gap-lbl {
		left: 62%;
		top: 22%;
		color: var(--sig);
		border-color: color-mix(in srgb, var(--sig) 45%, var(--border));
	}

	.tag-next-lbl {
		right: 2%;
		top: -2%;
		color: var(--up);
		border-color: color-mix(in srgb, var(--up) 45%, var(--border));
	}

	.stamp-badge {
		position: absolute;
		bottom: 6%;
		left: 0;
		padding: 5px 10px;
		border: 1px solid var(--border-strong);
		background: var(--bg-card);
		font-family: var(--mkt-mono);
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 0.05em;
		color: var(--text-faint);
		transform: rotate(-2deg);
	}

	/* Stats strip */
	.stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		max-width: 1180px;
		margin: 0 auto;
		padding: 0 clamp(20px, 4vw, 48px);
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}

	.stat {
		position: relative;
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 26px 20px 26px 24px;
		border-left: 1px solid var(--border);
	}

	.stat:first-child {
		border-left: none;
		padding-left: 0;
	}

	.stat-idx {
		font-family: var(--mkt-mono);
		font-size: 10.5px;
		color: var(--text-faint);
		letter-spacing: 0.06em;
	}

	.stat-k {
		font-family: var(--mkt-display);
		font-size: 2rem;
		font-weight: 600;
		color: var(--text);
	}

	.stat-v {
		font-size: 12.5px;
		color: var(--text-faint);
		line-height: 1.4;
	}

	/* Shared section heading */
	.how,
	.pillars,
	.usecases {
		max-width: 1180px;
		margin: 0 auto;
		padding: 84px clamp(20px, 4vw, 48px);
	}

	.how h2,
	.pillars h2,
	.usecases h2 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: clamp(1.7rem, 3.2vw, 2.4rem);
		letter-spacing: -0.01em;
		max-width: 20ch;
		margin: 0 0 52px;
	}

	/* How it works — ascending staircase */
	.steps {
		display: flex;
		align-items: flex-end;
		gap: clamp(8px, 2vw, 28px);
		position: relative;
		padding-top: 40px;
	}

	.steps::before {
		content: '';
		position: absolute;
		left: 2%;
		right: 6%;
		bottom: 108px;
		height: 1px;
		background: color-mix(in srgb, var(--sig) 40%, var(--border));
		transform: rotate(-4deg);
		transform-origin: left;
	}

	.step {
		position: relative;
		flex: 1;
		min-width: 0;
		padding: 20px 18px;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		transform: translateY(calc(52px - var(--i) * 22px));
	}

	.ghost-num {
		position: absolute;
		top: -8px;
		right: 4px;
		font-family: var(--mkt-display);
		font-weight: 300;
		font-size: clamp(3.4rem, 7vw, 5.2rem);
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--border-strong);
		z-index: 0;
		pointer-events: none;
		user-select: none;
	}

	.step-n {
		position: relative;
		z-index: 1;
		display: inline-flex;
		font-family: var(--mkt-mono);
		font-weight: 700;
		font-size: 12px;
		color: var(--sig);
		margin-bottom: 14px;
	}

	.step h3 {
		position: relative;
		z-index: 1;
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.08rem;
		margin-bottom: 8px;
	}

	.step p {
		position: relative;
		z-index: 1;
		font-size: 13.5px;
		color: var(--text-dim);
		line-height: 1.55;
		margin: 0;
	}

	/* Pillars */
	.pillar-grid {
		display: grid;
		grid-template-columns: 1.3fr 1fr 1fr;
		gap: 20px;
	}

	.bracket-card {
		position: relative;
		background: var(--bg-card);
		border: 1px solid var(--border);
		transition: border-color 0.2s;
	}

	.bracket-card::before,
	.bracket-card::after {
		content: '';
		position: absolute;
		width: 16px;
		height: 16px;
		border: 2px solid var(--sig);
		opacity: 0;
		transition: opacity 0.2s ease;
	}

	.bracket-card::before {
		top: -2px;
		left: -2px;
		border-right: none;
		border-bottom: none;
	}

	.bracket-card::after {
		bottom: -2px;
		right: -2px;
		border-left: none;
		border-top: none;
	}

	.bracket-card:hover {
		border-color: var(--border-strong);
	}

	.bracket-card:hover::before,
	.bracket-card:hover::after {
		opacity: 1;
	}

	.pillar {
		padding: 30px 26px;
	}

	.pillar-icon {
		width: 44px;
		height: 44px;
		display: grid;
		place-items: center;
		margin-bottom: 22px;
		border: 1px solid var(--border-strong);
		color: var(--sig);
	}

	.pillar-icon svg {
		width: 22px;
		height: 22px;
		stroke: currentColor;
		stroke-width: 1.8;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.p-num {
		display: block;
		font-family: var(--mkt-mono);
		font-weight: 600;
		font-size: 11px;
		letter-spacing: 0.08em;
		color: var(--text-faint);
		margin-bottom: 8px;
	}

	.pillar h3 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.25rem;
		margin-bottom: 10px;
	}

	.pillar p {
		margin: 0;
		font-size: 14.5px;
		color: var(--text-dim);
		line-height: 1.55;
	}

	/* Use cases */
	.usecases-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-end;
		gap: 20px;
	}

	.usecases-head h2 {
		margin-bottom: 0;
	}

	.usecase-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
		margin-top: 52px;
	}

	.usecase {
		display: flex;
		flex-direction: column;
		padding: 26px 24px;
		border: 1px solid var(--border);
		color: var(--text);
		background: var(--bg-elevated);
		clip-path: polygon(0 0, 100% 0, 100% 100%, 18px 100%, 0 calc(100% - 18px));
		transition:
			border-color 0.2s,
			background 0.2s;
	}

	.usecase:hover {
		text-decoration: none;
		border-color: var(--sig);
		background: var(--bg-card);
	}

	.usecase-idx {
		font-family: var(--mkt-mono);
		font-size: 10.5px;
		font-weight: 600;
		letter-spacing: 0.05em;
		color: var(--text-faint);
		margin-bottom: 16px;
	}

	.usecase h3 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.15rem;
		margin-bottom: 10px;
	}

	.usecase p {
		font-size: 14px;
		color: var(--text-dim);
		line-height: 1.55;
		margin: 0 0 20px;
		flex: 1;
	}

	.usecase-link {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		font-family: var(--mkt-mono);
		font-size: 12.5px;
		font-weight: 600;
		color: var(--sig);
	}

	/* Quote */
	.quote {
		max-width: 780px;
		margin: 0 auto;
		padding: 40px clamp(20px, 4vw, 48px) 96px;
		text-align: center;
	}

	.quote-mark {
		display: block;
		font-family: var(--mkt-display);
		font-size: 5rem;
		line-height: 1;
		color: var(--sig);
		opacity: 0.5;
		margin-bottom: -12px;
	}

	.quote blockquote {
		margin: 0 0 18px;
		font-family: var(--mkt-display);
		font-style: italic;
		font-size: clamp(1.4rem, 3.2vw, 2.1rem);
		font-weight: 500;
		letter-spacing: -0.01em;
		line-height: 1.35;
		color: var(--text);
	}

	.quote-attr {
		margin: 0;
		font-family: var(--mkt-mono);
		font-size: 12px;
		font-weight: 600;
		letter-spacing: 0.04em;
		color: var(--text-faint);
	}

	/* Final CTA */
	.final-cta {
		max-width: 1180px;
		margin: 0 auto 64px;
		padding: 0 clamp(20px, 4vw, 48px);
	}

	.final-cta-inner {
		padding: 64px clamp(24px, 5vw, 64px);
		text-align: center;
		background: var(--sig);
		clip-path: polygon(0 0, 100% 0, 100% calc(100% - 22px), calc(100% - 22px) 100%, 0 100%);
	}

	.final-cta h2 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: clamp(1.7rem, 3.6vw, 2.5rem);
		margin: 0 0 10px;
		color: var(--bg);
	}

	.final-cta p {
		color: color-mix(in srgb, var(--bg) 75%, transparent);
		margin: 0 0 28px;
		font-weight: 600;
	}

	@keyframes draw {
		to {
			stroke-dashoffset: 0;
		}
	}

	@media (max-width: 900px) {
		.hero {
			grid-template-columns: 1fr;
		}

		.hero-visual {
			justify-self: start;
			max-width: 100%;
		}

		.stats {
			grid-template-columns: repeat(2, 1fr);
		}

		.stat:nth-child(3) {
			border-left: none;
			padding-left: 0;
		}

		.steps {
			flex-direction: column;
			align-items: stretch;
			gap: 14px;
		}

		.steps::before {
			display: none;
		}

		.step {
			transform: none;
		}

		.pillar-grid,
		.usecase-grid {
			grid-template-columns: 1fr;
		}

		.usecases-head {
			flex-direction: column;
			align-items: flex-start;
			gap: 16px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		:global(.mkt [data-reveal]) {
			transition: none;
			opacity: 1;
			transform: none;
		}

		.ascend-line {
			animation: none;
			stroke-dashoffset: 0;
		}
	}
</style>
