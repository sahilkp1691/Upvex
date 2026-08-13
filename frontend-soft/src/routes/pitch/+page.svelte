<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const audience = [
		{
			label: 'Teams & companies',
			body: 'Per-employee diagnostic and material curation — completion without another dull LMS.',
			href: '/solutions#teams'
		},
		{
			label: 'Schools & nonprofits',
			body: 'Root-cause remediation with engagement that keeps students returning.',
			href: '/solutions#schools'
		},
		{
			label: 'Individual learners',
			body: 'Free diagnostic, then a personal path that skips what they already know.',
			href: '/solutions#individuals'
		}
	];

	const roadmap = [
		{ label: 'Now', body: 'SQL and Spark live. Full diagnose → lesson → progress loop.' },
		{ label: 'Next', body: 'More tracks, team dashboards, deeper admin graph tools.' },
		{ label: 'Later', body: 'Businesses upload materials; we curate diagnosable courses.' },
		{ label: 'Vision', body: 'Any subject on one shared prerequisite graph.' }
	];
</script>

<svelte:head>
	<title>Pitch — Upvex</title>
</svelte:head>

<div class="pitch">
	<MarketingNav />

	<section class="slide cover" use:reveal data-reveal>
		<p class="eyebrow">Early development</p>
		<div class="accent-line"></div>
		<h1>Upvex</h1>
		<p class="lede">Serious outcomes. Light daily experience. Engagement as the delivery system for competence.</p>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Problem</p>
		<h2>Static training wastes time — and people stop showing up.</h2>
		<p>One course for everyone misses the real gap. Completion becomes compliance theatre.</p>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Solution</p>
		<h2>Diagnose → root gap → short lesson → return loop.</h2>
		<p>
			A prerequisite graph powers an adaptive diagnostic. Lessons are personal.
			The daily loop is sticky enough that finishing stops being the hard part.
		</p>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Audience</p>
		<div class="grid">
			{#each audience as a (a.label)}
				<a class="card-link" href={a.href}>
					<strong>{a.label}</strong>
					<span>{a.body}</span>
				</a>
			{/each}
		</div>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Roadmap</p>
		<div class="grid">
			{#each roadmap as r (r.label)}
				<div class="card-link">
					<strong>{r.label}</strong>
					<span>{r.body}</span>
				</div>
			{/each}
		</div>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Ask</p>
		<h2>Design partners and early teams welcome.</h2>
		<p>If this problem is familiar, we would like to talk.</p>
		<a class="btn btn-primary" href="mailto:hello@upvex.io?subject=Upvex%20pitch">Get in touch</a>
	</section>

	<MarketingFooter />
</div>

<style>
	.pitch {
		background: var(--bg);
		color: var(--text);
	}

	.slide {
		padding: 64px clamp(20px, 4vw, 48px);
		max-width: 780px;
		margin: 0 auto;
		border-bottom: 1px solid var(--border);
	}

	.cover h1 {
		font-family: var(--font-display);
		font-size: clamp(2.8rem, 8vw, 4.2rem);
		font-weight: 600;
		margin: 0 0 14px;
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
		margin-bottom: 16px;
	}

	.lede,
	.slide p {
		color: var(--text-dim);
		font-size: 1.05rem;
		line-height: 1.55;
		max-width: 44ch;
	}

	h2 {
		font-family: var(--font-display);
		font-size: clamp(1.4rem, 3vw, 1.85rem);
		font-weight: 600;
		margin: 0 0 12px;
		line-height: 1.2;
	}

	.grid {
		display: grid;
		gap: 10px;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	}

	.card-link {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding: 16px;
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		color: inherit;
		text-decoration: none;
	}

	.card-link strong {
		font-family: var(--font-display);
		font-weight: 600;
	}

	.card-link span {
		font-size: 13.5px;
		color: var(--text-dim);
		line-height: 1.45;
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
