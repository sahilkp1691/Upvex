<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const sections = [
		{
			id: 'teams',
			idx: '01',
			eyebrow: 'Teams & companies',
			title: 'Close skill gaps before they become incidents.',
			body: 'Engineering and data teams usually get the same fixed onboarding course whether they are a new hire or a five-year senior. Upvex diagnoses each person against your actual stack — starting with SQL and Spark — and gives them a personal roadmap, while admins see exactly where the team is weak and can author the graph themselves, or hand us their own materials to curate.',
			bullets: [
				'Per-employee diagnostic instead of a generic onboarding course',
				'Root-gap visibility for managers, not just pass/fail scores',
				'Admin tools to author and adjust the knowledge graph for your stack',
				'Upload your own docs, playbooks, and decks — we curate a structured course from them',
				'Progress, streaks, and completion tracked per learner',
				'Deploy against real production skills — SQL, Spark, more coming'
			],
			cta: { label: 'Talk to us about team rollout', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20teams' },
			stat: { k: 'Admin', v: 'graph & content authoring built in' }
		},
		{
			id: 'schools',
			idx: '02',
			eyebrow: 'Schools & nonprofits',
			title: 'Give every student a path back to the foundation.',
			body: 'Students fall behind not because they lack a full course, but because one earlier concept never stuck. Upvex\u2019s diagnostic finds that concept and rebuilds from there, so teachers spend less time reteaching everything and more time on what is actually missing. Built with sponsored and discounted access in mind.',
			bullets: [
				'Adaptive remediation instead of one-size-fits-all worksheets',
				'Root-cause gap reports teachers can act on, not just grades',
				'Gamified motivation — XP, streaks, badges — built for engagement',
				'Discounted and sponsored access plans for schools and nonprofits',
				'Works alongside existing curricula rather than replacing them'
			],
			cta: { label: 'Discuss a school or nonprofit plan', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20schools' },
			stat: { k: 'Sponsored', v: 'access plans for eligible organizations' }
		},
		{
			id: 'individuals',
			idx: '03',
			eyebrow: 'Individual learners',
			title: 'Stop repeating lessons you already know.',
			body: 'Generic courses move at one pace for everyone. Upvex tests what you actually know first, skips it, and spends your time on the specific concept blocking your progress \u2014 with content generated for your learning style and tone, not reused from a fixed script.',
			bullets: [
				'Free adaptive diagnostic before you commit to a track',
				'Lessons generated against your profile, not a static syllabus',
				'XP, levels, streaks, and badges for momentum that sticks',
				'Start with SQL or Spark \u2014 more tracks on the way'
			],
			cta: { label: 'Start learning', href: '/auth' },
			stat: { k: 'Free', v: 'to diagnose before you commit' }
		}
	];
</script>

<svelte:head>
	<title>Solutions — Upvex</title>
	<meta
		name="description"
		content="The same diagnostic and knowledge-graph engine, deployed for teams, schools & nonprofits, and individual learners."
	/>
</svelte:head>

<div class="mkt solutions">
	<MarketingNav />

	<section class="hero">
		<p class="eyebrow" use:reveal data-reveal><span class="br">[</span>Solutions<span class="br">]</span></p>
		<h1 use:reveal={{ delay: 40 }} data-reveal>One engine.<br />Three ways to deploy it.</h1>
		<p class="sub" use:reveal={{ delay: 80 }} data-reveal>
			The same diagnostic, prerequisite graph, and generation loop adapts to how you teach —
			inside a company, a classroom, or on your own.
		</p>
		<div class="jump-row" use:reveal={{ delay: 120 }} data-reveal>
			{#each sections as s (s.id)}
				<a href="#{s.id}" class="jump"><span class="jump-idx">{s.idx}</span>{s.eyebrow}</a>
			{/each}
		</div>
	</section>

	{#each sections as s, i (s.id)}
		<section class="use-section" id={s.id} class:tint={i % 2 === 1}>
			<span class="ghost-num" aria-hidden="true">{s.idx}</span>
			<div class="use-copy" use:reveal data-reveal>
				<p class="eyebrow"><span class="br">[</span>TARGET {s.idx} // {s.eyebrow}<span class="br">]</span></p>
				<h2>{s.title}</h2>
				<p class="body">{s.body}</p>
				<a href={s.cta.href} class="mkt-btn">{s.cta.label}</a>
			</div>
			<div class="use-side" use:reveal={{ delay: 100 }} data-reveal>
				<ul class="bullets">
					{#each s.bullets as b (b)}
						<li>
							<span class="check" aria-hidden="true">&#10003;</span>
							{b}
						</li>
					{/each}
				</ul>
				<div class="stat-card bracket-card">
					<span class="stat-k">{s.stat.k}</span>
					<span class="stat-v">{s.stat.v}</span>
				</div>
			</div>
		</section>
	{/each}

	<section class="pricing-note" use:reveal data-reveal>
		<h2>Pricing is still taking shape.</h2>
		<p>
			We are in early development and want plans that fit each context instead of one fixed
			price. Reach out and we will figure out the right plan together — including sponsored
			access for schools and nonprofits.
		</p>
		<a href="mailto:hello@upvex.io" class="mkt-btn">Get in touch</a>
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

	.solutions {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

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

	.br {
		color: var(--text-faint);
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
		margin-bottom: 18px;
	}

	.hero {
		max-width: 820px;
		margin: 0 auto;
		padding: clamp(48px, 8vw, 92px) clamp(20px, 4vw, 48px) 48px;
		text-align: center;
	}

	.hero h1 {
		font-family: var(--mkt-display);
		font-optical-sizing: auto;
		font-weight: 600;
		font-size: clamp(2.3rem, 5vw, 3.6rem);
		letter-spacing: -0.01em;
		line-height: 1.05;
		margin: 0 0 20px;
	}

	.hero .sub {
		color: var(--text-dim);
		font-size: 17px;
		line-height: 1.6;
		max-width: 54ch;
		margin: 0 auto 36px;
	}

	.jump-row {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	.jump {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		padding: 9px 16px;
		border: 1px solid var(--border-strong);
		font-family: var(--mkt-mono);
		font-size: 13px;
		font-weight: 600;
		color: var(--text-dim);
	}

	.jump-idx {
		color: var(--sig);
	}

	.jump:hover {
		color: var(--text);
		border-color: var(--sig);
		text-decoration: none;
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

	.use-section {
		position: relative;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 0.85fr);
		gap: 48px;
		max-width: 1180px;
		margin: 0 auto;
		padding: 88px clamp(20px, 4vw, 48px);
		border-top: 1px solid var(--border);
		scroll-margin-top: 90px;
		overflow: hidden;
	}

	.use-section.tint {
		background: var(--bg-elevated);
	}

	.ghost-num {
		position: absolute;
		top: 20px;
		right: clamp(20px, 4vw, 48px);
		font-family: var(--mkt-display);
		font-weight: 300;
		font-size: clamp(5rem, 11vw, 9rem);
		line-height: 1;
		color: transparent;
		-webkit-text-stroke: 1px var(--border-strong);
		z-index: 0;
		pointer-events: none;
		user-select: none;
	}

	.use-copy,
	.use-side {
		position: relative;
		z-index: 1;
	}

	.use-copy h2 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: clamp(1.8rem, 3.6vw, 2.5rem);
		letter-spacing: -0.015em;
		margin: 0 0 16px;
		max-width: 18ch;
	}

	.use-copy .body {
		color: var(--text-dim);
		font-size: 16px;
		line-height: 1.65;
		max-width: 52ch;
		margin: 0 0 30px;
	}

	.use-side {
		display: flex;
		flex-direction: column;
		gap: 24px;
	}

	.bullets {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 13px;
	}

	.bullets li {
		display: flex;
		align-items: flex-start;
		gap: 12px;
		font-size: 14.5px;
		color: var(--text);
		line-height: 1.5;
	}

	.check {
		flex-shrink: 0;
		width: 20px;
		height: 20px;
		display: grid;
		place-items: center;
		border: 1px solid var(--up);
		color: var(--up);
		font-size: 11px;
		font-weight: 700;
		margin-top: 1px;
	}

	.stat-card {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 18px 20px;
		border: 1px solid var(--border);
		background: var(--bg-card);
	}

	.stat-k {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.4rem;
		color: var(--sig);
	}

	.stat-v {
		font-size: 12.5px;
		color: var(--text-faint);
	}

	/* Corner-bracket hover treatment, shared with landing */
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

	.pricing-note {
		max-width: 640px;
		margin: 28px auto 88px;
		padding: 0 clamp(20px, 4vw, 48px);
		text-align: center;
	}

	.pricing-note h2 {
		font-family: var(--mkt-display);
		font-weight: 600;
		font-size: 1.9rem;
		margin-bottom: 14px;
	}

	.pricing-note p {
		color: var(--text-dim);
		line-height: 1.6;
		margin-bottom: 30px;
	}

	@media (max-width: 860px) {
		.use-section {
			grid-template-columns: 1fr;
		}

		.ghost-num {
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
