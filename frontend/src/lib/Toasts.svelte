<script>
	import { toasts } from './stores.js';
</script>

<div class="toasts">
	{#each $toasts as t (t.id)}
		<div class="toast toast-{t.kind}">
			<strong>{t.title}</strong>
			{#if t.body}<span class="body">{t.body}</span>{/if}
		</div>
	{/each}
</div>

<style>
	.toasts {
		position: fixed;
		bottom: 24px;
		right: 24px;
		display: flex;
		flex-direction: column;
		gap: 10px;
		z-index: 100;
		max-width: 340px;
	}

	.toast {
		background: var(--bg-card);
		border: 1px solid var(--border-strong);
		border-left: 3px solid var(--accent);
		border-radius: var(--radius-sm);
		padding: 12px 16px;
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.45);
		display: flex;
		flex-direction: column;
		gap: 2px;
		animation: slide-in 0.2s ease-out;
	}

	.toast-xp {
		border-left-color: var(--up);
	}

	.toast-badge {
		border-left-color: var(--gold);
	}

	.toast-error {
		border-left-color: var(--danger);
	}

	.body {
		color: var(--text-dim);
		font-size: 13.5px;
	}

	@keyframes slide-in {
		from {
			transform: translateX(30px);
			opacity: 0;
		}
		to {
			transform: none;
			opacity: 1;
		}
	}
</style>
