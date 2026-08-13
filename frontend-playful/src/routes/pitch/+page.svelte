<script>
	import MarketingNav from '$lib/marketing/MarketingNav.svelte';
	import MarketingFooter from '$lib/marketing/MarketingFooter.svelte';
	import { reveal } from '$lib/marketing/reveal.js';

	const audience = [
		{
			label: 'Teams & companies',
			body: 'Personal diagnostics + material upload → curated course graphs people finish.',
			href: '/solutions#teams'
		},
		{
			label: 'Schools & nonprofits',
			body: 'Root-cause remediation with streaks that keep students coming back.',
			href: '/solutions#schools'
		},
		{
			label: 'Individual learners',
			body: 'Free diagnostic, then a climb that skips what you already know.',
			href: '/solutions#individuals'
		}
	];

	const roadmap = [
		{ label: 'Now', body: 'SQL and Spark live. Full diagnose → lesson → streak loop.' },
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
		<span class="pill">Early development</span>
		<h1>Upvex</h1>
		<p class="lede">Serious competence. Sticky daily experience. Not another boring LMS.</p>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Problem</p>
		<h2>Static training bores people — and misses the gap.</h2>
		<p>Everyone gets the same course. Completion drops. The real upstream weakness never gets fixed.</p>
	</section>

	<section class="slide" use:reveal data-reveal>
		<p class="eyebrow">Solution</p>
		<h2>Diagnose → root gap → short lesson → streak.</h2>
		<p>
			A prerequisite graph powers an adaptive diagnostic. Lessons are generated for the person.
			Gamification makes coming back feel like climbing, not compliance.
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
				<div class="card-link static">
					<strong>{r.label}</strong>
					<span>{r.body}</span>
				</div>
			{/each}
		</div>
	</section>

	<section class="slide ask" use:reveal data-reveal>
		<p class="eyebrow">Ask</p>
		<h2>Help shape the graph.</h2>
		<p>If this problem is familiar, we would like to talk — pilots, design partners, early teams.</p>
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
		max-width: 820px;
		margin: 0 auto;
		border-bottom: 3px solid var(--ink);
	}

	.cover h1 {
		font-size: clamp(3rem, 10vw, 5rem);
		margin: 12px 0 16px;
		transform: rotate(-1deg);
	}

	.pill {
		display: inline-flex;
		padding: 5px 12px;
		border-radius: 999px;
		background: var(--gold);
		border: 2.5px solid var(--ink);
		font-weight: 700;
		font-size: 12px;
	}

	.lede,
	.slide p {
		color: var(--text-dim);
		font-size: 1.05rem;
		line-height: 1.5;
		max-width: 42ch;
	}

	.eyebrow {
		font-size: 12px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.06em;
		color: var(--warn);
		margin: 0 0 10px;
	}

	h2 {
		font-size: clamp(1.5rem, 3.5vw, 2rem);
		margin: 0 0 12px;
		line-height: 1.15;
	}

	.grid {
		display: grid;
		gap: 12px;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
	}

	.card-link {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding: 16px;
		background: var(--bg-card);
		border: 2.5px solid var(--ink);
		border-radius: 14px;
		box-shadow: 3px 3px 0 var(--ink);
		color: inherit;
		text-decoration: none;
	}

	.card-link.static {
		cursor: default;
	}

	.card-link span {
		font-size: 13.5px;
		color: var(--text-dim);
		line-height: 1.45;
	}

	.ask {
		text-align: left;
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
