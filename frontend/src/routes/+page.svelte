<script>
	import { goto } from '$app/navigation';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import ThemeToggle from '$lib/ThemeToggle.svelte';

	$effect(() => {
		if ($userLoaded && $currentUser) {
			goto($currentUser.onboarded ? '/topics' : '/onboarding');
		}
	});
</script>

<svelte:head><title>Upvex — learning that points up</title></svelte:head>

<div class="landing mesh-bg">
	<header class="top">
		<Logo size={32} />
		<div class="top-actions">
			<ThemeToggle />
			<a href="/auth" class="btn btn-sm">Sign in</a>
		</div>
	</header>

	<section class="hero">
		<div class="hero-visual" aria-hidden="true">
			<svg class="map-bg" viewBox="0 0 640 280" fill="none">
				<path
					class="map-edge"
					d="M120 70 C180 70, 200 140, 260 140 S340 70, 400 70 S480 160, 540 160"
				/>
				<path class="map-edge soft" d="M120 70 C160 110, 180 200, 260 210 S360 180, 400 160" />
				<path class="map-edge soft" d="M260 140 C300 140, 320 210, 400 210 S480 160, 540 160" />
				<circle class="map-node done" cx="120" cy="70" r="14" />
				<circle class="map-node done" cx="260" cy="140" r="14" />
				<circle class="map-node next" cx="400" cy="70" r="16" />
				<circle class="map-node" cx="400" cy="210" r="12" />
				<circle class="map-node lock" cx="540" cy="160" r="12" />
			</svg>
			<div class="vector">
				<svg viewBox="0 0 24 24" fill="none">
					<path d="M12 3 L20 19 L12 14.5 L4 19 Z" fill="url(#landGrad)" />
					<defs>
						<linearGradient id="landGrad" x1="4" y1="19" x2="20" y2="3" gradientUnits="userSpaceOnUse">
							<stop offset="0" stop-color="#3d8bfd" />
							<stop offset="1" stop-color="#2dd4a0" />
						</linearGradient>
					</defs>
				</svg>
			</div>
		</div>
		<p class="brand-mark">Upvex</p>
		<h1>Skills on an upward vector.</h1>
		<p class="sub">
			Diagnose what you know, close the root gaps, climb with lessons built for you.
		</p>
		<a href="/auth" class="btn btn-primary btn-lg">Start learning</a>
	</section>

	<section class="pillars">
		<div class="pillar">
			<span class="p-num">01</span>
			<h3>Real diagnosis</h3>
			<p class="muted">
				An adaptive quiz maps your skill per concept, then traces weaknesses upstream to the
				foundation.
			</p>
		</div>
		<div class="pillar">
			<span class="p-num">02</span>
			<h3>Lessons for you</h3>
			<p class="muted">
				Content is generated against your profile — skill, gaps, style — not a static course for
				everyone.
			</p>
		</div>
		<div class="pillar">
			<span class="p-num">03</span>
			<h3>Momentum that sticks</h3>
			<p class="muted">
				XP, streaks, levels, and badges for checkpoints that matter — like resolving a root gap.
			</p>
		</div>
	</section>
</div>

<style>
	.landing {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	.top {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 20px 28px;
		max-width: 1120px;
		margin: 0 auto;
		width: 100%;
	}

	.top-actions {
		display: flex;
		align-items: center;
		gap: 8px;
	}

	.hero {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		text-align: center;
		padding: 48px 24px 72px;
		position: relative;
		min-height: min(78vh, 720px);
	}

	.hero-visual {
		position: relative;
		width: min(640px, 92vw);
		height: clamp(140px, 28vw, 220px);
		margin-bottom: 8px;
		display: grid;
		place-items: center;
	}

	.map-bg {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		opacity: 0.9;
	}

	.map-edge {
		stroke: color-mix(in srgb, var(--up) 55%, var(--border-strong));
		stroke-width: 2.2;
		stroke-linecap: round;
		fill: none;
		stroke-dasharray: 420;
		stroke-dashoffset: 420;
		animation: path-reveal 2.8s ease forwards;
	}

	.map-edge.soft {
		stroke: var(--border-strong);
		stroke-width: 1.5;
		animation-delay: 0.35s;
	}

	.map-node {
		fill: var(--bg-card);
		stroke: var(--border-strong);
		stroke-width: 2;
	}

	.map-node.done {
		fill: color-mix(in srgb, var(--up) 35%, var(--bg-card));
		stroke: var(--up);
	}

	.map-node.next {
		fill: color-mix(in srgb, var(--up) 55%, var(--bg-card));
		stroke: var(--up);
		animation: next-glow 2.4s ease-in-out infinite;
	}

	.map-node.lock {
		opacity: 0.45;
	}

	@keyframes path-reveal {
		to {
			stroke-dashoffset: 0;
		}
	}

	@keyframes next-glow {
		0%,
		100% {
			filter: drop-shadow(0 0 0 transparent);
		}
		50% {
			filter: drop-shadow(0 0 10px color-mix(in srgb, var(--up) 60%, transparent));
		}
	}

	.vector {
		position: relative;
		z-index: 1;
		width: min(88px, 16vw);
		animation: vector-drift 6s ease-in-out infinite;
		filter: drop-shadow(0 12px 40px rgba(45, 212, 160, 0.25));
	}

	.vector svg {
		width: 100%;
		height: auto;
		display: block;
	}

	.brand-mark {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: clamp(2.8rem, 8vw, 4.6rem);
		letter-spacing: -0.04em;
		margin: 0 0 12px;
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		line-height: 1;
	}

	h1 {
		font-size: clamp(1.35rem, 3.2vw, 1.85rem);
		font-weight: 650;
		max-width: 520px;
		margin: 0 auto 14px;
		color: var(--text-dim);
		letter-spacing: -0.02em;
	}

	.sub {
		color: var(--text-faint);
		font-size: 16.5px;
		max-width: 440px;
		margin: 0 auto 28px;
		line-height: 1.5;
	}

	.btn-lg {
		padding: 14px 32px;
		font-size: 16px;
	}

	.pillars {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 0;
		max-width: 1080px;
		margin: 0 auto;
		width: 100%;
		padding: 0 24px 80px;
		border-top: 1px solid var(--border);
	}

	.pillar {
		padding: 36px 28px 8px;
		border-right: 1px solid var(--border);
	}

	.pillar:last-child {
		border-right: none;
	}

	.p-num {
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 13px;
		letter-spacing: 0.08em;
		color: var(--up);
		display: block;
		margin-bottom: 10px;
	}

	.pillar h3 {
		font-size: 1.15rem;
		margin-bottom: 8px;
	}

	.pillar p {
		margin: 0;
		font-size: 14.5px;
		line-height: 1.5;
	}

	@media (max-width: 780px) {
		.pillars {
			grid-template-columns: 1fr;
		}

		.pillar {
			border-right: none;
			border-bottom: 1px solid var(--border);
			padding: 28px 8px;
		}

		.pillar:last-child {
			border-bottom: none;
		}
	}
</style>
