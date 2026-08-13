<script>
	import Logo from '$lib/Logo.svelte';
	const year = new Date().getFullYear();
</script>

<footer class="mfoot">
	<div class="mfoot-rule" aria-hidden="true">
		{#each Array(48) as _, i (i)}
			<span class="tick" class:major={i % 6 === 0}></span>
		{/each}
	</div>

	<div class="mfoot-top">
		<div class="mfoot-brand">
			<Logo size={24} />
			<p>Diagnose the gap. Trace the root. Generate the lesson. Climb.</p>
			<span class="mfoot-stamp">STATUS: EARLY DEVELOPMENT</span>
		</div>

		<div class="mfoot-cols">
			<div class="mfoot-col">
				<h4>01 / Product</h4>
				<a href="/#how-it-works">How it works</a>
				<a href="/#product">What&rsquo;s inside</a>
				<a href="/auth">Sign in</a>
			</div>
			<div class="mfoot-col">
				<h4>02 / Solutions</h4>
				<a href="/solutions#teams">Teams &amp; companies</a>
				<a href="/solutions#schools">Schools &amp; nonprofits</a>
				<a href="/solutions#individuals">Individual learners</a>
			</div>
			<div class="mfoot-col">
				<h4>03 / Company</h4>
				<a href="/pitch">Pitch overview</a>
				<a href="mailto:hello@upvex.io">Get in touch</a>
			</div>
		</div>
	</div>

	<div class="mfoot-bottom">
		<span>&copy; {year} UPVEX</span>
		<span class="mfoot-coord">SKILLS ON AN UPWARD VECTOR</span>
	</div>
</footer>

<style>
	.mfoot {
		--sig: var(--mkt-signal, var(--warn));
		border-top: 1px solid var(--border);
		padding: 0 clamp(20px, 4vw, 48px) 28px;
	}

	.mfoot-rule {
		display: flex;
		align-items: flex-end;
		gap: 6px;
		height: 22px;
		max-width: 1180px;
		margin: 0 auto;
		padding: 10px 0;
	}

	.tick {
		width: 1px;
		height: 6px;
		background: var(--border-strong);
		flex-shrink: 0;
	}

	.tick.major {
		height: 11px;
		background: var(--sig);
		opacity: 0.6;
	}

	.mfoot-top {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 40px;
		max-width: 1180px;
		margin: 0 auto;
		padding-top: 28px;
	}

	.mfoot-brand {
		max-width: 280px;
	}

	.mfoot-brand p {
		margin: 14px 0 16px;
		color: var(--text-faint);
		font-size: 13.5px;
		line-height: 1.5;
	}

	.mfoot-stamp {
		display: inline-flex;
		padding: 5px 9px;
		border: 1px solid var(--border-strong);
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.06em;
		color: var(--text-faint);
	}

	.mfoot-cols {
		display: flex;
		gap: 56px;
		flex-wrap: wrap;
	}

	.mfoot-col {
		display: flex;
		flex-direction: column;
		gap: 11px;
		min-width: 150px;
	}

	.mfoot-col h4 {
		margin: 0 0 3px;
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.04em;
		color: var(--sig);
	}

	.mfoot-col a {
		color: var(--text-dim);
		font-size: 14px;
	}

	.mfoot-col a:hover {
		color: var(--text);
		text-decoration: none;
	}

	.mfoot-bottom {
		display: flex;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: 10px;
		max-width: 1180px;
		margin: 40px auto 0;
		padding-top: 20px;
		border-top: 1px solid var(--border);
		font-family: var(--mkt-mono, 'JetBrains Mono', monospace);
		color: var(--text-faint);
		font-size: 11.5px;
		letter-spacing: 0.03em;
	}
</style>
