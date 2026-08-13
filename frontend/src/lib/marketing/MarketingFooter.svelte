<script>
	import Logo from '$lib/Logo.svelte';
	const year = new Date().getFullYear();
</script>

<footer class="mfoot">
	<div class="mfoot-top">
		<div class="mfoot-brand">
			<Logo size={24} />
			<p>Diagnose the gap. Generate the lesson. Climb.</p>
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
		<span>&copy; {year} Upvex &mdash; early development.</span>
	</div>
</footer>

<style>
	.mfoot {
		border-top: 1px solid var(--border);
		padding: 48px clamp(20px, 4vw, 48px) 28px;
	}

	.mfoot-top {
		display: flex;
		flex-wrap: wrap;
		justify-content: space-between;
		gap: 40px;
		max-width: 1180px;
		margin: 0 auto;
	}

	.mfoot-brand {
		max-width: 260px;
	}

	.mfoot-brand p {
		margin: 12px 0 0;
		color: var(--text-faint);
		font-size: 13.5px;
		line-height: 1.5;
	}

	.mfoot-cols {
		display: flex;
		gap: 56px;
		flex-wrap: wrap;
	}

	.mfoot-col {
		display: flex;
		flex-direction: column;
		gap: 10px;
		min-width: 140px;
	}

	.mfoot-col h4 {
		margin: 0 0 2px;
		font-size: 12px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
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
		max-width: 1180px;
		margin: 40px auto 0;
		padding-top: 20px;
		border-top: 1px solid var(--border);
		color: var(--text-faint);
		font-size: 13px;
	}
</style>
