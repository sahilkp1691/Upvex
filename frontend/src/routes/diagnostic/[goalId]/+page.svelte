<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { post, get } from '$lib/api.js';
	import { pushToast } from '$lib/stores.js';

	const goalId = page.params.goalId;

	let phase = $state('loading'); // loading | question | evaluating | results
	let question = $state(null);
	let answered = $state(0);
	let selected = $state(null);
	let answerText = $state('');
	let submitting = $state(false);
	let results = $state(null);
	let conceptTitles = $state({});

	$effect(() => {
		start();
	});

	async function start() {
		try {
			const res = await post(`/diagnostic/${goalId}/start`);
			if (res.done) return complete();
			question = res.question;
			answered = res.question.index - 1;
			phase = 'question';
		} catch (err) {
			pushToast('Could not start diagnostic', err.message, 'error');
			goto('/topics');
		}
	}

	async function submitAnswer() {
		submitting = true;
		try {
			const payload = { question_id: question.question_id };
			if (question.type === 'multiple_choice') payload.selected_option = selected;
			else payload.answer_text = answerText;
			const res = await post(`/diagnostic/${goalId}/answer`, payload);
			answered = res.answered;
			selected = null;
			answerText = '';
			if (res.done) return complete();
			question = res.question;
		} catch (err) {
			pushToast('Answer failed', err.message, 'error');
		} finally {
			submitting = false;
		}
	}

	async function complete() {
		phase = 'evaluating';
		try {
			results = await post(`/diagnostic/${goalId}/complete`);
			const rm = await get(`/roadmap/${goalId}`);
			conceptTitles = Object.fromEntries(rm.nodes.map((n) => [n.id, n.title]));
			phase = 'results';
		} catch (err) {
			pushToast('Evaluation failed', err.message, 'error');
			phase = 'question';
		}
	}

	let sortedConcepts = $derived(
		results ? Object.entries(results.concept_scores).sort((a, b) => b[1] - a[1]) : []
	);

	function scoreClass(score) {
		if (score >= 70) return 'strong';
		if (score >= 45) return 'mid';
		return 'weak';
	}

	let canSubmit = $derived(
		question?.type === 'multiple_choice' ? selected !== null : answerText.trim().length > 0
	);
</script>

<svelte:head><title>Diagnostic — Upvex</title></svelte:head>

<div class="page quiz-page">
	{#if phase === 'loading'}
		<p class="faint center">Preparing your diagnostic...</p>
	{:else if phase === 'question' && question}
		<div class="meta">
			<span class="tag tag-accent">Question {question.index} of ~{question.total_estimate}</span>
			<span class="tag tag-dim">{question.difficulty}</span>
		</div>
		<div class="card q-card">
			<h2 class="q-text">{question.question_text}</h2>
			{#if question.type === 'multiple_choice'}
				<div class="options">
					{#each question.options as opt, i (i)}
						<button class="option" class:selected={selected === i} onclick={() => (selected = i)}>
							{opt}
						</button>
					{/each}
				</div>
			{:else}
				<textarea
					class="input"
					rows="4"
					placeholder="Answer in a sentence or two — partial credit counts."
					bind:value={answerText}
				></textarea>
			{/if}
			<button
				class="btn btn-primary submit"
				disabled={!canSubmit || submitting}
				onclick={submitAnswer}
			>
				{submitting ? 'Checking...' : 'Submit answer'}
			</button>
		</div>
	{:else if phase === 'evaluating'}
		<div class="evaluating">
			<div class="pulse-arrow">
				<svg width="54" height="54" viewBox="0 0 24 24" fill="none">
					<path d="M12 3 L20 19 L12 14.5 L4 19 Z" fill="var(--accent)" />
				</svg>
			</div>
			<h2>Mapping your knowledge...</h2>
			<p class="muted">Scoring your answers and tracing gaps through the concept graph.</p>
		</div>
	{:else if phase === 'results' && results}
		<div class="results">
			<div class="level-block card">
				<span class="label">Your starting skill</span>
				<div class="level-num">{Math.round(results.level_score)}</div>
				<span class="muted">out of 100 · confidence {Math.round(results.confidence * 100)}%</span>
			</div>

			<div class="card reasoning">
				<h3>What we found</h3>
				<p>{results.gap_reasoning}</p>
				{#if results.root_gap_concepts.length}
					<div class="root-gaps">
						<span class="label">Root gaps to resolve first</span>
						{#each results.root_gap_concepts as cid (cid)}
							<span class="tag tag-warn">{conceptTitles[cid] || cid}</span>
						{/each}
					</div>
				{/if}
			</div>

			<div class="card breakdown">
				<h3>Concept breakdown</h3>
				{#each sortedConcepts as [cid, score] (cid)}
					<div class="bar-row">
						<span class="bar-label">{conceptTitles[cid] || cid}</span>
						<div class="bar-track">
							<div class="bar-fill {scoreClass(score)}" style="width: {score}%"></div>
						</div>
						<span class="bar-score">{Math.round(score)}</span>
					</div>
				{/each}
			</div>

			<button class="btn btn-primary big" onclick={() => goto(`/roadmap/${goalId}`)}>
				See your roadmap
			</button>
		</div>
	{/if}
</div>

<style>
	.quiz-page {
		max-width: 720px;
	}

	.center {
		text-align: center;
		padding-top: 80px;
	}

	.meta {
		display: flex;
		gap: 10px;
		margin-bottom: 14px;
	}

	.q-card {
		padding: 28px;
	}

	.q-text {
		font-size: 21px;
		margin-bottom: 20px;
	}

	.options {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.option {
		text-align: left;
		padding: 13px 17px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
		font-size: 15px;
		cursor: pointer;
		transition:
			border-color 0.12s,
			background 0.12s;
	}

	.option:hover {
		border-color: var(--up);
	}

	.option.selected {
		border-color: var(--up);
		background: var(--up-soft);
	}

	.submit {
		margin-top: 22px;
	}

	.evaluating {
		text-align: center;
		padding-top: 90px;
	}

	.pulse-arrow {
		animation: upvex-pulse 1.2s ease-in-out infinite;
		margin-bottom: 18px;
	}

	.results {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.level-block {
		text-align: center;
		padding: 30px;
	}

	.level-num {
		font-size: 64px;
		font-weight: 750;
		background: linear-gradient(100deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		line-height: 1.1;
	}

	.reasoning p {
		font-size: 15.5px;
	}

	.root-gaps {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
		margin-top: 12px;
	}

	.root-gaps .label {
		margin: 0;
		width: 100%;
	}

	.bar-row {
		display: grid;
		grid-template-columns: 220px 1fr 40px;
		align-items: center;
		gap: 14px;
		padding: 7px 0;
	}

	.bar-label {
		font-size: 14px;
		color: var(--text-dim);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.bar-track {
		height: 9px;
		border-radius: 5px;
		background: var(--bg-elevated);
		overflow: hidden;
	}

	.bar-fill {
		height: 100%;
		border-radius: 5px;
		transition: width 0.6s ease-out;
	}

	.bar-fill.strong {
		background: var(--up);
	}

	.bar-fill.mid {
		background: var(--warn);
	}

	.bar-fill.weak {
		background: var(--danger);
	}

	.bar-score {
		font-size: 13.5px;
		color: var(--text-dim);
		text-align: right;
	}

	.big {
		align-self: center;
		padding: 13px 30px;
		font-size: 16px;
	}
</style>
