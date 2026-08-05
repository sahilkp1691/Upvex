<script>
	import SqlEditor from './SqlEditor.svelte';
	import SchemaBrowser from './SchemaBrowser.svelte';
	import QueryResults from './QueryResults.svelte';
	import SandboxCelebration from './SandboxCelebration.svelte';
	import { runQuery } from './sqlEngine.js';
	import { post } from '$lib/api.js';
	import { randomSurprise } from './surpriseVariants.js';

	let {
		question = {},
		solutionSql = '',
		compact = false,
		contentId = null,
		questionIndex = null,
		allowSurprise = false,
		onPassed = () => {},
		onStateChange = () => {}
	} = $props();

	let activeQuestion = $state(null);
	let usingSurprise = $state(false);

	$effect(() => {
		activeQuestion = { ...question };
		usingSurprise = false;
	});

	let q = $derived(activeQuestion || question);

	let sql = $state('');
	let result = $state(null);
	let error = $state('');
	let running = $state(false);
	let checking = $state(false);
	let checkResult = $state(null);
	let hintsRevealed = $state(0);
	let showSolution = $state(false);
	let solutionTyped = $state('');
	let celebrate = $state(false);
	let checkAttempts = $state(0);
	let passed = $state(false);
	let diffMode = $state(false);

	let editorRef;

	const hints = $derived(q.hints || []);
	const difficulty = $derived(q.difficulty || 4);
	const orderSensitive = $derived(q.order_sensitive || false);

	$effect(() => {
		if (q?.starter_sql != null) {
			sql = q.starter_sql || '-- your SQL here\n';
			result = null;
			error = '';
			checkResult = null;
			passed = false;
			hintsRevealed = 0;
			showSolution = false;
		}
	});

	$effect(() => {
		onStateChange({
			user_sql: sql,
			passed,
			hints_used: hintsRevealed,
			check_attempts: checkAttempts
		});
	});

	async function handleRun() {
		running = true;
		error = '';
		checkResult = null;
		diffMode = false;
		try {
			result = await runQuery(q.dataset, sql);
		} catch (err) {
			error = err.message;
			result = null;
		} finally {
			running = false;
		}
	}

	async function handleCheck() {
		checking = true;
		checkAttempts += 1;
		diffMode = true;
		error = '';
		try {
			// Always run user query locally for instant results display
			try {
				result = await runQuery(q.dataset, sql);
			} catch (err) {
				error = err.message;
				checking = false;
				return;
			}

			const payload = {
				user_sql: sql,
				order_sensitive: orderSensitive
			};
			if (contentId != null && questionIndex != null) {
				payload.generated_content_id = contentId;
				payload.question_index = questionIndex;
			} else if (solutionSql || usingSurprise) {
				payload.dataset = q.dataset;
				payload.solution_sql = usingSurprise ? q.solution_sql : solutionSql;
			}

			const server = await post('/content/verify-sandbox', payload);
			checkResult = {
				...server,
				expected: server.expected,
				actual: server.actual || result
			};
			if (server.actual) result = server.actual;

			if (checkResult.passed) {
				passed = true;
				celebrate = true;
				onPassed();
				setTimeout(() => (celebrate = false), 1400);
			}
		} catch (err) {
			error = err.message;
		} finally {
			checking = false;
		}
	}

	function revealHint() {
		if (hintsRevealed < hints.length) hintsRevealed += 1;
	}

	function toggleSolution() {
		showSolution = !showSolution;
		if (showSolution && !solutionTyped) {
			typeSolution();
		}
	}

	function getSolutionText() {
		if (usingSurprise && q.solution_sql) return q.solution_sql;
		return solutionSql;
	}

	function surpriseMe() {
		const variant = randomSurprise();
		activeQuestion = {
			...variant,
			type: 'sandbox_sql',
			question_text: variant.question_text
		};
		usingSurprise = true;
		passed = false;
		checkResult = null;
	}

	function typeSolution() {
		solutionTyped = '';
		let i = 0;
		const text = getSolutionText();
		const interval = setInterval(() => {
			if (i < text.length) {
				solutionTyped += text[i];
				i += 1;
			} else {
				clearInterval(interval);
			}
		}, 12);
	}

	function insertFromSchema(text) {
		editorRef?.insertText(text);
	}

	export function getState() {
		return { user_sql: sql, passed, hints_used: hintsRevealed, check_attempts: checkAttempts };
	}

	export function isPassed() {
		return passed;
	}
