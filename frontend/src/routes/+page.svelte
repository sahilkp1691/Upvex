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

	const nodes = [
		{ id: 'sql', label: 'SQL core', x: 16, y: 58, z: 28, state: 'done' },
		{ id: 'join', label: 'Joins', x: 36, y: 40, z: 56, state: 'done' },
		{ id: 'win', label: 'Windows', x: 40, y: 74, z: -18, state: 'gap' },
		{ id: 'spark', label: 'Spark', x: 62, y: 28, z: 84, state: 'next' },
		{ id: 'opt', label: 'Optimise', x: 84, y: 46, z: 12, state: 'lock' },
		{ id: 'stream', label: 'Streaming', x: 72, y: 68, z: -36, state: 'lock' }
	];

	const edges = [
		['sql', 'join'],
		['sql', 'win'],
		['join', 'spark'],
		['win', 'spark'],
		['spark', 'opt'],
		['spark', 'stream']
	];

	const nodeById = Object.fromEntries(nodes.map((n) => [n.id, n]));

	let tiltX = $state(0);
	let tiltY = $state(0);
	let reduceMotion = $state(false);

	$effect(() => {
		const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
		reduceMotion = mq.matches;
		const onChange = () => (reduceMotion = mq.matches);
		mq.addEventListener('change', onChange);
		return () => mq.removeEventListener('change', onChange);
	});

	function onPointer(e) {
		if (reduceMotion) return;
		const r = e.currentTarget.getBoundingClientRect();
		const nx = (e.clientX - r.left) / r.width - 0.5;
		const ny = (e.clientY - r.top) / r.height - 0.5;
		tiltY = nx * 16;
		tiltX = -ny * 9;
	}

	function resetTilt() {
		tiltX = 0;
		tiltY = 0;
	}
</script>

<svelte:head>
	<title>Upvex — learning that points up</title>
	<meta
		name="description"
		content="Diagnose what you know, close the root gaps, climb with lessons built for you."
	/>
</svelte:head>

