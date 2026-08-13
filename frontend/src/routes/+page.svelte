<script>
	import { goto } from '$app/navigation';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';

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

<div class="landing">
	<MarketingNav />

	<section class="hero">
		<div class="hero-copy">
			<p class="eyebrow">Adaptive learning engine for technical skills</p>
			<h1>Skills on an <span class="grad">upward vector.</span></h1>
			<p class="sub">
				Diagnose what you actually know, trace weaknesses to the root, then climb a graph of
				lessons generated for you — not a static course built for everyone.
			</p>
			<div class="cta-row">
				<a href="/auth" class="btn btn-primary btn-lg">Start learning</a>
				<a href="#how-it-works" class="btn btn-ghost btn-lg">See how it works &darr;</a>
			</div>
		</div>

		<div class="hero-visual" aria-hidden="true">
			<svg class="ascend" viewBox="0 0 460 300" fill="none" preserveAspectRatio="xMidYMid meet">
				<line x1="20" y1="270" x2="440" y2="270" class="axis" />
				<path
					class="ascend-fill"
					d="M20 250 C 100 245, 140 200, 190 190 S 280 130, 330 95 S 400 45, 430 30 L 430 270 L 20 270 Z"
				/>
				<path
					class="ascend-line"
					d="M20 250 C 100 245, 140 200, 190 190 S 280 130, 330 95 S 400 45, 430 30"
				/>
				<circle class="pt done" cx="20" cy="250" r="6" />
				<circle class="pt done" cx="190" cy="190" r="6" />
				<circle class="pt gap" cx="330" cy="95" r="7" />
				<circle class="pt next" cx="430" cy="30" r="9" />
			</svg>
			<div class="tag tag-done">Diagnose</div>
			<div class="tag tag-gap-lbl">Root gap found</div>
			<div class="tag tag-next-lbl">Mastery</div>
		</div>
	</section>

	<section class="stats">
		{#each stats as s, i (s.v)}
			<div class="stat" style="--i: {i}">
				<span class="stat-k">{s.k}</span>
				<span class="stat-v">{s.v}</span>
			</div>
		{/each}
	</section>

	<section class="how" id="how-it-works">
		<p class="section-eyebrow">How it works</p>
		<h2>From guesswork to a graph you can climb.</h2>
		<div class="steps">
			{#each steps as s, i (s.n)}
				<div class="step" style="--i: {i}">
					<span class="step-n">{s.n}</span>
					<h3>{s.title}</h3>
					<p>{s.body}</p>
				</div>
			{/each}
		</div>
	</section>

	<section class="pillars" id="product">
		<p class="section-eyebrow">What&rsquo;s inside</p>
		<h2>Built as a real diagnostic system, not a quiz app.</h2>
		<div class="pillar-grid">
			{#each pillars as p, i (p.n)}
				<article class="pillar" style="--i: {i}">
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
				<p class="section-eyebrow">Who it&rsquo;s for</p>
				<h2>Built for more than one kind of learner.</h2>
			</div>
			<a href="/solutions" class="see-all">See all solutions &rarr;</a>
		</div>
		<div class="usecase-grid">
			{#each useCases as u, i (u.href)}
				<a class="usecase" href={u.href} style="--i: {i}">
					<h3>{u.label}</h3>
					<p>{u.body}</p>
					<span class="usecase-link">Explore &rarr;</span>
				</a>
			{/each}
		</div>
	</section>

	<section class="quote">
		<blockquote>
			&ldquo;Competence should be measured by what you can do next &mdash; not which course you
			finished.&rdquo;
		</blockquote>
		<p class="quote-attr">The Upvex approach</p>
	</section>

	<section class="final-cta">
		<h2>Start on your vector today.</h2>
		<p>Free adaptive diagnostic. No static syllabus.</p>
		<a href="/auth" class="btn btn-primary btn-lg">Start learning</a>
	</section>

	<MarketingFooter />
</div>

<style>
	.landing {
		--font-display: 'Bricolage Grotesk', 'Plus Jakarta Sans', sans-serif;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background:
			radial-gradient(ellipse 60% 45% at 85% -8%, var(--mesh-b), transparent 55%),
			radial-gradient(ellipse 55% 40% at 8% 8%, var(--mesh-a), transparent 55%),
			var(--bg);
	}

	section {
		width: 100%;
	}

	.eyebrow,
	.section-eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--up);
	}

	.eyebrow::before,
	.section-eyebrow::before {
		content: '';
		width: 18px;
		height: 1.5px;
		background: var(--up);
		display: inline-block;
	}

	/* Hero */
	.hero {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
		gap: 40px;
		align-items: center;
		max-width: 1180px;
		margin: 0 auto;
		padding: clamp(40px, 7vw, 88px) clamp(20px, 4vw, 48px) 56px;
	}

	.hero-copy {
		animation: rise 0.7s ease both;
	}

	.eyebrow {
		margin-bottom: 20px;
	}

	h1 {
		font-family: var(--font-display);
		font-size: clamp(2.6rem, 5.2vw, 4rem);
		font-weight: 800;
		letter-spacing: -0.035em;
		line-height: 1.04;
		margin: 0 0 20px;
	}

	.grad {
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}

	.sub {
		color: var(--text-dim);
		font-size: 17.5px;
		line-height: 1.6;
		max-width: 46ch;
		margin: 0 0 30px;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
	}

	.btn-lg {
		padding: 14px 28px;
		font-size: 15.5px;
	}

	.hero-visual {
		position: relative;
		animation: rise 0.8s ease 0.1s both;
	}

	.ascend {
		width: 100%;
		height: auto;
		display: block;
		overflow: visible;
	}

	.axis {
		stroke: var(--border);
		stroke-width: 1.5;
	}

	.ascend-fill {
		fill: color-mix(in srgb, var(--up) 7%, transparent);
	}

	.ascend-line {
		stroke: var(--up);
		stroke-width: 3;
		fill: none;
		stroke-linecap: round;
		stroke-dasharray: 620;
		stroke-dashoffset: 620;
		animation: draw 1.8s ease 0.3s forwards;
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
		fill: color-mix(in srgb, var(--warn) 35%, var(--bg));
		stroke: var(--warn);
	}

	.pt.next {
		fill: var(--up);
		stroke: var(--up);
		filter: drop-shadow(0 0 10px color-mix(in srgb, var(--up) 60%, transparent));
	}

	.tag {
		position: absolute;
		padding: 4px 10px;
		border-radius: 999px;
		background: var(--bg-card);
		border: 1px solid var(--border);
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.03em;
		white-space: nowrap;
	}

	.tag-done {
		left: 2%;
		bottom: 4%;
		color: var(--text-faint);
	}

	.tag-gap-lbl {
		left: 66%;
		top: 26%;
		color: var(--warn);
		border-color: color-mix(in srgb, var(--warn) 40%, var(--border));
	}

	.tag-next-lbl {
		right: 0;
		top: -4%;
		color: var(--up);
		border-color: color-mix(in srgb, var(--up) 40%, var(--border));
	}

	/* Stats strip */
	.stats {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		max-width: 1180px;
		margin: 0 auto;
		padding: 28px clamp(20px, 4vw, 48px);
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}

	.stat {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 0 20px;
		border-left: 1px solid var(--border);
		animation: rise 0.6s ease calc(var(--i) * 0.06s) both;
	}

	.stat:first-child {
		border-left: none;
		padding-left: 0;
	}

	.stat-k {
		font-family: var(--font-display);
		font-size: 1.8rem;
		font-weight: 800;
		color: var(--text);
	}

	.stat-v {
		font-size: 13px;
		color: var(--text-faint);
		line-height: 1.4;
	}

	/* Shared section heading */
	.how,
	.pillars,
	.usecases {
		max-width: 1180px;
		margin: 0 auto;
		padding: 76px clamp(20px, 4vw, 48px);
	}

	.how h2,
	.pillars h2,
	.usecases h2 {
		font-family: var(--font-display);
		font-size: clamp(1.6rem, 3vw, 2.2rem);
		letter-spacing: -0.02em;
		max-width: 20ch;
		margin: 14px 0 44px;
	}

	/* How it works */
	.steps {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 0;
		position: relative;
	}

	.steps::before {
		content: '';
		position: absolute;
		top: 17px;
		left: 4%;
		right: 4%;
		height: 1.5px;
		background: repeating-linear-gradient(
			90deg,
			var(--border-strong) 0 8px,
			transparent 8px 14px
		);
	}

	.step {
		position: relative;
		padding: 0 22px 0 0;
		animation: rise 0.6s ease calc(var(--i) * 0.08s) both;
	}

	.step-n {
		position: relative;
		z-index: 1;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 36px;
		height: 36px;
		border-radius: 50%;
		background: var(--bg);
		border: 1.5px solid var(--up);
		color: var(--up);
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 13px;
		margin-bottom: 18px;
	}

	.step h3 {
		font-size: 1.05rem;
		margin-bottom: 8px;
	}

	.step p {
		font-size: 14px;
		color: var(--text-dim);
		line-height: 1.55;
		margin: 0;
	}

	/* Pillars */
	.pillar-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
	}

	.pillar {
		padding: 28px 24px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		background: var(--bg-card);
		transition:
			border-color 0.2s,
			transform 0.2s;
		animation: rise 0.6s ease calc(var(--i) * 0.08s) both;
	}

	.pillar:hover {
		border-color: var(--border-strong);
		transform: translateY(-3px);
	}

	.pillar-icon {
		width: 46px;
		height: 46px;
		border-radius: 12px;
		display: grid;
		place-items: center;
		margin-bottom: 20px;
		background: var(--up-soft);
		color: var(--up);
	}

	.pillar-icon svg {
		width: 24px;
		height: 24px;
		stroke: currentColor;
		stroke-width: 1.8;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.p-num {
		display: block;
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 12px;
		letter-spacing: 0.1em;
		color: var(--text-faint);
		margin-bottom: 6px;
	}

	.pillar h3 {
		font-size: 1.2rem;
		margin-bottom: 8px;
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

	.see-all {
		font-weight: 650;
		font-size: 14.5px;
		white-space: nowrap;
		padding-bottom: 4px;
	}

	.usecase-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 20px;
		margin-top: 44px;
	}

	.usecase {
		display: flex;
		flex-direction: column;
		padding: 26px 24px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		color: var(--text);
		background: var(--bg-elevated);
		transition:
			border-color 0.2s,
			transform 0.2s,
			background 0.2s;
		animation: rise 0.6s ease calc(var(--i) * 0.08s) both;
	}

	.usecase:hover {
		text-decoration: none;
		border-color: var(--up);
		background: var(--bg-card);
		transform: translateY(-3px);
	}

	.usecase h3 {
		font-size: 1.1rem;
		margin-bottom: 10px;
	}

	.usecase p {
		font-size: 14px;
		color: var(--text-dim);
		line-height: 1.55;
		margin: 0 0 18px;
		flex: 1;
	}

	.usecase-link {
		font-size: 13.5px;
		font-weight: 700;
		color: var(--up);
	}

	/* Quote */
	.quote {
		max-width: 780px;
		margin: 0 auto;
		padding: 40px clamp(20px, 4vw, 48px) 88px;
		text-align: center;
	}

	.quote blockquote {
		margin: 0 0 16px;
		font-family: var(--font-display);
		font-size: clamp(1.3rem, 3vw, 1.9rem);
		font-weight: 650;
		letter-spacing: -0.02em;
		line-height: 1.35;
		color: var(--text);
	}

	.quote-attr {
		margin: 0;
		font-size: 13px;
		font-weight: 650;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
	}

	/* Final CTA */
	.final-cta {
		max-width: 1180px;
		margin: 0 auto 64px;
		padding: 64px clamp(24px, 5vw, 64px);
		border-radius: 28px;
		text-align: center;
		background: linear-gradient(135deg, var(--accent-soft), var(--up-soft));
		border: 1px solid var(--border);
	}

	.final-cta h2 {
		font-family: var(--font-display);
		font-size: clamp(1.6rem, 3.4vw, 2.4rem);
		margin: 0 0 10px;
	}

	.final-cta p {
		color: var(--text-dim);
		margin: 0 0 26px;
	}

	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(16px);
		}
		to {
			opacity: 1;
			transform: none;
		}
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

		.stats {
			grid-template-columns: repeat(2, 1fr);
			row-gap: 24px;
		}

		.stat:nth-child(3) {
			border-left: none;
			padding-left: 0;
		}

		.steps {
			grid-template-columns: 1fr;
			gap: 28px;
		}

		.steps::before {
			display: none;
		}

		.pillar-grid,
		.usecase-grid {
			grid-template-columns: 1fr;
		}

		.usecases-head {
			flex-direction: column;
			align-items: flex-start;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.hero-copy,
		.hero-visual,
		.stat,
		.step,
		.pillar,
		.usecase,
		.ascend-line {
			animation: none;
		}

		.ascend-line {
			stroke-dashoffset: 0;
		}
	}
</style>
