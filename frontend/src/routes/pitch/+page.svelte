<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';

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

<div class="pitch">
	<MarketingNav />

	<div class="counter" aria-hidden="true">
		{String(active + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}
	</div>

	<div class="deck" use:trackSlides>
		<section class="slide cover" id="cover">
			<span class="slide-index">01</span>
			<p class="eyebrow">Overview for partners, schools, teams &amp; early adopters</p>
			<h1>Upvex</h1>
			<p class="tagline">Skills on an upward vector.</p>
			<div class="meta-row">
				<span class="meta-chip">Status: early development</span>
				<span class="meta-chip">Focus: adaptive skill learning, any subject over time</span>
			</div>
		</section>

		<section class="slide" id="problem">
			<span class="slide-index">02</span>
			<p class="eyebrow">The problem</p>
			<h2>Courses finish. Gaps don&rsquo;t.</h2>
			<ul class="points">
				<li>Static curricula give every learner the same path, regardless of what they know.</li>
				<li>
					When someone gets stuck, most platforms show the wrong answer &mdash; not the earlier
					concept actually causing it.
				</li>
				<li>Completion is treated as competence, so gaps quietly compound.</li>
			</ul>
		</section>

		<section class="slide tint" id="solution">
			<span class="slide-index">03</span>
			<p class="eyebrow">The solution</p>
			<h2>Diagnose &rarr; trace &rarr; generate &rarr; climb.</h2>
			<p class="lead">
				Upvex represents every subject as a prerequisite knowledge graph. An adaptive diagnostic
				tags each answer to a concept node; a recursive graph walk finds the upstream root cause;
				a generation pipeline assembles a lesson against the learner&rsquo;s live profile; and a
				gamification loop keeps the climb visible.
			</p>
			<div class="chip-row">
				<span class="chip">Adaptive diagnostic</span>
				<span class="chip">Recursive root-gap traversal</span>
				<span class="chip">Per-profile generation</span>
				<span class="chip">XP, streaks, badges</span>
			</div>
		</section>

		<section class="slide" id="product">
			<span class="slide-index">04</span>
			<p class="eyebrow">Product</p>
			<h2>Four systems, one loop.</h2>
			<div class="mini-grid">
				<div class="mini-card">
					<h3>Diagnostic engine</h3>
					<p>Branches on every answer; deterministic scoring plus LLM-assisted grading.</p>
				</div>
				<div class="mini-card">
					<h3>Knowledge graph</h3>
					<p>
						Concepts and prerequisites, walked upstream to find the real root gap &mdash; built to
						extend past technical skills to any subject.
					</p>
				</div>
				<div class="mini-card">
					<h3>Generated lessons</h3>
					<p>Assembled live per profile signature, then cached for instant reuse.</p>
				</div>
				<div class="mini-card">
					<h3>Gamification loop</h3>
					<p>XP, streaks, levels, and badges tied to checkpoints that actually matter.</p>
				</div>
			</div>
		</section>

		<section class="slide tint" id="audience">
			<span class="slide-index">05</span>
			<p class="eyebrow">Who it&rsquo;s for</p>
			<h2>One engine, three deployments.</h2>
			<div class="mini-grid three">
				{#each audience as a (a.label)}
					<a class="mini-card link" href={a.href}>
						<h3>{a.label}</h3>
						<p>{a.body}</p>
						<span class="mini-link">Learn more &rarr;</span>
					</a>
				{/each}
			</div>
		</section>

		<section class="slide" id="model">
			<span class="slide-index">06</span>
			<p class="eyebrow">Business model</p>
			<h2>Priced to fit where it&rsquo;s deployed.</h2>
			<div class="mini-grid three">
				{#each model as m (m.label)}
					<div class="mini-card">
						<h3>{m.label}</h3>
						<p>{m.body}</p>
					</div>
				{/each}
			</div>
			<p class="footnote">Still being validated with early design partners &mdash; nothing here is fixed.</p>
		</section>

		<section class="slide tint" id="roadmap">
			<span class="slide-index">07</span>
			<p class="eyebrow">Roadmap</p>
			<h2>Where this is headed.</h2>
			<div class="timeline">
				{#each roadmap as r, i (r.label)}
					<div class="tl-item" style="--i: {i}">
						<span class="tl-dot"></span>
						<div>
							<h3>{r.label}</h3>
							<p>{r.body}</p>
						</div>
					</div>
				{/each}
			</div>
		</section>

		<section class="slide ask" id="ask">
			<span class="slide-index">08</span>
			<p class="eyebrow">The ask</p>
			<h2>Building in public. Looking for early partners.</h2>
			<p class="lead">
				We want design partners across teams, schools, and individual learners &mdash; and anyone
				who wants to help shape the graph. If this problem is familiar, we would like to talk.
			</p>
			<div class="cta-row">
				<a href="mailto:hello@upvex.io" class="btn btn-primary btn-lg">Get in touch</a>
				<a href="/solutions" class="btn btn-ghost btn-lg">Explore solutions</a>
			</div>
		</section>
	</div>

	<MarketingFooter />
</div>

<style>
	.pitch {
		--font-display: 'Bricolage Grotesk', 'Plus Jakarta Sans', sans-serif;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.counter {
		position: fixed;
		right: clamp(16px, 3vw, 32px);
		bottom: 24px;
		z-index: 40;
		padding: 7px 14px;
		border-radius: 999px;
		background: var(--bg-card);
		border: 1px solid var(--border-strong);
		font-family: var(--font-display);
		font-weight: 700;
		font-size: 12.5px;
		letter-spacing: 0.04em;
		color: var(--text-dim);
		box-shadow: 0 8px 24px rgba(0, 0, 0, 0.18);
	}

	.eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--up);
		margin-bottom: 18px;
	}

	.eyebrow::before {
		content: '';
		width: 18px;
		height: 1.5px;
		background: var(--up);
		display: inline-block;
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
		font-family: var(--font-display);
		font-weight: 800;
		font-size: clamp(2.2rem, 6vw, 4rem);
		color: var(--border);
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
		font-family: var(--font-display);
		font-size: clamp(3.4rem, 10vw, 6.5rem);
		font-weight: 800;
		letter-spacing: -0.04em;
		margin: 0;
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}

	.tagline {
		font-size: 1.25rem;
		color: var(--text-dim);
		margin: 14px 0 30px;
	}

	.meta-row {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	.meta-chip {
		padding: 7px 14px;
		border-radius: 999px;
		border: 1px solid var(--border-strong);
		font-size: 13px;
		font-weight: 600;
		color: var(--text-dim);
	}

	h2 {
		font-family: var(--font-display);
		font-size: clamp(1.8rem, 4vw, 2.6rem);
		letter-spacing: -0.025em;
		max-width: 18ch;
		margin: 0 0 24px;
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
		padding-left: 26px;
		font-size: 16px;
		color: var(--text);
		line-height: 1.6;
	}

	.points li::before {
		content: '';
		position: absolute;
		left: 0;
		top: 9px;
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--warn);
	}

	.chip-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-top: 28px;
	}

	.chip {
		padding: 8px 14px;
		border-radius: 999px;
		background: var(--up-soft);
		color: var(--up);
		font-size: 13px;
		font-weight: 700;
	}

	.mini-grid {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: 16px;
	}

	.mini-grid.three {
		grid-template-columns: repeat(3, 1fr);
	}

	.mini-card {
		display: flex;
		flex-direction: column;
		padding: 22px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		background: var(--bg-card);
	}

	.mini-card.link {
		color: var(--text);
		transition:
			border-color 0.2s,
			transform 0.2s;
	}

	.mini-card.link:hover {
		text-decoration: none;
		border-color: var(--up);
		transform: translateY(-3px);
	}

	.mini-card h3 {
		font-size: 1.02rem;
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
		margin-top: 14px;
		font-size: 13px;
		font-weight: 700;
		color: var(--up);
	}

	.footnote {
		margin: 22px 0 0;
		font-size: 13px;
		color: var(--text-faint);
	}

	.timeline {
		display: flex;
		flex-direction: column;
		gap: 28px;
		position: relative;
		padding-left: 6px;
	}

	.timeline::before {
		content: '';
		position: absolute;
		left: 5px;
		top: 8px;
		bottom: 8px;
		width: 1.5px;
		background: var(--border-strong);
	}

	.tl-item {
		position: relative;
		display: flex;
		gap: 20px;
		padding-left: 26px;
	}

	.tl-dot {
		position: absolute;
		left: -1px;
		top: 6px;
		width: 12px;
		height: 12px;
		border-radius: 50%;
		background: var(--up);
		box-shadow: 0 0 0 4px var(--up-soft);
	}

	.tl-item h3 {
		font-size: 1.05rem;
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
		gap: 12px;
		margin-top: 30px;
	}

	.btn-lg {
		padding: 14px 26px;
		font-size: 15.5px;
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
</style>
