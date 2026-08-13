<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const sections = [
		{
			id: 'teams',
			eyebrow: 'Teams & companies',
			title: 'Training people actually finish.',
			body: 'Diagnose each employee against your stack — or upload playbooks and decks for us to curate. Personal paths, sticky daily loop, completion that stops being the hard part.',
			bullets: [
				'Per-employee diagnostic instead of one shared onboarding deck',
				'Root-gap visibility for managers',
				'Upload docs, playbooks, and decks — we curate a course graph',
				'Streaks and checkpoints so people come back'
			],
			cta: { label: 'Talk to us about team rollout', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20teams' }
		},
		{
			id: 'schools',
			eyebrow: 'Schools & nonprofits',
			title: 'Path back to the foundation.',
			body: 'Students fall behind when one earlier concept never stuck. Upvex finds that concept and rebuilds from there — with XP and streaks built for engagement.',
			bullets: [
				'Adaptive remediation instead of one-size worksheets',
				'Root-cause gap reports teachers can act on',
				'Gamified motivation that feels like progress',
				'Sponsored and discounted access plans'
			],
			cta: { label: 'Discuss a school plan', href: 'mailto:hello@upvex.io?subject=Upvex%20for%20schools' }
		},
		{
			id: 'individuals',
			eyebrow: 'Individual learners',
			title: 'Skip what you know. Climb what you need.',
			body: 'A free diagnostic maps your gaps. Lessons are generated for you — then streaks keep you coming back.',
			bullets: [
				'Free adaptive diagnostic before you commit',
				'Lessons for your profile, not a static syllabus',
				'XP, levels, streaks, and badges',
				'Start with SQL or Spark — any subject over time'
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
			<h1>One climb. Three ways in.</h1>
			<p class="sub">Same diagnostic engine — for teams, schools, and you.</p>
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
		max-width: 820px;
		margin: 0 auto;
	}

	.hero {
		padding-top: 64px;
	}

	.eyebrow {
		font-size: 12px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--warn);
		margin: 0 0 8px;
	}

	h1 {
		font-size: clamp(2rem, 5vw, 3rem);
		margin: 0 0 12px;
		line-height: 1.1;
	}

	h2 {
		font-size: clamp(1.4rem, 3vw, 1.9rem);
		margin: 0 0 12px;
	}

	.sub,
	.body {
		color: var(--text-dim);
		line-height: 1.5;
		margin: 0 0 20px;
	}

	.jumps {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
	}

	.jumps a {
		padding: 8px 14px;
		border-radius: 999px;
		border: 2.5px solid var(--ink);
		background: var(--bg-card);
		color: var(--text);
		font-weight: 700;
		font-size: 13px;
		box-shadow: 2px 2px 0 var(--ink);
		text-decoration: none;
	}

	.block {
		border-top: 3px solid var(--ink);
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
		border: 2.5px solid var(--ink);
		border-radius: 12px;
		font-size: 14px;
		box-shadow: 2px 2px 0 var(--ink);
	}

	:global([data-reveal]) {
		opacity: 0;
		transform: translateY(12px);
		transition:
			opacity 0.45s ease,
			transform 0.45s ease;
	}

	:global([data-reveal].is-in) {
		opacity: 1;
		transform: none;
	}
</style>
