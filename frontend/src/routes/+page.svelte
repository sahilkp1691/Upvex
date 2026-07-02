<script>
	import { goto } from '$app/navigation';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';

	$effect(() => {
		if ($userLoaded && $currentUser) {
			goto($currentUser.onboarded ? '/topics' : '/onboarding');
		}
	});
</script>

<svelte:head><title>Upvex — learning that points up</title></svelte:head>

<div class="landing">
	<header class="top">
		<Logo size={28} />
		<a href="/auth" class="btn">Sign in</a>
	</header>

	<section class="hero">
		<h1>Your skills, on an <span class="grad">upward vector</span>.</h1>
		<p class="sub">
			Upvex diagnoses what you actually know, finds the foundational gaps holding you back, and
			generates lessons built for you — not a fixed course served to everyone.
		</p>
		<a href="/auth" class="btn btn-primary btn-lg">Start learning</a>
	</section>

	<section class="features">
		<div class="card">
			<h3>Real diagnosis</h3>
			<p class="muted">
				An adaptive quiz maps your level per concept, then traces weak spots back through the
				prerequisite graph to the root cause.
			</p>
		</div>
		<div class="card">
			<h3>Lessons made for you</h3>
			<p class="muted">
				Content is generated live against your profile — your level, your gaps, your learning
				style — not pulled from a static library.
			</p>
		</div>
		<div class="card">
			<h3>Momentum that sticks</h3>
			<p class="muted">
				XP, streaks, and milestone badges tied to meaningful checkpoints, like resolving a root gap
				that unlocks everything above it.
			</p>
		</div>
	</section>
</div>

<style>
	.landing {
		max-width: 1080px;
		margin: 0 auto;
		padding: 24px;
	}

	.top {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.hero {
		text-align: center;
		padding: 110px 20px 80px;
	}

	h1 {
		font-size: 46px;
		max-width: 700px;
		margin: 0 auto 20px;
	}

	.grad {
		background: linear-gradient(100deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}

	.sub {
		color: var(--text-dim);
		font-size: 18px;
		max-width: 580px;
		margin: 0 auto 34px;
	}

	.btn-lg {
		padding: 13px 30px;
		font-size: 16px;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
		gap: 18px;
		padding-bottom: 80px;
	}
</style>
