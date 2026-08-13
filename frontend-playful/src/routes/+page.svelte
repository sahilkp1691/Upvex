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
		{ n: '1', title: 'Diagnose', body: 'An adaptive quiz maps what you know — per concept, not a vague topic score.' },
		{ n: '2', title: 'Find the root', body: 'We walk the prerequisite graph upstream to the concept actually blocking you.' },
		{ n: '3', title: 'Get the lesson', body: 'A short lesson is generated for your gaps, style, and tone — then cached.' },
		{ n: '4', title: 'Keep climbing', body: 'XP, streaks, and checkpoints make coming back feel like progress, not homework.' }
	];

	const useCases = [
		{ href: '/solutions#teams', label: 'Teams', body: 'Personal paths from your materials — people finish because it is not boring.' },
		{ href: '/solutions#schools', label: 'Schools', body: 'Trace students back to the foundation that never stuck.' },
		{ href: '/solutions#individuals', label: 'You', body: 'Skip what you know. Climb only what you need.' }
	];
</script>

<svelte:head>
	<title>Upvex — skills on an upward vector</title>
	<meta
		name="description"
		content="Diagnose the gap, get the exact lesson, keep the streak climbing. Learning that is not boring."
	/>
</svelte:head>

<div class="landing">
	<div class="blob" aria-hidden="true"></div>
	<MarketingNav />

	<section class="hero">
		<div class="hero-inner" use:reveal data-reveal>
			<span class="streak-pill">Fun to open every day</span>
			<h1>Skills on an upward vector.</h1>
			<p class="lead">
				Diagnose the gap, get the exact lesson, watch the streak build. Serious learning —
				without the boredom of another LMS.
			</p>
			<div class="cta-row">
				<a class="btn btn-primary" href="/auth">Start learning</a>
				<a class="btn" href="/#how-it-works">See how it works</a>
			</div>
			<div class="progress" aria-hidden="true">
				<span class="on"></span><span class="on"></span><span class="on"></span><span></span><span></span>
			</div>
		</div>
	</section>

	<section class="section" id="how-it-works">
		<div class="section-inner" use:reveal data-reveal>
			<p class="eyebrow">How it works</p>
			<h2>Four steps. One climb.</h2>
			<div class="steps">
				{#each steps as s (s.n)}
					<article class="step">
						<span class="n">{s.n}</span>
						<h3>{s.title}</h3>
						<p>{s.body}</p>
					</article>
				{/each}
			</div>
		</div>
	</section>

	<section class="section alt" id="product">
		<div class="section-inner" use:reveal data-reveal>
			<p class="eyebrow">Who it is for</p>
			<h2>Any subject. Same sticky loop.</h2>
			<div class="usecases">
				{#each useCases as u (u.href)}
					<a class="ucard" href={u.href}>
						<strong>{u.label}</strong>
						<span>{u.body}</span>
					</a>
				{/each}
			</div>
		</div>
	</section>

	<section class="section cta-band">
		<div class="section-inner" use:reveal data-reveal>
			<h2>Ready to climb?</h2>
			<p>Start with a free diagnostic. Keep the streak going.</p>
			<a class="btn btn-primary" href="/auth">Start learning</a>
		</div>
	</section>

	<MarketingFooter />
</div>

<style>
	.landing {
		position: relative;
		overflow: hidden;
		background: var(--bg);
		color: var(--text);
	}

	.blob {
		position: absolute;
		width: min(420px, 70vw);
		height: min(420px, 70vw);
		border-radius: 45% 55% 60% 40% / 50% 45% 55% 50%;
		background: var(--gold);
		opacity: 0.55;
		top: -120px;
		right: -80px;
		pointer-events: none;
		z-index: 0;
	}

	.hero,
	.section {
		position: relative;
		z-index: 1;
	}

	.hero {
		padding: clamp(48px, 10vw, 100px) clamp(20px, 4vw, 48px) 64px;
	}

	.hero-inner {
		max-width: 640px;
	}

	.streak-pill {
		display: inline-flex;
		padding: 6px 12px;
		border-radius: 999px;
		background: var(--warn);
		color: #fff;
		font-weight: 700;
		font-size: 12.5px;
		border: 2.5px solid var(--ink);
		margin-bottom: 18px;
	}

	h1 {
		font-size: clamp(2.4rem, 6vw, 3.6rem);
		line-height: 1.05;
		margin: 0 0 16px;
		max-width: 12ch;
	}

	.lead {
		font-size: 1.1rem;
		line-height: 1.5;
		color: var(--text-dim);
		max-width: 38ch;
		margin: 0 0 24px;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		gap: 12px;
		margin-bottom: 28px;
	}

	.progress {
		display: flex;
		gap: 6px;
	}

	.progress span {
		width: 36px;
		height: 10px;
		border-radius: 6px;
		background: var(--ink);
		opacity: 0.15;
	}

	.progress span.on {
		background: var(--accent);
		opacity: 1;
	}

	.section {
		padding: 56px clamp(20px, 4vw, 48px);
	}

	.section.alt {
		background: color-mix(in srgb, var(--gold) 14%, var(--bg));
		border-top: 3px solid var(--ink);
		border-bottom: 3px solid var(--ink);
	}

	.section-inner {
		max-width: 1100px;
		margin: 0 auto;
	}

	.eyebrow {
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--warn);
		margin: 0 0 8px;
	}

	h2 {
		font-size: clamp(1.6rem, 3vw, 2.1rem);
		margin: 0 0 24px;
	}

	.steps {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 14px;
	}

	.step {
		background: var(--bg-card);
		border: 2.5px solid var(--ink);
		border-radius: 16px;
		padding: 18px;
		box-shadow: 3px 3px 0 var(--ink);
	}

	.step .n {
		display: inline-grid;
		place-items: center;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background: var(--gold);
		border: 2px solid var(--ink);
		font-weight: 700;
		font-size: 13px;
		margin-bottom: 10px;
	}

	.step h3 {
		margin: 0 0 8px;
		font-size: 1.1rem;
	}

	.step p {
		margin: 0;
		font-size: 14px;
		color: var(--text-dim);
		line-height: 1.45;
	}

	.usecases {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
		gap: 14px;
	}

	.ucard {
		display: flex;
		flex-direction: column;
		gap: 8px;
		padding: 18px;
		background: var(--bg-card);
		border: 2.5px solid var(--ink);
		border-radius: 16px;
		box-shadow: 3px 3px 0 var(--ink);
		color: inherit;
		text-decoration: none;
	}

	.ucard:hover {
		text-decoration: none;
		transform: translate(-1px, -1px);
		box-shadow: 4px 4px 0 var(--ink);
	}

	.ucard strong {
		font-size: 1.05rem;
	}

	.ucard span {
		font-size: 14px;
		color: var(--text-dim);
		line-height: 1.45;
	}

	.cta-band {
		text-align: center;
	}

	.cta-band p {
		color: var(--text-dim);
		margin: 0 0 18px;
	}

	:global([data-reveal]) {
		opacity: 0;
		transform: translateY(16px);
		transition:
			opacity 0.5s ease,
			transform 0.5s ease;
	}

	:global([data-reveal].is-in) {
		opacity: 1;
		transform: none;
	}
</style>
