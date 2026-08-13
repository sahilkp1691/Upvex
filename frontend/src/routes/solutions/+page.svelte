<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';

	const sections = [
		{
			id: 'teams',
			eyebrow: 'For teams & companies',
			title: 'Close skill gaps before they become incidents.',
			body: 'Engineering and data teams usually get the same fixed onboarding course whether they are a new hire or a five-year senior. Upvex diagnoses each person against your actual stack — starting with SQL and Spark — and gives them a personal roadmap, while admins see exactly where the team is weak and can author the graph themselves.',
			bullets: [
				'Per-employee diagnostic instead of a generic onboarding course',
				'Root-gap visibility for managers, not just pass/fail scores',
				'Admin tools to author and adjust the knowledge graph for your stack',
				'Progress, streaks, and completion tracked per learner',
				'Deploy against real production skills — SQL, Spark, more coming'
			],
			cta: { label: 'Talk to us about team rollout', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20teams' },
			stat: { k: 'Admin', v: 'graph & content authoring built in' }
		},
		{
			id: 'schools',
			eyebrow: 'For schools & nonprofits',
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
			eyebrow: 'For individual learners',
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

<div class="solutions">
	<MarketingNav />

	<section class="hero">
		<p class="eyebrow">Solutions</p>
		<h1>One engine. Three ways to deploy it.</h1>
		<p class="sub">
			The same diagnostic, prerequisite graph, and generation loop adapts to how you teach —
			inside a company, a classroom, or on your own.
		</p>
		<div class="jump-row">
			{#each sections as s (s.id)}
				<a href="#{s.id}" class="jump">{s.eyebrow.replace('For ', '')}</a>
			{/each}
		</div>
	</section>

	{#each sections as s, i (s.id)}
		<section class="use-section" id={s.id} class:tint={i % 2 === 1}>
			<div class="use-copy">
				<p class="eyebrow">{s.eyebrow}</p>
				<h2>{s.title}</h2>
				<p class="body">{s.body}</p>
				<a href={s.cta.href} class="btn btn-primary btn-lg">{s.cta.label}</a>
			</div>
			<div class="use-side">
				<ul class="bullets">
					{#each s.bullets as b (b)}
						<li>
							<span class="check" aria-hidden="true">
								<svg viewBox="0 0 16 16" fill="none">
									<path d="M3.5 8.5 L6.5 11.5 L12.5 4.5" />
								</svg>
							</span>
							{b}
						</li>
					{/each}
				</ul>
				<div class="stat-card">
					<span class="stat-k">{s.stat.k}</span>
					<span class="stat-v">{s.stat.v}</span>
				</div>
			</div>
		</section>
	{/each}

	<section class="pricing-note">
		<h2>Pricing is still taking shape.</h2>
		<p>
			We are in early development and want plans that fit each context instead of one fixed
			price. Reach out and we will figure out the right plan together — including sponsored
			access for schools and nonprofits.
		</p>
		<a href="mailto:hello@upvex.io" class="btn btn-primary btn-lg">Get in touch</a>
	</section>

	<MarketingFooter />
</div>

<style>
	.solutions {
		--font-display: 'Bricolage Grotesk', 'Plus Jakarta Sans', sans-serif;
		min-height: 100vh;
		display: flex;
		flex-direction: column;
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
		margin-bottom: 16px;
	}

	.eyebrow::before {
		content: '';
		width: 18px;
		height: 1.5px;
		background: var(--up);
		display: inline-block;
	}

	.hero {
		max-width: 780px;
		margin: 0 auto;
		padding: clamp(48px, 8vw, 88px) clamp(20px, 4vw, 48px) 40px;
		text-align: center;
	}

	.hero h1 {
		font-family: var(--font-display);
		font-size: clamp(2.2rem, 4.6vw, 3.4rem);
		letter-spacing: -0.03em;
		margin: 0 0 18px;
	}

	.hero .sub {
		color: var(--text-dim);
		font-size: 17px;
		line-height: 1.6;
		max-width: 56ch;
		margin: 0 auto 32px;
	}

	.jump-row {
		display: flex;
		justify-content: center;
		flex-wrap: wrap;
		gap: 10px;
	}

	.jump {
		padding: 8px 16px;
		border-radius: 999px;
		border: 1px solid var(--border-strong);
		font-size: 13.5px;
		font-weight: 650;
		color: var(--text-dim);
	}

	.jump:hover {
		color: var(--text);
		border-color: var(--up);
		text-decoration: none;
	}

	.use-section {
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 0.85fr);
		gap: 48px;
		max-width: 1180px;
		margin: 0 auto;
		padding: 72px clamp(20px, 4vw, 48px);
		border-top: 1px solid var(--border);
		scroll-margin-top: 90px;
	}

	.use-section.tint {
		background: var(--bg-elevated);
		border-radius: 28px;
		max-width: calc(1180px + 40px);
	}

	.use-copy h2 {
		font-family: var(--font-display);
		font-size: clamp(1.7rem, 3.4vw, 2.4rem);
		letter-spacing: -0.025em;
		margin: 0 0 16px;
		max-width: 18ch;
	}

	.use-copy .body {
		color: var(--text-dim);
		font-size: 16px;
		line-height: 1.65;
		max-width: 52ch;
		margin: 0 0 28px;
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
		gap: 14px;
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
		width: 22px;
		height: 22px;
		border-radius: 50%;
		display: grid;
		place-items: center;
		background: var(--up-soft);
		color: var(--up);
		margin-top: 1px;
	}

	.check svg {
		width: 11px;
		height: 11px;
		stroke: currentColor;
		stroke-width: 2.2;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.stat-card {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 18px 20px;
		border-radius: var(--radius);
		border: 1px solid var(--border);
		background: var(--bg-card);
	}

	.stat-k {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 1.3rem;
		color: var(--up);
	}

	.stat-v {
		font-size: 13px;
		color: var(--text-faint);
	}

	.pricing-note {
		max-width: 640px;
		margin: 24px auto 80px;
		padding: 0 clamp(20px, 4vw, 48px);
		text-align: center;
	}

	.pricing-note h2 {
		font-family: var(--font-display);
		font-size: 1.7rem;
		margin-bottom: 12px;
	}

	.pricing-note p {
		color: var(--text-dim);
		line-height: 1.6;
		margin-bottom: 26px;
	}

	.btn-lg {
		padding: 14px 26px;
		font-size: 15.5px;
	}

	@media (max-width: 860px) {
		.use-section {
			grid-template-columns: 1fr;
		}
	}
</style>
