<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const slides = [
		'cover',
		'problem',
		'solution',
		'product',
		'audience',
		'model',
		'roadmap',
		'ask'
	];

	let active = $state(0);

	/** @param {HTMLElement} node */
	function trackSlides(node) {
		const sections = Array.from(node.querySelectorAll('.slide'));
		const observer = new IntersectionObserver(
			(entries) => {
				for (const entry of entries) {
					if (entry.isIntersecting) {
						const idx = sections.indexOf(entry.target);
						if (idx !== -1) active = idx;
					}
				}
			},
			{ rootMargin: '-40% 0px -40% 0px', threshold: 0.01 }
		);
		sections.forEach((s) => observer.observe(s));
		return {
			destroy() {
				observer.disconnect();
			}
		};
	}

	const audience = [
		{
			label: 'Teams & companies',
			body: 'Per-employee diagnostic and admin graph authoring today; upload your own materials for us to curate into a course tomorrow.',
			href: '/solutions#teams'
		},
		{
			label: 'Schools & nonprofits',
			body: 'Root-cause remediation and sponsored access instead of one-size-fits-all worksheets.',
			href: '/solutions#schools'
		},
		{
			label: 'Individual learners',
			body: 'A free diagnostic, then a personal path that skips what you already know.',
			href: '/solutions#individuals'
		}
	];

	const model = [
		{
			label: 'Individuals',
			body: 'Free adaptive diagnostic, with a subscription unlocking full generated tracks.'
		},
		{
			label: 'Teams & companies',
			body: 'Seat-based licensing plus admin tools to author your own knowledge graph, or hand us your materials to curate.'
		},
		{
			label: 'Schools & nonprofits',
			body: 'Discounted or sponsored access, priced to fit the organization rather than a fixed rate.'
		}
	];

	const roadmap = [
		{
			label: 'Now',
			body: 'SQL and Spark tracks live. Full diagnose \u2192 trace \u2192 generate \u2192 gamify loop working end to end.'
		},
		{
			label: 'Next',
			body: 'More technical tracks, team dashboards for managers, and deeper admin graph-authoring tools.'
		},
		{
			label: 'Later',
			body: 'LMS integrations, plus letting businesses upload their own materials \u2014 playbooks, docs, decks \u2014 for Upvex to curate into a structured, diagnosable course.'
		},
		{
			label: 'Vision',
			body: 'Any subject, not just technical skills, represented on one shared prerequisite graph.'
		}
	];
</script>

<svelte:head>
	<title>Pitch — Upvex</title>
	<meta
		name="description"
		content="An overview of Upvex for partners, schools, teams, and early adopters."
	/>
</svelte:head>

