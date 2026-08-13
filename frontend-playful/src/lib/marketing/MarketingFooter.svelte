<script>
	import Logo from '$lib/Logo.svelte';
	const year = new Date().getFullYear();
</script>

<footer class="mfoot">
	<div class="mfoot-top">
		<div class="mfoot-brand">
			<Logo size={24} />
			<p>Diagnose the gap. Get the lesson. Keep the streak climbing.</p>
		</div>

		<div class="mfoot-cols">
			<div class="mfoot-col">
				<h4>Product</h4>
				<a href="/#how-it-works">How it works</a>
				<a href="/#product">What&rsquo;s inside</a>
				<a href="/auth">Sign in</a>
			</div>
			<div class="mfoot-col">
				<h4>Solutions</h4>
				<a href="/solutions#teams">Teams &amp; companies</a>
				<a href="/solutions#schools">Schools &amp; nonprofits</a>
				<a href="/solutions#individuals">Individual learners</a>
			</div>
			<div class="mfoot-col">
				<h4>Company</h4>
				<a href="/pitch">Pitch overview</a>
				<a href="mailto:hello@upvex.io">Get in touch</a>
			</div>
		</div>
	</div>

	<div class="mfoot-bottom">
		<span>&copy; {year} Upvex</span>
		<span class="chip">Skills on an upward vector</span>
	</div>
</footer>

<style>
	.mfoot {
		border-top: 3px solid var(--ink);
		padding: 36px clamp(20px, 4vw, 48px) 28px;
		background: color-mix(in srgb, var(--gold) 18%, var(--bg));
	}

	.mfoot-top {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 28px;
		max-width: 1100px;
		margin: 0 auto 28px;
	}

	.mfoot-brand {
		max-width: 280px;
	}

	.mfoot-brand p {
		margin: 12px 0 0;
		color: var(--text-dim);
		font-size: 14px;
		line-height: 1.45;
	}

	.mfoot-cols {
		display: flex;
		flex-wrap: wrap;
		gap: 36px;
	}

	.mfoot-col {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-width: 140px;
	}

	.mfoot-col h4 {
		margin: 0 0 4px;
		font-size: 13px;
		font-weight: 700;
	}

	.mfoot-col a {
		color: var(--text-dim);
		font-size: 13.5px;
		font-weight: 500;
	}

	.mfoot-col a:hover {
		color: var(--text);
	}

	.mfoot-bottom {
		max-width: 1100px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
		padding-top: 18px;
		border-top: 2px solid color-mix(in srgb, var(--ink) 25%, transparent);
		font-size: 12.5px;
		color: var(--text-faint);
		font-weight: 600;
	}

	.chip {
		display: inline-flex;
		padding: 4px 10px;
		border-radius: 999px;
		border: 2px solid var(--ink);
		background: var(--bg-card);
		color: var(--text);
		font-size: 11.5px;
	}
</style>
