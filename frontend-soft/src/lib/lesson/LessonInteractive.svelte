<script>
	import SqlSandbox from '$lib/sandbox/SqlSandbox.svelte';

	let { interactive } = $props();

	// step_reorder state
	let stepOrder = $state([]);
	let stepResult = $state(null);

	// concept_match state
	let matchSelections = $state({});
	let matchResult = $state(null);

	// mini_sandbox state
	let miniPassed = $state(false);

	$effect(() => {
		if (interactive?.type === 'step_reorder' && interactive.steps) {
			stepOrder = [...interactive.steps].sort(() => Math.random() - 0.5);
			stepResult = null;
		}
		if (interactive?.type === 'concept_match' && interactive.pairs) {
			matchSelections = {};
			matchResult = null;
		}
	});

	function shuffleSteps() {
		stepOrder = [...stepOrder].sort(() => Math.random() - 0.5);
		stepResult = null;
	}

	function moveStep(from, to) {
		if (to < 0 || to >= stepOrder.length) return;
		const next = [...stepOrder];
		const [item] = next.splice(from, 1);
		next.splice(to, 0, item);
		stepOrder = next;
		stepResult = null;
	}

	function checkStepOrder() {
		const correct = interactive.correct_order.map((i) => interactive.steps[i]);
		const pass = stepOrder.every((s, i) => s === correct[i]);
		stepResult = pass ? 'correct' : 'wrong';
	}

	function checkMatch() {
		const pairs = interactive.pairs || [];
		const allSelected = pairs.every((_, i) => matchSelections[i] != null);
		if (!allSelected) {
			matchResult = 'incomplete';
			return;
		}
		const pass = pairs.every((p, i) => matchSelections[i] === p.right);
		matchResult = pass ? 'correct' : 'wrong';
	}

	function getRights() {
		const rights = (interactive.pairs || []).map((p) => p.right);
		return [...new Set(rights)].sort(() => Math.random() - 0.5);
	}

	let shuffledRights = $derived.by(() => {
		if (interactive?.type !== 'concept_match') return [];
		return getRights();
	});
</script>

<div class="interactive-block">
	{#if interactive.type === 'mini_sandbox'}
		<div class="block-head">
			<span class="block-tag">Try it now</span>
			{#if miniPassed}<span class="block-pass">Completed</span>{/if}
		</div>
		<SqlSandbox
			question={{
				question_text: interactive.prompt,
				dataset: interactive.dataset,
				starter_sql: interactive.starter_sql,
				hints: interactive.hints || [],
				difficulty: 3,
				order_sensitive: false
			}}
			solutionSql={interactive.solution_sql}
			compact={true}
			onPassed={() => (miniPassed = true)}
		/>
	{:else if interactive.type === 'step_reorder'}
		<div class="block-head">
			<span class="block-tag">Reorder steps</span>
		</div>
		<p class="block-prompt">{interactive.prompt}</p>
		<ul class="step-list">
			{#each stepOrder as step, i (step + i)}
				<li>
					<span class="step-num">{i + 1}</span>
					<span class="step-text">{step}</span>
					<div class="step-btns">
						<button onclick={() => moveStep(i, i - 1)} disabled={i === 0} aria-label="Move up">↑</button>
						<button onclick={() => moveStep(i, i + 1)} disabled={i === stepOrder.length - 1} aria-label="Move down">↓</button>
					</div>
				</li>
			{/each}
		</ul>
		<div class="step-actions">
			<button class="btn-sm" onclick={shuffleSteps}>Shuffle</button>
			<button class="btn-sm primary" onclick={checkStepOrder}>Check order</button>
		</div>
		{#if stepResult === 'correct'}
			<p class="feedback good">Correct execution order.</p>
		{:else if stepResult === 'wrong'}
			<p class="feedback bad">Not quite — FROM comes before SELECT in processing order.</p>
		{/if}
	{:else if interactive.type === 'concept_match'}
		<div class="block-head">
			<span class="block-tag">Match concepts</span>
		</div>
		<p class="block-prompt">{interactive.prompt}</p>
		<div class="match-grid">
			{#each interactive.pairs as pair, i (i)}
				<div class="match-row">
					<span class="match-left">{pair.left}</span>
					<select bind:value={matchSelections[i]} onchange={() => (matchResult = null)}>
						<option value={null}>Choose...</option>
						{#each shuffledRights as right (right)}
							<option value={right}>{right}</option>
						{/each}
					</select>
				</div>
			{/each}
		</div>
		<button class="btn-sm primary" onclick={checkMatch}>Check matches</button>
		{#if matchResult === 'correct'}
			<p class="feedback good">All matches correct.</p>
		{:else if matchResult === 'wrong'}
			<p class="feedback bad">Some matches are off — try again.</p>
		{:else if matchResult === 'incomplete'}
			<p class="feedback bad">Select an answer for each row.</p>
		{/if}
	{/if}
</div>

<style>
	.interactive-block {
		margin: 16px 0;
		padding: 16px;
		background: var(--bg-card);
		border: 1px solid var(--border-strong);
		border-radius: var(--radius);
		border-left: 3px solid var(--accent);
	}

	.block-head {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 8px;
	}

	.block-tag {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: var(--accent-bright);
	}

	.block-pass {
		font-size: 11px;
		font-weight: 700;
		color: var(--up);
		background: var(--up-soft);
		padding: 2px 8px;
		border-radius: 999px;
	}

	.block-prompt {
		font-size: 14px;
		color: var(--text-dim);
		margin: 0 0 12px;
	}

	.step-list {
		list-style: none;
		margin: 0 0 12px;
		padding: 0;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.step-list li {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 8px 12px;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
	}

	.step-num {
		width: 24px;
		height: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--accent-soft);
		color: var(--accent-bright);
		border-radius: 50%;
		font-size: 12px;
		font-weight: 700;
		flex-shrink: 0;
	}

	.step-text {
		flex: 1;
		font-family: var(--mono);
		font-size: 13px;
	}

	.step-btns {
		display: flex;
		gap: 4px;
	}

	.step-btns button {
		width: 28px;
		height: 28px;
		border: 1px solid var(--border);
		background: var(--bg-card);
		color: var(--text-dim);
		border-radius: 4px;
		cursor: pointer;
		font-size: 12px;
	}

	.step-btns button:hover:not(:disabled) {
		border-color: var(--accent);
		color: var(--accent);
	}

	.step-btns button:disabled {
		opacity: 0.3;
		cursor: not-allowed;
	}

	.step-actions {
		display: flex;
		gap: 8px;
	}

	.btn-sm {
		padding: 6px 14px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
	}

	.btn-sm.primary {
		background: var(--accent);
		color: var(--accent-fg);
		border-color: var(--accent);
	}

	.match-grid {
		display: flex;
		flex-direction: column;
		gap: 8px;
		margin-bottom: 12px;
	}

	.match-row {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 10px;
		align-items: center;
	}

	.match-left {
		font-size: 13px;
		font-weight: 600;
		padding: 8px 12px;
		background: var(--bg-elevated);
		border-radius: var(--radius-sm);
		border: 1px solid var(--border);
	}

	.match-row select {
		padding: 8px 10px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
		font-size: 13px;
	}

	.feedback {
		margin: 10px 0 0;
		font-size: 13px;
		font-weight: 600;
	}

	.feedback.good {
		color: var(--up);
	}

	.feedback.bad {
		color: var(--danger);
	}
</style>
