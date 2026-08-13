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
		{ n: '01', title: 'Diagnose', body: 'Map each person against your stack or curated materials — not a shared deck.' },
		{ n: '02', title: 'Trace the root', body: 'Walk the prerequisite graph to the upstream concept causing the gap.' },
		{ n: '03', title: 'Short lessons', body: 'Generate focused content against the learner profile, then cache it.' },
		{ n: '04', title: 'Completion', body: 'A sticky daily loop so people finish — engagement as the delivery system.' }
	];

	const proofs = [
		{ k: 'Personal path', v: 'per employee, not one deck' },
		{ k: 'Your materials', v: 'curated into a graph' },
		{ k: 'Daily loop', v: 'people come back to' }
	];
</script>

<svelte:head>
	<title>Upvex — training people actually finish</title>
	<meta
		name="description"
		content="Diagnose each employee, curate courses from your materials, and keep learning sticky enough that completion stops being the hard part."
	/>
</svelte:head>

<div class="landing">
	<MarketingNav />

	<section class="hero">
		<div class="hero-inner" use:reveal data-reveal>
			<p class="eyebrow">For teams &amp; companies</p>
			<div class="accent-line"></div>
			<h1>Training people actually finish.</h1>
			<p class="lead">
				Diagnose each employee against your stack or your own materials. Short personal lessons —
				sticky enough that completion stops being the hard part.
			</p>
			<div class="cta-row">
				<a class="btn btn-primary" href="mailto:hello@upvex.io?subject=Upvex%20walkthrough">Book a walkthrough</a>
				<a class="btn" href="/#how-it-works">See how it works</a>
			</div>
			<div class="proof">
				{#each proofs as p (p.k)}
					<div>
						<strong>{p.k}</strong>
						<span>{p.v}</span>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<section class="section" id="how-it-works">
		<div class="wrap" use:reveal data-reveal>
			<p class="eyebrow">How it works</p>
			<h2>Competence delivered through engagement</h2>
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

	<section class="section tint" id="product">
		<div class="wrap" use:reveal data-reveal>
			<p class="eyebrow">Deploy</p>
			<h2>Same engine. Team, school, or individual.</h2>
			<div class="links">
				<a href="/solutions#teams">Teams &amp; companies</a>
				<a href="/solutions#schools">Schools &amp; nonprofits</a>
				<a href="/solutions#individuals">Individual learners</a>
			</div>
		</div>
	</section>

	<section class="section cta">
		<div class="wrap" use:reveal data-reveal>
			<h2>Ready when your team is.</h2>
			<p>Walk through a diagnostic on your materials — or start with SQL and Spark.</p>
			<a class="btn btn-primary" href="mailto:hello@upvex.io">Get in touch</a>
		</div>
	</section>

	<MarketingFooter />
</div>

<style>
	.landing {
		background: var(--bg);
		color: var(--text);
	}

	.hero {
		padding: clamp(56px, 10vw, 96px) clamp(20px, 4vw, 48px) 72px;
		background:
			radial-gradient(ellipse 40% 50% at 90% 10%, color-mix(in srgb, var(--gold) 22%, transparent), transparent 70%),
			radial-gradient(ellipse 35% 40% at 100% 80%, color-mix(in srgb, var(--accent) 12%, transparent), transparent 70%),
			var(--bg);
	}

	.hero-inner {
		max-width: 640px;
	}

	.eyebrow {
		font-size: 11px;
		font-weight: 700;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--warn);
		margin: 0 0 10px;
	}

	.accent-line {
		width: 28px;
		height: 3px;
		background: var(--gold);
		border-radius: 2px;
		margin-bottom: 16px;
	}

	h1 {
		font-family: var(--font-display);
		font-size: clamp(2.2rem, 5vw, 3.2rem);
		font-weight: 600;
		line-height: 1.1;
		margin: 0 0 14px;
		letter-spacing: -0.02em;
	}

	.lead {
		font-size: 1.05rem;
		line-height: 1.55;
		color: var(--text-dim);
		max-width: 42ch;
		margin: 0 0 22px;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		margin-bottom: 28px;
	}

	.proof {
		display: flex;
		flex-wrap: wrap;
		gap: 20px;
		padding-top: 20px;
		border-top: 1px solid var(--border);
	}

	.proof strong {
		display: block;
		font-family: var(--font-display);
		font-size: 15px;
		font-weight: 600;
		margin-bottom: 2px;
	}

	.proof span {
		font-size: 12.5px;
		color: var(--text-faint);
	}

	.section {
		padding: 56px clamp(20px, 4vw, 48px);
	}

	.section.tint {
		background: var(--bg-elevated);
		border-top: 1px solid var(--border);
		border-bottom: 1px solid var(--border);
	}

	.wrap {
		max-width: 1000px;
		margin: 0 auto;
	}

	h2 {
		font-family: var(--font-display);
		font-size: clamp(1.5rem, 3vw, 2rem);
		font-weight: 600;
		margin: 0 0 24px;
	}

	.steps {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 12px;
	}

	.step {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		padding: 16px;
	}

	.step .n {
		font-size: 11px;
		font-weight: 700;
		color: var(--accent);
		letter-spacing: 0.06em;
	}

	.step h3 {
		font-family: var(--font-display);
		font-size: 1.05rem;
		font-weight: 600;
		margin: 6px 0 8px;
	}

	.step p {
		margin: 0;
		font-size: 13.5px;
		color: var(--text-dim);
		line-height: 1.45;
	}

	.links {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
	}

	.links a {
		padding: 10px 14px;
		border-radius: 8px;
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text);
		font-weight: 600;
		font-size: 13.5px;
		text-decoration: none;
	}

	.links a:hover {
		border-color: var(--accent);
		color: var(--accent);
	}

	.cta {
		text-align: left;
	}

	.cta p {
		color: var(--text-dim);
		margin: 0 0 16px;
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
