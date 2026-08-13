<script>
	import Logo from '$lib/Logo.svelte';
	const year = new Date().getFullYear();
</script>

<footer class="mfoot">
	<div class="mfoot-top">
		<div class="mfoot-brand">
			<div class="logo-wrap"><Logo size={24} /></div>
			<p>Training people finish — personal paths from your materials, with a loop that is not boring.</p>
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
		<span>Competence delivered through engagement</span>
	</div>
</footer>

<style>
	.mfoot {
		border-top: 1px solid var(--border);
		padding: 40px clamp(20px, 4vw, 48px) 28px;
		background: var(--bg-elevated);
	}

	.mfoot-top {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 28px;
		max-width: 1100px;
		margin: 0 auto 28px;
	}

	.logo-wrap {
		font-family: var(--font-display);
	}

	.mfoot-brand {
		max-width: 300px;
	}

	.mfoot-brand p {
		margin: 12px 0 0;
		color: var(--text-dim);
		font-size: 14px;
		line-height: 1.5;
	}

	.mfoot-cols {
		display: flex;
		flex-wrap: wrap;
		gap: 40px;
	}

	.mfoot-col {
		display: flex;
		flex-direction: column;
		gap: 8px;
		min-width: 140px;
	}

	.mfoot-col h4 {
		margin: 0 0 4px;
		font-size: 12px;
		font-weight: 700;
		letter-spacing: 0.04em;
		text-transform: uppercase;
		color: var(--text-faint);
		font-family: var(--font);
	}

	.mfoot-col a {
		color: var(--text-dim);
		font-size: 13.5px;
	}

	.mfoot-col a:hover {
		color: var(--accent);
	}

	.mfoot-bottom {
		max-width: 1100px;
		margin: 0 auto;
		display: flex;
		justify-content: space-between;
		gap: 12px;
		flex-wrap: wrap;
		padding-top: 18px;
		border-top: 1px solid var(--border);
		font-size: 12.5px;
		color: var(--text-faint);
	}
</style>