</script>

<SandboxCelebration active={celebrate} />

<div class="sandbox" class:compact>
	<div class="sandbox-layout">
		{#if !compact}
			<div class="sidebar">
				<SchemaBrowser dataset={q.dataset} onInsert={insertFromSchema} />
			</div>
		{/if}

		<div class="workspace">
			<div class="problem-card">
				<div class="problem-head">
					<span class="problem-tag">SQL Challenge</span>
					<div class="difficulty">
						<span class="diff-label">Difficulty</span>
						<div class="diff-track">
							<div class="diff-fill" style="width: {(difficulty / 7) * 100}%"></div>
						</div>
						<span class="diff-val">{difficulty}/7</span>
					</div>
				</div>
				<p class="problem-text">{q.question_text}</p>
			</div>

			<div class="toolbar">
				{#if allowSurprise && !compact}
					<button class="tb surprise" onclick={surpriseMe}>Surprise me</button>
				{/if}
				<button class="tb hint" onclick={revealHint} disabled={hintsRevealed >= hints.length}>
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M9 18h6M10 22h4M12 2a7 7 0 0 0-4 12.7V17h8v-2.3A7 7 0 0 0 12 2z" />
					</svg>
					Hint {hintsRevealed > 0 ? `(${hintsRevealed}/${hints.length})` : ''}
				</button>
				{#if (solutionSql || usingSurprise) && q.solution_sql}
					<button class="tb solution" onclick={toggleSolution}>
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
							<circle cx="12" cy="12" r="3" />
						</svg>
						{showSolution ? 'Hide' : 'Show'} solution
					</button>
				{/if}
				<button class="tb check" onclick={handleCheck} disabled={checking || !sql.trim()}>
					{#if checking}
						Checking...
					{:else if passed}
						Passed
					{:else}
						Check my answer
					{/if}
				</button>
				<button class="tb run" onclick={handleRun} disabled={running || !sql.trim()}>
					{running ? 'Running...' : 'Run'}
					<kbd>⌘↵</kbd>
				</button>
			</div>

			{#if hintsRevealed > 0}
				<div class="hints-panel">
					{#each hints.slice(0, hintsRevealed) as hint, i (i)}
						<div class="hint-row" style="animation-delay: {i * 0.1}s">
							<span class="hint-num">{i + 1}</span>
							<span>{hint}</span>
						</div>
					{/each}
				</div>
			{/if}

			{#if showSolution && solutionSql}
				<div class="solution-panel">
					<span class="sol-label">Solution</span>
					<pre><code>{solutionTyped || getSolutionText()}</code></pre>
				</div>
			{/if}

			{#if checkResult && !checkResult.passed && checkResult.issues?.length}
				<div class="issues-panel">
					{#each checkResult.issues as issue, i (i)}
						<p>{issue}</p>
					{/each}
				</div>
			{/if}

			<SqlEditor bind:this={editorRef} bind:value={sql} onRun={handleRun} minHeight={compact ? 120 : 160} />

			<QueryResults
				{result}
				{error}
				{diffMode}
				expected={checkResult?.expected}
				{checkResult}
			/>
		</div>
	</div>
</div>

<style>
	.sandbox {
		width: 100%;
	}

	.sandbox-layout {
		display: grid;
		grid-template-columns: 220px 1fr;
		gap: 14px;
		min-height: 480px;
	}

	.compact .sandbox-layout {
		grid-template-columns: 1fr;
		min-height: auto;
	}

	.sidebar {
		min-height: 0;
	}

	.workspace {
		display: flex;
		flex-direction: column;
		gap: 10px;
		min-width: 0;
	}

	.problem-card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 14px 16px;
	}

	.problem-head {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: 8px;
		gap: 12px;
		flex-wrap: wrap;
	}

	.problem-tag {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.07em;
		color: var(--accent-bright);
		background: var(--accent-soft);
		padding: 3px 8px;
		border-radius: 4px;
	}

	.difficulty {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 12px;
	}

	.diff-label {
		color: var(--text-faint);
	}

	.diff-track {
		width: 80px;
		height: 4px;
		background: var(--border);
		border-radius: 2px;
		overflow: hidden;
	}

	.diff-fill {
		height: 100%;
		background: linear-gradient(90deg, var(--up), var(--accent));
		border-radius: 2px;
		transition: width 0.3s;
	}

	.diff-val {
		color: var(--text-dim);
		font-weight: 600;
		font-size: 11px;
	}

	.problem-text {
		font-size: 14.5px;
		line-height: 1.55;
		color: var(--text);
		margin: 0;
	}

	.toolbar {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
	}

	.tb {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		padding: 7px 14px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		transition: border-color 0.15s, background 0.15s;
	}

	.tb:hover:not(:disabled) {
		border-color: var(--accent);
		background: var(--accent-soft);
	}

	.tb:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.tb.surprise {
		color: var(--warn);
		border-color: color-mix(in srgb, var(--warn) 40%, var(--border));
	}

	.tb.hint {
		color: var(--accent-bright);
		border-color: color-mix(in srgb, var(--accent) 40%, var(--border));
	}

	.tb.solution {
		color: var(--gold);
		border-color: color-mix(in srgb, var(--gold) 40%, var(--border));
	}

	.tb.check {
		color: var(--up);
		border-color: color-mix(in srgb, var(--up) 40%, var(--border));
	}

	.tb.run {
		margin-left: auto;
		background: var(--accent);
		color: var(--accent-fg);
		border-color: var(--accent);
	}

	.tb.run:hover:not(:disabled) {
		background: var(--accent-bright);
		border-color: var(--accent-bright);
	}

	.tb kbd {
		font-size: 10px;
		opacity: 0.8;
		font-family: var(--font);
	}

	.hints-panel {
		background: var(--accent-soft);
		border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--border));
		border-radius: var(--radius-sm);
		padding: 10px 12px;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.hint-row {
		display: flex;
		gap: 10px;
		font-size: 13px;
		color: var(--text);
		animation: hint-in 0.3s ease-out both;
	}

	.hint-num {
		flex-shrink: 0;
		width: 20px;
		height: 20px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--accent);
		color: white;
		border-radius: 50%;
		font-size: 11px;
		font-weight: 700;
	}

	@keyframes hint-in {
		from {
			opacity: 0;
			transform: translateX(-8px);
		}
	}

	.solution-panel {
		background: var(--gold-soft);
		border: 1px solid color-mix(in srgb, var(--gold) 35%, var(--border));
		border-radius: var(--radius-sm);
		padding: 10px 12px;
	}

	.sol-label {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		color: var(--gold);
		letter-spacing: 0.06em;
	}

	.solution-panel pre {
		margin: 8px 0 0;
		font-size: 13px;
		font-family: var(--mono);
		color: var(--text);
		white-space: pre-wrap;
	}

	.issues-panel {
		background: var(--danger-soft);
		border: 1px solid color-mix(in srgb, var(--danger) 35%, var(--border));
		border-radius: var(--radius-sm);
		padding: 10px 12px;
	}

	.issues-panel p {
		margin: 0;
		font-size: 13px;
		color: var(--danger);
	}

	.issues-panel p + p {
		margin-top: 4px;
	}

	@media (max-width: 768px) {
		.sandbox-layout {
			grid-template-columns: 1fr;
		}
	}
</style>
