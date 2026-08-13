<script>
	import { theme, toggleTheme } from './stores.js';
</script>

<button
	class="btn btn-ghost theme-toggle"
	type="button"
	onclick={toggleTheme}
	aria-label={$theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
	title={$theme === 'dark' ? 'Light mode' : 'Dark mode'}
>
	{#if $theme === 'dark'}
		<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
			<circle cx="12" cy="12" r="4.5" stroke="currentColor" stroke-width="1.8" />
			<path
				d="M12 2v2.2M12 19.8V22M4.2 12H2M22 12h-2.2M5.05 5.05l1.55 1.55M17.4 17.4l1.55 1.55M5.05 18.95l1.55-1.55M17.4 6.6l1.55-1.55"
				stroke="currentColor"
				stroke-width="1.8"
				stroke-linecap="round"
			/>
		</svg>
	{:else}
		<svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden="true">
			<path
				d="M20.5 14.2A8.2 8.2 0 0 1 9.8 3.5 8.5 8.5 0 1 0 20.5 14.2Z"
				stroke="currentColor"
				stroke-width="1.8"
				stroke-linejoin="round"
			/>
		</svg>
	{/if}
</button>

<style>
	.theme-toggle {
		padding: 7px;
		min-width: 34px;
		color: var(--text-dim);
	}

	.theme-toggle:hover {
		color: var(--text);
	}
</style>
