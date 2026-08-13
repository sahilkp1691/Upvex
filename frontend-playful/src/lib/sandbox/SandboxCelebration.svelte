<script>
	let { active = false } = $props();

	const particles = Array.from({ length: 24 }, (_, i) => ({
		id: i,
		x: 20 + Math.random() * 60,
		delay: Math.random() * 0.4,
		hue: i % 3 === 0 ? 'var(--up)' : i % 3 === 1 ? 'var(--accent)' : 'var(--gold)',
		size: 4 + Math.random() * 6
	}));
</script>

{#if active}
	<div class="celebration" aria-hidden="true">
		{#each particles as p (p.id)}
			<span
				class="particle"
				style="left:{p.x}%; --delay:{p.delay}s; --hue:{p.hue}; --size:{p.size}px"
			></span>
		{/each}
		<div class="burst-ring"></div>
		<span class="burst-text">Perfect!</span>
	</div>
{/if}

<style>
	.celebration {
		position: fixed;
		inset: 0;
		pointer-events: none;
		z-index: 9999;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.particle {
		position: absolute;
		top: 45%;
		width: var(--size);
		height: var(--size);
		background: var(--hue);
		border-radius: 50%;
		animation: burst 1.2s ease-out var(--delay) forwards;
		opacity: 0;
	}

	.burst-ring {
		position: absolute;
		width: 80px;
		height: 80px;
		border: 3px solid var(--up);
		border-radius: 50%;
		animation: ring 0.8s ease-out forwards;
		opacity: 0;
	}

	.burst-text {
		position: absolute;
		font-family: var(--font-display);
		font-size: 28px;
		font-weight: 800;
		color: var(--up);
		animation: text-pop 1s ease-out 0.1s forwards;
		opacity: 0;
		text-shadow: 0 0 30px rgba(45, 212, 160, 0.5);
	}

	@keyframes burst {
		0% {
			opacity: 1;
			transform: translate(0, 0) scale(1);
		}
		100% {
			opacity: 0;
			transform: translate(calc((var(--size) - 6px) * 8), -120px) scale(0);
		}
	}

	@keyframes ring {
		0% {
			opacity: 0.8;
			transform: scale(0.3);
		}
		100% {
			opacity: 0;
			transform: scale(3);
		}
	}

	@keyframes text-pop {
		0% {
			opacity: 0;
			transform: scale(0.5) translateY(10px);
		}
		40% {
			opacity: 1;
			transform: scale(1.1) translateY(0);
		}
		100% {
			opacity: 0;
			transform: scale(1) translateY(-20px);
		}
	}
</style>