<div class="landing">
	<div class="grain" aria-hidden="true"></div>
	<div class="light" aria-hidden="true"></div>

	<header class="nav-pill">
		<Logo size={28} />
		<div class="nav-actions">
			<ThemeToggle />
			<a href="/auth" class="neo-btn">Sign in</a>
		</div>
	</header>

	<section class="hero">
		<div class="copy">
			<p class="eyebrow">Knowledge, mapped in depth</p>
			<h1>
				Skills on an
				<em>upward vector.</em>
			</h1>
			<p class="sub">
				Diagnose what you actually know, trace weaknesses to the root, then climb a graph of
				lessons built for you — not a course built for everyone.
			</p>
			<div class="cta-row">
				<a href="/auth" class="neo-cta">Start learning</a>
				<span class="cta-hint">Adaptive diagnosis. No static syllabus.</span>
			</div>
		</div>

		<div
			class="chamber"
			role="img"
			aria-label="Spatial knowledge graph of SQL and Spark concepts"
			onpointermove={onPointer}
			onpointerleave={resetTilt}
		>
			<div
				class="scene"
				class:still={reduceMotion}
				style="transform: rotateX({tiltX}deg) rotateY({tiltY}deg)"
			>
				<div class="floor"></div>
				<svg class="threads" viewBox="0 0 100 100" preserveAspectRatio="none">
					{#each edges as [a, b], i (a + b)}
						<line
							x1={nodeById[a].x}
							y1={nodeById[a].y}
							x2={nodeById[b].x}
							y2={nodeById[b].y}
							class="thread"
							style="--d: {0.35 + i * 0.12}s"
						/>
					{/each}
				</svg>

				{#each nodes as n (n.id)}
					<div
						class="node {n.state}"
						style="--x: {n.x}%; --y: {n.y}%; --z: {n.z}px; --delay: {n.z * 4}ms"
					>
						<span class="orb"></span>
						<span class="n-label">{n.label}</span>
					</div>
				{/each}

				<div class="callout gap-tag" style="--x: 40%; --y: 74%; --z: -18px">Root gap</div>
				<div class="callout next-tag" style="--x: 62%; --y: 28%; --z: 84px">Up next</div>
			</div>
		</div>
	</section>

	<section class="pillars">
		<article class="plate" style="--i: 0">
			<div class="plate-icon" aria-hidden="true">
				<svg viewBox="0 0 32 32" fill="none">
					<circle cx="10" cy="16" r="4" />
					<circle cx="22" cy="10" r="4" />
					<circle cx="22" cy="22" r="4" />
					<path d="M14 16h4M18.5 12.5l-5 2.5M18.5 19.5l-5-2.5" />
				</svg>
			</div>
			<span class="p-num">01</span>
			<h3>Real diagnosis</h3>
			<p>
				An adaptive quiz maps skill per concept, then walks the prerequisite graph upstream until
				it finds the foundation you are missing.
			</p>
		</article>
		<article class="plate" style="--i: 1">
			<div class="plate-icon" aria-hidden="true">
				<svg viewBox="0 0 32 32" fill="none">
					<path d="M8 22 V12 h6 v10 M18 22 V8 h6 v14" />
				</svg>
			</div>
			<span class="p-num">02</span>
			<h3>Lessons for you</h3>
			<p>
				Content is generated against your profile — skill, gaps, style, tone — not a static
				syllabus copied to every learner.
			</p>
		</article>
		<article class="plate" style="--i: 2">
			<div class="plate-icon" aria-hidden="true">
				<svg viewBox="0 0 32 32" fill="none">
					<path d="M8 20 L16 8 L24 20 L16 16 Z" />
				</svg>
			</div>
			<span class="p-num">03</span>
			<h3>Momentum that sticks</h3>
			<p>
				XP, streaks, levels, and badges for checkpoints that matter — like resolving a root gap
				and unlocking the next climb.
			</p>
		</article>
	</section>
</div>

<style>
	.landing {
		--font-display: 'Bricolage Grotesk', 'Plus Jakarta Sans', sans-serif;
		--neo: #1a2336;
		--neo-hi: #2a3854;
		--neo-lo: #0c111c;
		--neo-convex:
			10px 10px 22px var(--neo-lo), -8px -8px 18px var(--neo-hi),
			inset 1px 1px 0 color-mix(in srgb, white 8%, transparent);
		--neo-concave:
			inset 8px 8px 16px var(--neo-lo), inset -6px -6px 14px var(--neo-hi);
		--neo-press:
			inset 6px 6px 12px var(--neo-lo), inset -4px -4px 10px var(--neo-hi);
		--grid: color-mix(in srgb, var(--up) 22%, transparent);
		--landing-text: #e8eefc;
		--landing-dim: #8b9bb8;
		--landing-faint: #62728c;

		position: relative;
		min-height: 100vh;
		overflow: clip;
		color: var(--landing-text);
		background: var(--neo);
		isolation: isolate;
	}

	:global([data-theme='light']) .landing {
		--neo: #dce4f0;
		--neo-hi: #ffffff;
		--neo-lo: #b7c3d6;
		--neo-convex:
			10px 10px 20px var(--neo-lo), -8px -8px 18px var(--neo-hi),
			inset 1px 1px 0 rgba(255, 255, 255, 0.7);
		--neo-concave:
			inset 8px 8px 16px var(--neo-lo), inset -6px -6px 12px var(--neo-hi);
		--neo-press:
			inset 6px 6px 12px var(--neo-lo), inset -4px -4px 10px var(--neo-hi);
		--grid: color-mix(in srgb, var(--up) 28%, transparent);
		--landing-text: #152033;
		--landing-dim: #4c5d78;
		--landing-faint: #6e7d94;
	}

	.grain,
	.light {
		position: absolute;
		inset: 0;
		pointer-events: none;
		z-index: 0;
	}

	.light {
		background:
			radial-gradient(ellipse 70% 50% at 12% -8%, color-mix(in srgb, white 7%, transparent), transparent 52%),
			radial-gradient(ellipse 45% 40% at 88% 8%, color-mix(in srgb, var(--up) 10%, transparent), transparent 50%),
			radial-gradient(ellipse 40% 30% at 70% 100%, color-mix(in srgb, var(--accent) 8%, transparent), transparent 55%);
	}

	.grain {
		opacity: 0.045;
		mix-blend-mode: overlay;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
		background-size: 180px 180px;
	}

	.nav-pill {
		position: relative;
		z-index: 4;
		display: flex;
		justify-content: space-between;
		align-items: center;
		width: min(1120px, calc(100% - 32px));
		margin: 22px auto 0;
		padding: 10px 12px 10px 18px;
		border-radius: 999px;
		background: var(--neo);
		box-shadow: var(--neo-convex);
	}

	.nav-actions {
		display: flex;
		align-items: center;
		gap: 6px;
	}

	.nav-pill :global(.theme-toggle) {
		border-radius: 999px;
		box-shadow: var(--neo-concave);
		background: var(--neo);
		color: var(--landing-dim);
	}

	.nav-pill :global(.theme-toggle:hover) {
		color: var(--landing-text);
		background: var(--neo);
		border-color: transparent;
	}

	.neo-btn {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 8px 16px;
		border-radius: 999px;
		background: var(--neo);
		color: var(--landing-text);
		font-size: 13.5px;
		font-weight: 650;
		box-shadow: var(--neo-convex);
		text-decoration: none;
		transition:
			box-shadow 0.18s ease,
			transform 0.18s ease;
	}

	.neo-btn:hover {
		text-decoration: none;
		transform: translateY(-1px);
	}

	.neo-btn:active {
		box-shadow: var(--neo-press);
		transform: translateY(1px);
	}

	.hero {
		position: relative;
		z-index: 2;
		display: grid;
		grid-template-columns: minmax(0, 1fr) minmax(0, 1.15fr);
		gap: 28px 40px;
		align-items: center;
		width: min(1180px, calc(100% - 40px));
		margin: 0 auto;
		padding: 48px 0 36px;
		min-height: min(78vh, 760px);
	}

	.copy {
		position: relative;
		z-index: 2;
	}

	.eyebrow {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		margin: 0 0 18px;
		padding: 7px 14px;
		border-radius: 999px;
		background: var(--neo);
		box-shadow: var(--neo-concave);
		font-size: 11.5px;
		font-weight: 700;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--up);
		animation: rise 0.8s ease both;
	}

	h1 {
		font-family: var(--font-display);
		font-optical-sizing: auto;
		font-size: clamp(2.4rem, 5.4vw, 4.35rem);
		font-weight: 800;
		letter-spacing: -0.045em;
		line-height: 0.98;
		margin: 0 0 18px;
		color: var(--landing-text);
		text-shadow:
			2px 2px 4px var(--neo-lo),
			-1px -1px 2px var(--neo-hi);
		animation: rise 0.9s ease 0.06s both;
	}

	h1 em {
		font-style: italic;
		font-weight: 800;
		display: block;
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		text-shadow: none;
		filter: drop-shadow(0 8px 18px color-mix(in srgb, var(--up) 25%, transparent));
	}

	.sub {
		color: var(--landing-dim);
		font-size: 17px;
		line-height: 1.55;
		max-width: 42ch;
		margin: 0 0 28px;
		animation: rise 0.9s ease 0.12s both;
	}

	.cta-row {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 16px 20px;
		animation: rise 0.9s ease 0.18s both;
	}

	.neo-cta {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 16px 28px;
		border-radius: 18px;
		background: var(--neo);
		color: var(--landing-text);
		font-family: var(--font-display);
		font-size: 16.5px;
		font-weight: 800;
		letter-spacing: -0.02em;
		text-decoration: none;
		box-shadow:
			var(--neo-convex),
			inset 0 0 0 1px color-mix(in srgb, var(--up) 38%, transparent),
			0 0 28px color-mix(in srgb, var(--up) 16%, transparent);
		transition:
			box-shadow 0.18s ease,
			transform 0.18s ease;
	}

	.neo-cta:hover {
		text-decoration: none;
		transform: translateY(-2px);
		box-shadow:
			12px 14px 26px var(--neo-lo),
			-8px -8px 18px var(--neo-hi),
			inset 0 0 0 1px color-mix(in srgb, var(--up) 55%, transparent),
			0 0 36px color-mix(in srgb, var(--up) 22%, transparent);
	}

	.neo-cta:active {
		transform: translateY(1px);
		box-shadow: var(--neo-press);
	}

	.cta-hint {
		color: var(--landing-faint);
		font-size: 13px;
		max-width: 16ch;
		line-height: 1.35;
	}

	.chamber {
		perspective: 1400px;
		perspective-origin: 50% 42%;
		height: min(560px, 72vw);
		animation: chamber-in 1.15s cubic-bezier(0.16, 1, 0.3, 1) 0.1s both;
	}

	.scene {
		position: relative;
		width: 100%;
		height: 100%;
		transform-style: preserve-3d;
		transition: transform 0.22s ease-out;
	}

	.scene.still {
		transform: none !important;
		transition: none;
	}

	.floor {
		position: absolute;
		left: 2%;
		top: 38%;
		width: 96%;
		height: 78%;
		border-radius: 28px;
		transform: rotateX(68deg) translateZ(-48px);
		transform-origin: center;
		background:
			linear-gradient(var(--grid) 1px, transparent 1px),
			linear-gradient(90deg, var(--grid) 1px, transparent 1px);
		background-size: 34px 34px;
		mask-image: radial-gradient(ellipse at 50% 30%, black 12%, transparent 72%);
		box-shadow: 0 40px 80px rgba(0, 0, 0, 0.28);
	}

	.threads {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		overflow: visible;
		transform: translateZ(8px);
	}

	.thread {
		stroke: color-mix(in srgb, var(--up) 70%, var(--accent));
		stroke-width: 0.45;
		stroke-linecap: round;
		fill: none;
		opacity: 0.7;
		stroke-dasharray: 80;
		stroke-dashoffset: 80;
		animation: thread-draw 1.6s ease forwards;
		animation-delay: var(--d);
	}

	.node {
		position: absolute;
		left: var(--x);
		top: var(--y);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		transform: translate3d(-50%, -50%, var(--z));
		transform-style: preserve-3d;
		animation: float 6.4s ease-in-out infinite;
		animation-delay: var(--delay);
	}

	.orb {
		width: 54px;
		height: 54px;
		border-radius: 50%;
		background:
			radial-gradient(circle at 32% 28%, color-mix(in srgb, white 26%, var(--neo)), var(--neo) 58%);
		box-shadow: var(--neo-convex);
	}

	.n-label {
		font-size: 11.5px;
		font-weight: 700;
		letter-spacing: 0.02em;
		color: var(--landing-dim);
		white-space: nowrap;
		padding: 4px 9px;
		border-radius: 999px;
		background: var(--neo);
		box-shadow: var(--neo-convex);
	}

	.node.done .orb {
		background:
			radial-gradient(circle at 32% 28%, color-mix(in srgb, white 30%, var(--up)), color-mix(in srgb, var(--up) 45%, var(--neo)) 62%);
		box-shadow:
			var(--neo-convex),
			0 0 18px color-mix(in srgb, var(--up) 28%, transparent);
	}

	.node.gap .orb {
		background:
			radial-gradient(circle at 32% 28%, color-mix(in srgb, white 28%, var(--warn)), color-mix(in srgb, var(--warn) 40%, var(--neo)) 62%);
		box-shadow:
			var(--neo-convex),
			0 0 16px color-mix(in srgb, var(--warn) 30%, transparent);
	}

	.node.next {
		z-index: 2;
		animation-duration: 4.6s;
	}

	.node.next .orb {
		width: 66px;
		height: 66px;
		background:
			radial-gradient(circle at 32% 28%, color-mix(in srgb, white 34%, var(--up)), var(--up) 70%);
		box-shadow:
			var(--neo-convex),
			0 0 0 6px color-mix(in srgb, var(--up) 18%, transparent),
			0 0 32px color-mix(in srgb, var(--up) 40%, transparent);
	}

	.node.next .n-label {
		color: var(--up);
	}

	.node.lock .orb {
		width: 42px;
		height: 42px;
		box-shadow: var(--neo-concave);
		opacity: 0.72;
	}

	.node.lock .n-label {
		opacity: 0.65;
		box-shadow: var(--neo-concave);
	}

	.callout {
		position: absolute;
		left: var(--x);
		top: var(--y);
		transform: translate3d(28px, -42px, var(--z));
		padding: 5px 10px;
		border-radius: 999px;
		font-size: 10.5px;
		font-weight: 800;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		background: var(--neo);
		box-shadow: var(--neo-convex);
		white-space: nowrap;
	}

	.gap-tag {
		color: var(--warn);
		transform: translate3d(30px, 28px, var(--z));
	}

	.next-tag {
		color: var(--up);
	}

	.pillars {
		position: relative;
		z-index: 2;
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 22px;
		width: min(1180px, calc(100% - 40px));
		margin: 8px auto 0;
		padding: 12px 0 72px;
	}

	.plate {
		padding: 26px 24px 28px;
		border-radius: 28px;
		background: var(--neo);
		box-shadow: var(--neo-convex);
		transform: rotateY(calc((var(--i) - 1) * 3deg)) translateZ(calc((1 - var(--i)) * 12px));
		animation: rise 0.9s ease calc(0.28s + var(--i) * 0.08s) both;
	}

	.plate-icon {
		width: 52px;
		height: 52px;
		border-radius: 16px;
		display: grid;
		place-items: center;
		margin-bottom: 18px;
		background: var(--neo);
		box-shadow: var(--neo-concave);
		color: var(--up);
	}

	.plate-icon svg {
		width: 26px;
		height: 26px;
		stroke: currentColor;
		stroke-width: 1.8;
		stroke-linecap: round;
		stroke-linejoin: round;
	}

	.p-num {
		display: block;
		font-family: var(--font-display);
		font-weight: 800;
		font-size: 12px;
		letter-spacing: 0.12em;
		color: var(--up);
		margin-bottom: 8px;
	}

	.plate h3 {
		font-family: var(--font-display);
		font-size: 1.28rem;
		letter-spacing: -0.03em;
		margin-bottom: 8px;
		color: var(--landing-text);
	}

	.plate p {
		margin: 0;
		font-size: 14.5px;
		line-height: 1.5;
		color: var(--landing-dim);
	}

	@keyframes rise {
		from {
			opacity: 0;
			transform: translateY(18px);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}

	@keyframes chamber-in {
		from {
			opacity: 0;
			transform: translateY(28px) scale(0.96);
		}
		to {
			opacity: 1;
			transform: none;
		}
	}

	@keyframes thread-draw {
		to {
			stroke-dashoffset: 0;
		}
	}

	@keyframes float {
		0%,
		100% {
			translate: 0 0;
		}
		50% {
			translate: 0 -9px;
		}
	}

	@media (max-width: 960px) {
		.hero {
			grid-template-columns: 1fr;
			min-height: unset;
			padding-top: 36px;
			gap: 12px;
		}

		.copy {
			text-align: left;
		}

		.chamber {
			height: min(420px, 88vw);
		}

		.pillars {
			grid-template-columns: 1fr;
		}

		.plate {
			transform: none;
		}
	}

	@media (max-width: 560px) {
		.nav-pill {
			width: calc(100% - 20px);
			margin-top: 14px;
			padding: 8px 8px 8px 14px;
		}

		h1 {
			font-size: 2.35rem;
		}

		.cta-hint {
			max-width: none;
		}

		.callout {
			display: none;
		}

		.node .n-label {
			font-size: 10px;
		}

		.orb {
			width: 44px;
			height: 44px;
		}

		.node.next .orb {
			width: 54px;
			height: 54px;
		}
	}

	@media (prefers-reduced-motion: reduce) {
		.eyebrow,
		h1,
		.sub,
		.cta-row,
		.chamber,
		.plate,
		.node,
		.thread {
			animation: none;
		}

		.scene {
			transition: none;
		}
	}
</style>
