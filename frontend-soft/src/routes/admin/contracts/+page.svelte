<script>
	import { get, post } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	let contracts = $state([]);
	let loading = $state(true);
	let form = $state({ persona_text: '', structural_template: '', constraints_text: '' });
	let saving = $state(false);
	let viewingVersion = $state(null);

	$effect(() => {
		load();
	});

	async function load() {
		try {
			contracts = await get('/admin/contracts');
			const active = contracts.find((c) => c.is_active);
			if (active) {
				form = {
					persona_text: active.persona_text,
					structural_template: active.structural_template,
					constraints_text: active.constraints_text
				};
			}
		} finally {
			loading = false;
		}
	}

	async function save() {
		saving = true;
		try {
			const res = await post('/admin/contracts', form);
			pushToast(`Contract v${res.version} activated`, 'Old versions retained; existing content stays tagged with its version.');
			await load();
		} catch (err) {
			pushToast('Save failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	let active = $derived(contracts.find((c) => c.is_active));
</script>

<svelte:head><title>Generation contract — Upvex</title></svelte:head>

{#if loading}
	<p class="faint">Loading...</p>
{:else}
	<div class="head-row">
		<div>
			<h2>Generation Contract</h2>
			<p class="muted">
				Governs all content generation. Saving creates a new version and activates it — the primary
				lever for fixing drift or consistency issues globally.
			</p>
		</div>
		{#if active}<span class="tag tag-up">Active: v{active.version}</span>{/if}
	</div>

	<div class="card">
		<label class="label" for="c-persona">Persona</label>
		<p class="faint hint">Tone, explanation approach, encouragement level, analogy and humor use.</p>
		<textarea id="c-persona" class="input tall" bind:value={form.persona_text}></textarea>

		<label class="label" for="c-template">Structural template</label>
		<p class="faint hint">Fixed lesson and quiz shape the model must produce.</p>
		<textarea id="c-template" class="input tall" bind:value={form.structural_template}></textarea>

		<label class="label" for="c-constraints">Constraints</label>
		<p class="faint hint">Scope discipline, uncertainty flagging, output format rules.</p>
		<textarea id="c-constraints" class="input tall" bind:value={form.constraints_text}></textarea>

		<button
			class="btn btn-primary save"
			disabled={saving ||
				!form.persona_text.trim() ||
				!form.structural_template.trim() ||
				!form.constraints_text.trim()}
			onclick={save}
		>
			{saving ? 'Saving...' : 'Save as new version'}
		</button>
	</div>

	<h3 class="history-h">Version history</h3>
	<div class="versions">
		{#each contracts as c (c.id)}
			<div class="card v-row">
				<div class="v-head">
					<span class="v-name">
						v{c.version}
						{#if c.is_active}<span class="tag tag-up">active</span>{/if}
					</span>
					<span class="faint">{new Date(c.created_at).toLocaleString()}</span>
					<button
						class="btn btn-xs"
						onclick={() => (viewingVersion = viewingVersion === c.version ? null : c.version)}
					>
						{viewingVersion === c.version ? 'Hide' : 'View'}
					</button>
				</div>
				{#if viewingVersion === c.version}
					<div class="v-body">
						<span class="label">Persona</span>
						<p class="muted pre">{c.persona_text}</p>
						<span class="label">Template</span>
						<p class="muted pre">{c.structural_template}</p>
						<span class="label">Constraints</span>
						<p class="muted pre">{c.constraints_text}</p>
					</div>
				{/if}
			</div>
		{/each}
	</div>
{/if}

<style>
	.head-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 20px;
		margin-bottom: 16px;
	}

	.head-row h2 {
		margin-bottom: 4px;
	}

	.label {
		margin-top: 18px;
	}

	.label:first-child {
		margin-top: 0;
	}

	.hint {
		font-size: 12.5px;
		margin: 0 0 6px;
	}

	.tall {
		min-height: 120px;
		font-size: 13.5px;
		line-height: 1.55;
	}

	.save {
		margin-top: 18px;
	}

	.history-h {
		margin-top: 32px;
	}

	.versions {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.v-row {
		padding: 14px 18px;
	}

	.v-head {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.v-name {
		font-weight: 650;
		display: flex;
		gap: 8px;
		align-items: center;
		flex: 1;
	}

	.btn-xs {
		padding: 4px 10px;
		font-size: 12.5px;
	}

	.v-body {
		margin-top: 14px;
		border-top: 1px solid var(--border);
		padding-top: 12px;
	}

	.pre {
		white-space: pre-wrap;
		font-size: 13px;
	}
</style>
