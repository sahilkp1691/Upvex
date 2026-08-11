<script>
	import { page } from '$app/state';
	import { get, post, patch, del } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	const topicId = page.params.topicId;

	let data = $state(null);
	let loading = $state(true);
	let saving = $state(false);
	let drafting = $state(false);
	let drafts = $state([]);
	let draftSource = $state(null);

	let filterConcept = $state('');
	let editingId = $state(null);
	let form = $state(blankForm());

	function blankForm(conceptId = '') {
		return {
			concept_node_id: conceptId,
			difficulty: 'medium',
			type: 'multiple_choice',
			question_text: '',
			options: ['', '', '', ''],
			correct_option: 0,
			expected_concepts: ''
		};
	}

	$effect(() => {
		load();
	});

	async function load() {
		loading = true;
		try {
			data = await get(`/admin/topics/${topicId}/diagnostics`);
			if (!form.concept_node_id && data.concepts.length) {
				form = blankForm(data.concepts[0].id);
			}
		} catch (err) {
			pushToast('Could not load diagnostics', err.message, 'error');
		} finally {
			loading = false;
		}
	}

	let titleOf = $derived.by(() => {
		const map = Object.fromEntries((data?.concepts || []).map((c) => [c.id, c.title]));
		return (id) => map[id] || id;
	});

	let filteredQuestions = $derived.by(() => {
		if (!data) return [];
		if (!filterConcept) return data.questions;
		return data.questions.filter((q) => q.concept_node_id === filterConcept);
	});

	function startEdit(q) {
		editingId = q.id;
		form = {
			concept_node_id: q.concept_node_id,
			difficulty: q.difficulty,
			type: q.type,
			question_text: q.question_text,
			options: q.type === 'multiple_choice' ? [...(q.options || []), '', '', '', ''].slice(0, 4) : ['', '', '', ''],
			correct_option: q.correct_option ?? 0,
			expected_concepts: (q.expected_concepts || []).join(', ')
		};
	}

	function startNew() {
		editingId = null;
		form = blankForm(filterConcept || data?.concepts?.[0]?.id || '');
	}

	function payloadFromForm() {
		const body = {
			concept_node_id: form.concept_node_id,
			difficulty: form.difficulty,
			type: form.type,
			question_text: form.question_text.trim()
		};
		if (form.type === 'multiple_choice') {
			body.options = form.options.map((o) => o.trim()).filter(Boolean);
			body.correct_option = Number(form.correct_option);
			body.expected_concepts = null;
		} else {
			body.options = null;
			body.correct_option = null;
			body.expected_concepts = form.expected_concepts
				.split(',')
				.map((s) => s.trim())
				.filter(Boolean);
		}
		return body;
	}

	async function saveQuestion() {
		saving = true;
		try {
			const body = payloadFromForm();
			if (editingId) {
				await patch(`/admin/diagnostics/${editingId}`, body);
				pushToast('Question updated');
			} else {
				await post(`/admin/topics/${topicId}/diagnostics`, body);
				pushToast('Question added');
			}
			startNew();
			await load();
		} catch (err) {
			pushToast('Save failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	async function removeQuestion(id) {
		if (!confirm('Delete this diagnostic question?')) return;
		saving = true;
		try {
			await del(`/admin/diagnostics/${id}`);
			pushToast('Question deleted');
			if (editingId === id) startNew();
			await load();
		} catch (err) {
			pushToast('Delete failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	async function draftAll() {
		drafting = true;
		try {
			const res = await post(`/admin/topics/${topicId}/diagnostics/draft`, {
				concept_ids: filterConcept ? [filterConcept] : null,
				count_per_concept: 2
			});
			drafts = res.drafts;
			draftSource = res.source;
			pushToast(
				'Draft ready',
				`${res.count} questions (${res.source === 'ai' ? 'AI' : 'offline stub'})`,
				'info'
			);
		} catch (err) {
			pushToast('Draft failed', err.message, 'error');
		} finally {
			drafting = false;
		}
	}

	async function acceptDrafts() {
		if (!drafts.length) return;
		saving = true;
		try {
			const res = await post(`/admin/topics/${topicId}/diagnostics/bulk`, {
				questions: drafts.map((d) => ({
					concept_node_id: d.concept_node_id,
					difficulty: d.difficulty,
					type: d.type,
					question_text: d.question_text,
					options: d.options,
					correct_option: d.correct_option,
					expected_concepts: d.expected_concepts
				}))
			});
			pushToast('Drafts added', `${res.created_count} questions saved`);
			drafts = [];
			await load();
		} catch (err) {
			pushToast('Bulk save failed', err.message, 'error');
		} finally {
			saving = false;
		}
	}

	function fillFormFromDraft(d) {
		editingId = null;
		form = {
			concept_node_id: d.concept_node_id,
			difficulty: d.difficulty,
			type: d.type,
			question_text: d.question_text,
			options:
				d.type === 'multiple_choice'
					? [...(d.options || []), '', '', '', ''].slice(0, 4)
					: ['', '', '', ''],
			correct_option: d.correct_option ?? 0,
			expected_concepts: (d.expected_concepts || []).join(', ')
		};
	}
</script>

<svelte:head>
	<title>{data?.topic_name ? `${data.topic_name} diagnostics` : 'Diagnostics'} — Upvex</title>
</svelte:head>

<a href={`/admin/graph/${topicId}`} class="back">Back to graph</a>

{#if loading}
	<p class="faint">Loading diagnostic bank...</p>
{:else if data}
	<header class="page-head">
		<div>
			<h1>{data.topic_name} — Diagnostics</h1>
			<p class="muted">
				Question bank for the adaptive diagnostic. Learners cannot start until the bank is ready.
			</p>
		</div>
		<div class="toolbar">
			<a class="btn" href={`/admin/graph/${topicId}`}>Edit graph</a>
			<button class="btn" disabled={drafting || !data.concepts.length} onclick={draftAll}>
				{drafting ? 'Drafting...' : 'Draft with AI'}
			</button>
			<button class="btn btn-primary" onclick={startNew}>New question</button>
		</div>
	</header>

	<div class="ready-card" class:ok={data.readiness.ready}>
		{#if data.readiness.ready}
			<strong>Diagnostic ready</strong>
			<span class="muted"
				>{data.readiness.question_count} questions · {data.readiness.concepts_covered} concepts
				covered</span
			>
		{:else}
			<strong>Not ready for learners</strong>
			<ul>
				{#each data.readiness.issues as issue, i (i)}
					<li>{issue}</li>
				{/each}
			</ul>
		{/if}
		<div class="ready-stats">
			<span>{data.readiness.question_count}/{data.readiness.min_bank_size} questions</span>
			<span
				>{data.readiness.concepts_covered}/{data.readiness.min_concepts_covered} concepts</span
			>
			<span
				>easy {data.readiness.by_difficulty.easy} · medium {data.readiness.by_difficulty.medium} ·
				hard {data.readiness.by_difficulty.hard}</span
			>
		</div>
	</div>

	{#if !data.concepts.length}
		<div class="empty-state">
			<h3>No concepts yet</h3>
			<p class="muted">Build the knowledge graph first, then add diagnostic questions.</p>
			<a class="btn btn-primary" href={`/admin/graph/${topicId}`}>Open graph editor</a>
		</div>
	{:else}
		<div class="layout">
			<section class="list-pane">
				<div class="list-head">
					<h2>Questions ({filteredQuestions.length})</h2>
					<select class="input filter" bind:value={filterConcept}>
						<option value="">All concepts</option>
						{#each data.concepts as c (c.id)}
							<option value={c.id}>{c.title}</option>
						{/each}
					</select>
				</div>

				{#if filteredQuestions.length === 0}
					<p class="muted empty-list">No questions yet — draft with AI or add manually.</p>
				{:else}
					<ul class="q-list">
						{#each filteredQuestions as q (q.id)}
							<li class:active={editingId === q.id}>
								<button class="q-main" onclick={() => startEdit(q)}>
									<span class="q-meta">
										<span class="tag tag-dim">{q.difficulty}</span>
										<span class="tag tag-accent">{q.type === 'multiple_choice' ? 'MC' : 'SA'}</span>
										<span class="faint">{titleOf(q.concept_node_id)}</span>
									</span>
									<span class="q-text">{q.question_text}</span>
								</button>
								<button class="btn btn-sm danger-outline" onclick={() => removeQuestion(q.id)}
									>Delete</button
								>
							</li>
						{/each}
					</ul>
				{/if}

				{#if drafts.length}
					<div class="drafts">
						<div class="draft-head">
							<h3>Drafts ({drafts.length}) · {draftSource}</h3>
							<button class="btn btn-sm btn-primary" disabled={saving} onclick={acceptDrafts}>
								Add all drafts
							</button>
							<button class="btn btn-sm" onclick={() => (drafts = [])}>Discard</button>
						</div>
						<ul class="draft-list">
							{#each drafts as d, i (i)}
								<li>
									<span class="q-meta">
										<span class="tag tag-dim">{d.difficulty}</span>
										<span class="faint">{d.concept_title}</span>
									</span>
									<span class="q-text">{d.question_text}</span>
									<button class="btn btn-sm" onclick={() => fillFormFromDraft(d)}>Edit in form</button>
								</li>
							{/each}
						</ul>
					</div>
				{/if}
			</section>

			<aside class="form-pane card">
				<h2>{editingId ? 'Edit question' : 'New question'}</h2>

				<label class="label" for="d-concept">Concept</label>
				<select id="d-concept" class="input" bind:value={form.concept_node_id}>
					{#each data.concepts as c (c.id)}
						<option value={c.id}>{c.title}</option>
					{/each}
				</select>

				<div class="grid-2">
					<div>
						<label class="label" for="d-diff">Difficulty</label>
						<select id="d-diff" class="input" bind:value={form.difficulty}>
							<option value="easy">easy</option>
							<option value="medium">medium</option>
							<option value="hard">hard</option>
						</select>
					</div>
					<div>
						<label class="label" for="d-type">Type</label>
						<select id="d-type" class="input" bind:value={form.type}>
							<option value="multiple_choice">multiple_choice</option>
							<option value="short_answer">short_answer</option>
						</select>
					</div>
				</div>

				<label class="label" for="d-text">Question</label>
				<textarea id="d-text" class="input" rows="4" bind:value={form.question_text}></textarea>

				{#if form.type === 'multiple_choice'}
					<label class="label">Options</label>
					{#each form.options as _, i (i)}
						<div class="opt-row">
							<input
								class="input"
								type="radio"
								name="correct"
								checked={form.correct_option === i}
								onchange={() => (form.correct_option = i)}
								aria-label={`Mark option ${i + 1} correct`}
							/>
							<input class="input" bind:value={form.options[i]} placeholder={`Option ${i + 1}`} />
						</div>
					{/each}
					<p class="faint hint">Select the radio next to the correct option.</p>
				{:else}
					<label class="label" for="d-kw">Expected keywords (comma-separated)</label>
					<input id="d-kw" class="input" bind:value={form.expected_concepts} />
				{/if}

				<div class="form-actions">
					{#if editingId}
						<button class="btn" onclick={startNew}>Cancel edit</button>
					{/if}
					<button
						class="btn btn-primary"
						disabled={saving || !form.question_text.trim() || !form.concept_node_id}
						onclick={saveQuestion}
					>
						{saving ? 'Saving...' : editingId ? 'Update' : 'Add question'}
					</button>
				</div>
			</aside>
		</div>
	{/if}
{/if}

<style>
	.back {
		display: inline-block;
		margin-bottom: 14px;
		color: var(--text-dim);
		font-size: 14px;
	}

	.page-head {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 16px;
		flex-wrap: wrap;
		margin-bottom: 14px;
	}

	.page-head h1 {
		margin: 0 0 4px;
		font-size: 1.45rem;
	}

	.toolbar {
		display: flex;
		gap: 8px;
		flex-wrap: wrap;
	}

	.ready-card {
		padding: 14px 16px;
		border-radius: var(--radius);
		border: 1px solid color-mix(in srgb, var(--warn) 45%, var(--border));
		background: var(--warn-soft);
		margin-bottom: 18px;
	}

	.ready-card.ok {
		border-color: color-mix(in srgb, var(--up) 45%, var(--border));
		background: var(--up-soft);
	}

	.ready-card strong {
		display: block;
		margin-bottom: 4px;
	}

	.ready-card ul {
		margin: 6px 0 0;
		padding-left: 18px;
		color: var(--text-dim);
		font-size: 13.5px;
	}

	.ready-stats {
		display: flex;
		flex-wrap: wrap;
		gap: 12px 18px;
		margin-top: 10px;
		font-size: 12.5px;
		color: var(--text-faint);
		font-weight: 600;
	}

	.layout {
		display: grid;
		grid-template-columns: 1fr min(380px, 40vw);
		gap: 16px;
		align-items: start;
	}

	@media (max-width: 960px) {
		.layout {
			grid-template-columns: 1fr;
		}
	}

	.list-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 10px;
		margin-bottom: 10px;
	}

	.list-head h2 {
		margin: 0;
		font-size: 1.1rem;
	}

	.filter {
		width: min(220px, 100%);
	}

	.q-list,
	.draft-list {
		list-style: none;
		margin: 0;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.q-list li {
		display: flex;
		gap: 8px;
		align-items: stretch;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		padding: 8px;
	}

	.q-list li.active {
		border-color: var(--accent);
	}

	.q-main {
		flex: 1;
		border: none;
		background: transparent;
		text-align: left;
		cursor: pointer;
		color: inherit;
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 4px;
	}

	.q-meta {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		align-items: center;
	}

	.q-text {
		font-size: 13.5px;
		line-height: 1.35;
	}

	.empty-list {
		padding: 20px 0;
	}

	.drafts {
		margin-top: 22px;
		padding-top: 14px;
		border-top: 1px solid var(--border);
	}

	.draft-head {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
		margin-bottom: 10px;
	}

	.draft-head h3 {
		margin: 0;
		flex: 1;
		font-size: 1rem;
	}

	.draft-list li {
		display: flex;
		flex-direction: column;
		gap: 6px;
		padding: 10px 12px;
		border: 1px dashed var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-elevated);
	}

	.form-pane {
		position: sticky;
		top: 16px;
		padding: 18px;
	}

	.form-pane h2 {
		margin: 0 0 8px;
		font-size: 1.1rem;
	}

	.grid-2 {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 10px;
	}

	.label {
		margin-top: 12px;
	}

	.opt-row {
		display: grid;
		grid-template-columns: 22px 1fr;
		gap: 8px;
		align-items: center;
		margin-bottom: 6px;
	}

	.hint {
		font-size: 12px;
		margin: 4px 0 0;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 8px;
		margin-top: 16px;
	}

	.danger-outline {
		color: var(--danger);
		border-color: color-mix(in srgb, var(--danger) 40%, var(--border));
		align-self: center;
	}

	.empty-state {
		padding: 40px 24px;
		text-align: center;
		border: 1px dashed var(--border);
		border-radius: var(--radius);
		background: var(--bg-elevated);
	}
</style>
