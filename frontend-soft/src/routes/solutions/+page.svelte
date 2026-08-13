<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const sections = [
		{
			id: 'teams',
			eyebrow: 'Teams & companies',
			title: 'Close skill gaps before they become incidents.',
			body: 'Diagnose each person against your stack — or upload playbooks and decks for us to curate. Managers see root gaps; employees get a path they actually finish.',
			bullets: [
				'Per-employee diagnostic instead of a generic onboarding course',
				'Root-gap visibility for managers',
				'Upload docs, playbooks, and decks — curated into a course graph',
				'Progress and completion tracked per learner'
			],
			cta: { label: 'Talk to us about team rollout', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20teams' }
		},
		{
			id: 'schools',
			eyebrow: 'Schools & nonprofits',
			title: 'Give every student a path back to the foundation.',
			body: 'Find the earlier concept that never stuck and rebuild from there — with engagement that keeps students returning.',
			bullets: [
				'Adaptive remediation instead of one-size worksheets',
				'Root-cause gap reports teachers can act on',
				'Motivation loops built for engagement',
				'Sponsored and discounted access plans'
			],
			cta: { label: 'Discuss a school plan', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20schools' }
		},
		{
			id: 'individuals',
			eyebrow: 'Individual learners',
			title: 'Skip what you already know.',
			body: 'A free diagnostic maps your gaps. Lessons are generated for you — then a daily loop keeps progress moving.',
			bullets: [
				'Free adaptive diagnostic before you commit',
				'Lessons for your profile, not a static syllabus',
				'XP, levels, and streaks for momentum',
				'SQL and Spark today — any subject over time'
			],
			cta: { label: 'Start learning', href: '/auth' }
		}
	];
</script>

<svelte:head>
	<title>Solutions — Upvex</title>
</svelte:head>

<div class="solutions">
	<MarketingNav />

	<section class="hero">
		<div use:reveal data-reveal>
			<p class="eyebrow">Solutions</p>
			<div class="accent-line"></div>
			<h1>One engine. Three ways to deploy it.</h1>
			<p class="sub">The same diagnostic and generation loop — for companies, classrooms, and individuals.</p>
			<div class="jumps">
				{#each sections as s (s.id)}
					<a href="#{s.id}">{s.eyebrow}</a>
				{/each}
			</div>
		</div>
	</section>

	{#each sections as s (s.id)}
		<section class="block" id={s.id} use:reveal data-reveal>
			<p class="eyebrow">{s.eyebrow}</p>
			<h2>{s.title}</h2>
			<p class="body">{s.body}</p>
			<ul>
				{#each s.bullets as b (b)}
					<li>{b}</li>
				{/each}
			</ul>
			<a class="btn btn-primary" href={s.cta.href}>{s.cta.label}</a>
		</section>
	{/each}

	<MarketingFooter />
</div>

<style>
	.solutions {
		background: var(--bg);
		color: var(--text);
	}

	.hero,
	.block {
		padding: 48px clamp(20px, 4vw, 48px);
		max-width: 780px;
		margin: 0 auto;
	}

	.hero {
		padding-top: 64px;
	}

	.eyebrow {
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--warn);
		margin: 0 0 8px;
	}

	.accent-line {
		width: 28px;
		height: 3px;
		background: var(--gold);
		border-radius: 2px;
		margin-bottom: 14px;
	}

	h1,
	h2 {
		font-family: var(--font-display);
		font-weight: 600;
		margin: 0 0 12px;
		line-height: 1.15;
	}

	h1 {
		font-size: clamp(1.9rem, 4vw, 2.6rem);
	}

	h2 {
		font-size: clamp(1.35rem, 3vw, 1.75rem);
	}

	.sub,
	.body {
		color: var(--text-dim);
		line-height: 1.55;
		margin: 0 0 20px;
	}

	.jumps {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.jumps a {
		padding: 8px 12px;
		border-radius: 8px;
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text);
		font-weight: 600;
		font-size: 13px;
		text-decoration: none;
	}

	.jumps a:hover {
		border-color: var(--accent);
		color: var(--accent);
	}

	.block {
		border-top: 1px solid var(--border);
	}

	ul {
		margin: 0 0 20px;
		padding: 0;
		list-style: none;
		display: grid;
		gap: 8px;
	}

	li {
		padding: 12px 14px;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		font-size: 14px;
		color: var(--text-dim);
	}

	:global([data-reveal]) {
		opacity: 0;
		transform: translateY(10px);
		transition:
			opacity 0.4s ease,
			transform 0.4s ease;
	}

	:global([data-reveal].is-in) {
		opacity: 1;
		transform: none;
	}
</style>