<div class="mkt pitch">
	<MarketingNav />

	<div class="counter" aria-hidden="true">
		<span class="counter-br">[</span>{String(active + 1).padStart(2, '0')}<span class="counter-sep">/</span
		>{String(slides.length).padStart(2, '0')}<span class="counter-br">]</span>
	</div>

	<div class="deck" use:trackSlides>
		<section class="slide cover" id="cover">
			<span class="slide-index"><span class="br">[</span>01<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>Overview for partners, schools, teams &amp; early adopters</p>
			<h1 use:reveal={{ delay: 60 }} data-reveal>Upvex</h1>
			<p class="tagline" use:reveal={{ delay: 100 }} data-reveal>Skills on an upward vector.</p>
			<div class="meta-row" use:reveal={{ delay: 140 }} data-reveal>
				<span class="meta-chip">Status: early development</span>
				<span class="meta-chip">Focus: adaptive skill learning, any subject over time</span>
			</div>
		</section>

		<section class="slide" id="problem">
			<span class="slide-index"><span class="br">[</span>02<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>The problem</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Courses finish. Gaps don&rsquo;t.</h2>
			<ul class="points" use:reveal={{ delay: 80 }} data-reveal>
				<li>Static curricula give every learner the same path, regardless of what they know.</li>
				<li>
					When someone gets stuck, most platforms show the wrong answer &mdash; not the earlier
					concept actually causing it.
				</li>
				<li>Completion is treated as competence, so gaps quietly compound.</li>
			</ul>
		</section>

		<section class="slide tint" id="solution">
			<span class="slide-index"><span class="br">[</span>03<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>The solution</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Diagnose &rarr; trace &rarr; generate &rarr; climb.</h2>
			<p class="lead" use:reveal={{ delay: 80 }} data-reveal>
				Upvex represents every subject as a prerequisite knowledge graph. An adaptive diagnostic
				tags each answer to a concept node; a recursive graph walk finds the upstream root cause;
				a generation pipeline assembles a lesson against the learner&rsquo;s live profile; and a
				gamification loop keeps the climb visible.
			</p>
			<div class="chip-row" use:reveal={{ delay: 120 }} data-reveal>
				<span class="chip">Adaptive diagnostic</span>
				<span class="chip">Recursive root-gap traversal</span>
				<span class="chip">Per-profile generation</span>
				<span class="chip">XP, streaks, badges</span>
			</div>
		</section>

		<section class="slide" id="product">
			<span class="slide-index"><span class="br">[</span>04<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>Product</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Four systems, one loop.</h2>
			<div class="mini-grid">
				<div class="mini-card bracket-card" use:reveal={{ delay: 0 }} data-reveal>
					<h3>Diagnostic engine</h3>
					<p>Branches on every answer; deterministic scoring plus LLM-assisted grading.</p>
				</div>
				<div class="mini-card bracket-card" use:reveal={{ delay: 80 }} data-reveal>
					<h3>Knowledge graph</h3>
					<p>
						Concepts and prerequisites, walked upstream to find the real root gap &mdash; built to
						extend past technical skills to any subject.
					</p>
				</div>
				<div class="mini-card bracket-card" use:reveal={{ delay: 160 }} data-reveal>
					<h3>Generated lessons</h3>
					<p>Assembled live per profile signature, then cached for instant reuse.</p>
				</div>
				<div class="mini-card bracket-card" use:reveal={{ delay: 240 }} data-reveal>
					<h3>Gamification loop</h3>
					<p>XP, streaks, levels, and badges tied to checkpoints that actually matter.</p>
				</div>
			</div>
		</section>

		<section class="slide tint" id="audience">
			<span class="slide-index"><span class="br">[</span>05<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>Who it&rsquo;s for</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>One engine, three deployments.</h2>
			<div class="mini-grid three">
				{#each audience as a, i (a.label)}
					<a class="mini-card link bracket-card" href={a.href} use:reveal={{ delay: i * 80 }} data-reveal>
						<h3>{a.label}</h3>
						<p>{a.body}</p>
						<span class="mini-link">Learn more <span class="arrow">&rarr;</span></span>
					</a>
				{/each}
			</div>
		</section>

		<section class="slide" id="model">
			<span class="slide-index"><span class="br">[</span>06<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>Business model</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Priced to fit where it&rsquo;s deployed.</h2>
			<div class="mini-grid three">
				{#each model as m, i (m.label)}
					<div class="mini-card bracket-card" use:reveal={{ delay: i * 80 }} data-reveal>
						<h3>{m.label}</h3>
						<p>{m.body}</p>
					</div>
				{/each}
			</div>
			<p class="footnote">Still being validated with early design partners &mdash; nothing here is fixed.</p>
		</section>

		<section class="slide tint" id="roadmap">
			<span class="slide-index"><span class="br">[</span>07<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>Roadmap</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Where this is headed.</h2>
			<div class="timeline">
				{#each roadmap as r, i (r.label)}
					<div class="tl-item" use:reveal={{ delay: i * 90 }} data-reveal>
						<span class="tl-waypoint">{String(i + 1).padStart(2, '0')}</span>
						<div>
							<h3>{r.label}</h3>
							<p>{r.body}</p>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<section class="slide ask" id="ask">
			<span class="slide-index"><span class="br">[</span>08<span class="br">]</span></span>
			<p class="eyebrow" use:reveal data-reveal>The ask</p>
			<h2 use:reveal={{ delay: 40 }} data-reveal>Building in public. Looking for early partners.</h2>
			<p class="lead" use:reveal={{ delay: 80 }} data-reveal>
				We want design partners across teams, schools, and individual learners &mdash; and anyone
				who wants to help shape the graph. If this problem is familiar, we would like to talk.
			</p>
			<div class="cta-row" use:reveal={{ delay: 120 }} data-reveal>
				<a href="mailto:hello@upvex.io" class="mkt-btn">Get in touch</a>
				<a href="/solutions" class="mkt-link">Explore solutions <span class="arrow">&rarr;</span></a>
			</div>
		</section>
	</div>

	<MarketingFooter />
</div>

<style>
	.mkt {
		--mkt-signal: var(--warn);
		--mkt-mono: 'JetBrains Mono', ui-monospace, 'Cascadia Code', monospace;
		--mkt-display: 'Fraunces', Georgia, serif;
		--sig: var(--mkt-signal);
	}

	.pitch {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	:global(.mkt [data-reveal]) {
		opacity: 0;
		transform: translateY(24px);
		transition:
			opacity 0.65s cubic-bezier(0.16, 1, 0.3, 1),
			transform 0.65s cubic-bezier(0.16, 1, 0.3, 1);
		transition-delay: var(--reveal-delay, 0ms);
	}

	:global(.mkt [data-reveal].is-in) {
		opacity: 1;
		transform: none;
	}

	.br {
		color: var(--text-faint);
	}

	.counter {
		position: fixed;
		right: clamp(16px, 3vw, 32px);
		bottom: 24px;
		z-index: 40;
		padding: 8px 14px;
		background: var(--bg-card);
		border: 1px solid var(--border-strong);
		font-family: var(--mkt-mono);
		font-weight: 600;
		font-size: 12.5px;
		letter-spacing: 0.02em;
		color: var(--text-dim);
		box-shadow: 5px 6px 0 0 color-mix(in srgb, var(--sig) 25%, transparent);
	}

	.counter-br {
		color: var(--sig);
	}

	.counter-sep {
		color: var(--text-faint);
		margin: 0 1px;
	}

	.eyebrow {
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

	.slide {
		position: relative;
		max-width: 900px;
		margin: 0 auto;
		padding: clamp(64px, 12vw, 128px) clamp(20px, 4vw, 48px);
		border-top: 1px solid var(--border);
		scroll-margin-top: 24px;
	}

	.slide.tint {
		max-width: none;
		background: var(--bg-elevated);
	}

	.slide.tint > * {
		max-width: 900px;
		margin-left: auto;
		margin-right: auto;
	}

	.slide-index {
		position: absolute;
		top: clamp(20px, 4vw, 40px);
		right: clamp(20px, 4vw, 48px);
		font-family: var(--mkt-mono);
		font-weight: 600;
		font-size: 13px;
		letter-spacing: 0.03em;
		color: var(--text-faint);
		line-height: 1;
		user-select: none;
	}

	.cover {
		border-top: none;
		text-align: center;
		padding-top: clamp(72px, 14vw, 140px);
	}

	.cover .eyebrow {
		justify-content: center;
	}

	.cover h1 {
		font-family: var(--mkt-display);
		font-optical-sizing: auto;
		font-size: clamp(3.6rem, 11vw, 7rem);
		font-weight: 600;
		font-style: italic;
		letter-spacing: -0.015em;
		margin: 0;
		display: inline-block;
		padding: 2px 20px 10px;
		background: var(--sig);
		color: var(--bg);
		transform: rotate(-1deg);
	}

	.tagline {
		font-family: var(--mkt-mono);
		font-size: 1rem;
		letter-spacing: 0.02em;
		color: var(--text-dim);
		margin: 26px 0 30px;
	}

	.meta-row {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	.meta-chip {
		padding: 7px 14px;
		border: 1px solid var(--border-strong);
		font-family: var(--mkt-mono);
		font-size: 12px;
		font-weight: 500;
		color: var(--text-dim);
	}

	h2 {
		font-family: var(--mkt-display);
		font-optical-sizing: auto;
		font-weight: 600;
		font-size: clamp(1.9rem, 4.2vw, 2.7rem);
		letter-spacing: -0.015em;
		max-width: 18ch;
		margin: 0 0 26px;
	}

	.lead {
		font-size: 16.5px;
		color: var(--text-dim);
		line-height: 1.7;
		max-width: 62ch;
	}

	.points {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 16px;
		max-width: 60ch;
	}

	.points li {
		position: relative;
		padding-left: 28px;
		font-size: 16px;
		color: var(--text);
		line-height: 1.6;
	}

	.points li::before {
		content: '';
		position: absolute;
		left: 0;
		top: 7px;
		width: 10px;
		height: 10px;
		background: var(--sig);
		clip-path: polygon(50% 0, 100% 100%, 0 100%);
	}

	.chip-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 30px;
	}

	.chip {
		padding: 8px 14px;
		border: 1px solid var(--up);
		color: var(--up);
		font-family: var(--mkt-mono);
		font-size: 12px;
		font-weight: 600;
	}

	.mini-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 16px;
	}

	.mini-grid.three {
		grid-template-columns: repeat(3, 1fr);
	}

	.bracket-card {
		position: relative;
	}

	.bracket-card::before,
	.bracket-card::after {
		content: '';
		position: absolute;
		width: 14px;
		height: 14px;
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

	.bracket-card:hover::before,
	.bracket-card:hover::after {
		opacity: 1;
	}

	.mini-card {
		display: flex;
		flex-direction: column;
		padding: 22px;
		border: 1px solid var(--border);
		background: var(--bg-card);
	}

	.mini-card.link {
		color: var(--text);
		transition: border-color 0.2s;
	}

	.mini-card.link:hover {
		text-decoration: none;
		border-color: var(--border-strong);
	}

	.mini-card h3 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.08rem;
		margin: 0 0 8px;
	}

	.mini-card p {
		margin: 0;
		font-size: 13.5px;
		color: var(--text-dim);
		line-height: 1.55;
		flex: 1;
	}

	.mini-link {
		display: inline-flex;
		align-items: center;
		gap: 5px;
		margin-top: 16px;
		font-family: var(--mkt-mono);
		font-size: 12px;
		font-weight: 600;
		color: var(--sig);
	}

	.footnote {
		margin: 24px 0 0;
		font-family: var(--mkt-mono);
		font-size: 12px;
		color: var(--text-faint);
	}

	.timeline {
		display: flex;
		flex-direction: column;
		gap: 0;
		position: relative;
	}

	.tl-item {
		position: relative;
		display: flex;
		gap: 22px;
		padding: 22px 0;
		border-left: 1.5px solid var(--border-strong);
		padding-left: 26px;
		margin-left: 5px;
	}

	.tl-item:last-child {
		border-left-color: transparent;
	}

	.tl-waypoint {
		position: absolute;
		left: -17px;
		top: 22px;
		width: 24px;
		height: 24px;
		display: grid;
		place-items: center;
		background: var(--bg);
		border: 1.5px solid var(--sig);
		color: var(--sig);
		font-family: var(--mkt-mono);
		font-size: 10px;
		font-weight: 700;
	}

	.tl-item h3 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.1rem;
		margin: 0 0 6px;
	}

	.tl-item p {
		margin: 0;
		font-size: 14.5px;
		color: var(--text-dim);
		line-height: 1.6;
		max-width: 60ch;
	}

	.ask {
		text-align: left;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 24px;
		margin-top: 32px;
	}

	.mkt-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 14px 28px;
		background: var(--sig);
		color: var(--bg);
		font-weight: 700;
		font-size: 15px;
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

	.mkt-link .arrow,
	.mini-link .arrow {
		transition: transform 0.2s ease;
		display: inline-block;
	}

	.mkt-link:hover .arrow {
		transform: translateX(3px);
	}

	@media (max-width: 720px) {
		.mini-grid,
		.mini-grid.three {
			grid-template-columns: 1fr;
		}

		.slide-index {
			display: none;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		:global(.mkt [data-reveal]) {
			transition: none;
			opacity: 1;
			transform: none;
		}
	}
</style>
