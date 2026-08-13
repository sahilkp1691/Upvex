<script>
	let { size = 26 } = $props();
</script>

<span class="logo" style="--s: {size}px">
	<svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden="true">
		<path d="M12 3 L20 19 L12 14.5 L4 19 Z" fill="url(#upvexGrad)" />
		<defs>
			<linearGradient id="upvexGrad" x1="4" y1="19" x2="20" y2="3" gradientUnits="userSpaceOnUse">
				<stop offset="0" stop-color="#4f7cff" />
				<stop offset="1" stop-color="#34d399" />
			</linearGradient>
		</defs>
	</svg>
	<span class="word">Upvex</span>
</span>

<style>
	.logo {
		display: inline-flex;
		align-items: center;
		gap: 8px;
		font-family: var(--font-display);
		font-weight: 800;
		font-size: calc(var(--s) * 0.78);
		letter-spacing: -0.03em;
		color: var(--text);
	}

	.word {
		background: linear-gradient(120deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
	}
</style>
