<script>
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { get, post } from '$lib/api.js';
	import { renderMarkdown } from '$lib/markdown.js';
	import LessonVisual from '$lib/LessonVisual.svelte';
	import { pushToast, gamification, refreshGamification } from '$lib/stores.js';
	import { get as getStore } from 'svelte/store';

	const goalId = page.params.goalId;
	const conceptId = page.params.conceptId;

	let phase = $state('loading'); // loading | generating | lesson | quiz | done | failed
	let content = $state(null);
	let error = $state('');
	let pollTimer = null;
	let loadingMsgIndex = $state(0);
	let leveledUp = $state(false);
	let previousLevel = $state(null);

	const loadingMessages = [
		'Crafting your lesson...',
		'Tuning it to your level...',
		'Checking your root gaps...',
		'Sharpening the examples...',
		'Almost there — plotting your vector up...'
	];

	// quiz state
	let answers = $state([]);
	let quizResult = $state(null);
	let submittingQuiz = $state(false);

	$effect(() => {
		load();
		const msgTimer = setInterval(() => {
			loadingMsgIndex = (loadingMsgIndex + 1) % loadingMessages.length;
		}, 2600);
		return () => {
			clearInterval(msgTimer);
			if (pollTimer) clearTimeout(pollTimer);
		};
	});

	async function load() {
		try {
			handle(await get(`/content/${goalId}/${conceptId}`));
		} catch (err) {
			error = err.message;
			phase = 'failed';
		}
	}

	function handle(res) {
		const prevVisits = content?.visit_count;
		const prevCompletions = content?.completion_count;
		const prevLast = content?.last_visited_at;
		content = {
			...res,
			visit_count: res.visit_count ?? prevVisits ?? 0,
			completion_count: res.completion_count ?? prevCompletions ?? 0,
			last_visited_at: res.last_visited_at ?? prevLast ?? null
		};
		if (res.status === 'ready') {
			answers = res.quiz.questions.map(() => ({ selected_option: null, answer_text: '' }));
			phase = 'lesson';
		} else if (res.status === 'failed') {
			error = res.error || 'Generation failed';
			phase = 'failed';
		} else {
			phase = 'generating';
			pollTimer = setTimeout(poll, 2000);
		}
	}

	function plural(n, word) {
		return `${n} ${word}${n === 1 ? '' : 's'}`;
	}

	async function poll() {
		try {
			handle(await get(`/content/status/${content.content_id}`));
		} catch {
			pollTimer = setTimeout(poll, 3000);
		}
	}

	async function retry() {
		phase = 'loading';
		error = '';
		await load();
	}

	let canSubmitQuiz = $derived(
		content?.quiz &&
			answers.every((a, i) => {
				const q = content.quiz.questions[i];
				return q.type === 'multiple_choice'
					? a.selected_option !== null
					: a.answer_text.trim().length > 0;
			})
	);

	async function submitQuiz() {
		submittingQuiz = true;
		leveledUp = false;
		const before = getStore(gamification);
		previousLevel = before?.level ?? null;
		try {
			quizResult = await post(`/content/${goalId}/${conceptId}/submit-quiz`, {
				generated_content_id: content.content_id,
				answers: answers.map((a, i) => ({
					question_index: i,
					selected_option: a.selected_option,
					answer_text: a.answer_text || null
				}))
			});
			phase = 'done';
			if (previousLevel != null && quizResult.level > previousLevel) {
				leveledUp = true;
			}
			await refreshGamification(get);
			pushToast(`+${quizResult.xp_earned} XP`, `Streak: ${quizResult.streak.current} days`, 'xp');
			for (const b of quizResult.badges_earned) {
				pushToast(`Badge earned: ${b.name}`, b.description, 'badge', 6000);
			}
			if (leveledUp) {
				pushToast(`Level up!`, `You reached level ${quizResult.level}`, 'xp', 5000);
			}
		} catch (err) {
			pushToast('Quiz submission failed', err.message, 'error');
		} finally {
			submittingQuiz = false;
		}
	}

	let levelPct = $derived(
		quizResult?.xp_to_next_level != null
			? Math.min(
					100,
					Math.round(
						(quizResult.xp_into_level /
							(quizResult.xp_into_level + quizResult.xp_to_next_level || 1)) *
							100
					)
				)
			: 0
	);
</script>

<svelte:head><title>Lesson — Upvex</title></svelte:head>

<div class="page lesson-page">
	{#if phase === 'loading'}
		<p class="faint center">Loading...</p>
	{:else if phase === 'generating'}
		<div class="generating">
			<div class="pulse-arrow">
				<svg width="58" height="58" viewBox="0 0 24 24" fill="none">
					<path d="M12 3 L20 19 L12 14.5 L4 19 Z" fill="var(--accent)" />
				</svg>
			</div>
			<h2>{loadingMessages[loadingMsgIndex]}</h2>
			{#if content?.visit_count}
				<p class="visit-meta center-meta">
					Visited {plural(content.visit_count, 'time')} · Completed {plural(
						content.completion_count ?? 0,
						'time'
					)}
				</p>
			{/if}
			<p class="muted">
				Upvex is generating this lesson specifically for your profile — your level, your gaps, your
				style. First time takes a moment; it's cached for you and similar learners after.
			</p>
		</div>
	{:else if phase === 'failed'}
		<div class="card center-card">
			<h2>Generation hit a snag</h2>
			<p class="muted">{error}</p>
			<button class="btn btn-primary" onclick={retry}>Try again</button>
		</div>
	{:else if phase === 'lesson' && content?.lesson}
		<article class="lesson">
			<a href={`/roadmap/${goalId}`} class="back">Back to roadmap</a>
			{#if content.visit_count != null}
				<p class="visit-meta">
					Visited {plural(content.visit_count, 'time')} · Completed {plural(
						content.completion_count ?? 0,
						'time'
					)}
				</p>
			{/if}
			<h1>{content.lesson.title}</h1>
			<p class="intro">{content.lesson.intro}</p>

			{#each content.lesson.sections as section, i (i)}
				<section>
					<h2>{section.heading}</h2>
					<div class="md-body">{@html renderMarkdown(section.body)}</div>
					{#if section.visual}
						<LessonVisual visual={section.visual} />
					{/if}
					{#if section.code_example}
						<pre><code>{section.code_example.code}</code></pre>
					{/if}
				</section>
			{/each}

			<div class="card takeaways">
				<h3>Key takeaways</h3>
				<ul>
					{#each content.lesson.key_takeaways as t, i (i)}
						<li>{t}</li>
					{/each}
				</ul>
			</div>

			<div class="card check">
				<h3>Before the quiz, think about this</h3>
				<p class="muted">{content.lesson.check_understanding}</p>
			</div>

			<button class="btn btn-primary big" onclick={() => (phase = 'quiz')}>
				Take the quiz
			</button>
		</article>
	{:else if phase === 'quiz' && content?.quiz}
		<div class="quiz">
			<h1>Quick check</h1>
			<p class="muted">Your answers update your knowledge map — honest attempts beat guesses.</p>
			{#each content.quiz.questions as q, i (i)}
				<div class="card q-block">
					<p class="q-text"><strong>{i + 1}.</strong> {q.question_text}</p>
					{#if q.type === 'multiple_choice'}
						<div class="options">
							{#each q.options as opt, oi (oi)}
								<button
									class="option"
									class:selected={answers[i].selected_option === oi}
									onclick={() => (answers[i].selected_option = oi)}
								>
									{opt}
								</button>
							{/each}
						</div>
					{:else}
						<textarea
							class="input"
							rows="3"
							placeholder="A sentence or two..."
							bind:value={answers[i].answer_text}
						></textarea>
					{/if}
				</div>
			{/each}
			<button
				class="btn btn-primary big"
				disabled={!canSubmitQuiz || submittingQuiz}
				onclick={submitQuiz}
			>
				{submittingQuiz ? 'Scoring...' : 'Submit quiz'}
			</button>
		</div>
	{:else if phase === 'done' && quizResult}
		<div class="done">
			{#if leveledUp}
				<div class="level-up-banner">Level up — you reached level {quizResult.level}</div>
			{/if}

			<div class="card score-card">
				<span class="label">Quiz score</span>
				<div class="score-num">{Math.round(quizResult.quiz_score)}</div>
				<div class="reward-row">
					<span class="reward xp">+{quizResult.xp_earned} XP</span>
					<span class="reward streak">
						{quizResult.streak.current} day streak
					</span>
					{#if quizResult.level}
						<span class="reward lvl">Level {quizResult.level}</span>
					{/if}
				</div>
				{#if quizResult.xp_to_next_level != null}
					<div class="level-progress">
						<div class="progress-bar">
							<span style="width: {levelPct}%"></span>
						</div>
						<span class="faint lp-meta"
							>{quizResult.xp_to_next_level} XP to level {quizResult.level + 1}</span
						>
					</div>
				{/if}
				{#if quizResult.root_gap_resolved}
					<p class="resolved">Root gap resolved — concepts that depended on this just got closer.</p>
				{/if}
			</div>

			{#if quizResult.badges_earned?.length}
				<div class="badge-reveal">
					{#each quizResult.badges_earned as b (b.id)}
						<div class="badge-tile earned">
							<span class="tag tag-gold">New badge</span>
							<span class="b-name">{b.name}</span>
							<span class="b-desc">{b.description}</span>
						</div>
					{/each}
				</div>
			{/if}

			<div class="card review">
				<h3>Answer review</h3>
				{#each quizResult.review as r (r.question_index)}
					{@const q = content.quiz.questions[r.question_index]}
					<div class="review-row">
						<span class="mark" class:good={r.correct}>{r.correct ? 'Correct' : 'Missed'}</span>
						<div>
							<p class="rq">{q.question_text}</p>
							{#if r.explanation}<p class="muted rexp">{r.explanation}</p>{/if}
						</div>
					</div>
				{/each}
			</div>

			{#if quizResult.gap_reasoning}
				<div class="card">
					<h3>Where you stand now</h3>
					<p>{quizResult.gap_reasoning}</p>
				</div>
			{/if}

			<button class="btn btn-primary big" onclick={() => goto(`/roadmap/${goalId}`)}>
				Back to your roadmap
			</button>
		</div>
	{/if}
</div>

<style>
	.lesson-page {
		max-width: 760px;
	}

	.center {
		text-align: center;
		padding-top: 80px;
	}

	.generating {
		text-align: center;
		padding-top: 90px;
		max-width: 480px;
		margin: 0 auto;
	}

	.pulse-arrow {
		animation: upvex-pulse 1.2s ease-in-out infinite;
		margin-bottom: 18px;
	}

	.center-card {
		text-align: center;
		margin-top: 60px;
	}

	.back {
		display: inline-block;
		margin-bottom: 18px;
		color: var(--text-dim);
		font-size: 14px;
	}

	.visit-meta {
		margin: -8px 0 10px;
		font-size: 13px;
		color: var(--text-faint);
		letter-spacing: 0.01em;
	}

	.visit-meta.center-meta {
		margin: 0 0 12px;
	}

	.intro {
		font-size: 17px;
		color: var(--text-dim);
	}

	section {
		margin-top: 28px;
	}

	.md-body {
		font-size: 15.5px;
		color: var(--text);
	}

	.md-body :global(p) {
		margin: 0 0 0.9em;
	}

	.md-body :global(p:last-child) {
		margin-bottom: 0;
	}

	.md-body :global(ul),
	.md-body :global(ol) {
		margin: 0 0 0.9em;
		padding-left: 1.35em;
	}

	.md-body :global(li) {
		margin-bottom: 0.35em;
	}

	.md-body :global(strong) {
		font-weight: 650;
		color: var(--text);
	}

	.md-body :global(blockquote) {
		margin: 0 0 0.9em;
		padding: 8px 14px;
		border-left: 3px solid var(--accent);
		color: var(--text-dim);
		background: var(--bg-elevated);
		border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
	}

	.md-body :global(pre) {
		margin: 0 0 0.9em;
	}

	.md-body :global(.table-wrap) {
		width: 100%;
		max-width: 100%;
		overflow-x: auto;
		margin: 1em 0;
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
	}

	.md-body :global(table) {
		width: 100%;
		min-width: 520px;
		border-collapse: collapse;
		font-size: 14px;
		line-height: 1.45;
		margin: 0;
	}

	.md-body :global(thead) {
		background: var(--bg-elevated);
	}

	.md-body :global(th),
	.md-body :global(td) {
		padding: 10px 14px;
		text-align: left;
		vertical-align: top;
		border-bottom: 1px solid var(--border);
		border-right: 1px solid var(--border);
	}

	.md-body :global(th:last-child),
	.md-body :global(td:last-child) {
		border-right: none;
	}

	.md-body :global(tbody tr:last-child td) {
		border-bottom: none;
	}

	.md-body :global(th) {
		font-weight: 650;
		color: var(--text);
		white-space: nowrap;
	}

	.md-body :global(td) {
		color: var(--text-dim);
	}

	.md-body :global(tr:hover td) {
		background: var(--bg-hover);
	}

	.takeaways {
		margin-top: 30px;
	}

	.takeaways ul {
		margin: 8px 0 0;
		padding-left: 20px;
	}

	.takeaways li {
		margin-bottom: 6px;
	}

	.check {
		margin-top: 18px;
		border-left: 3px solid var(--accent);
	}

	.big {
		margin-top: 28px;
		padding: 13px 30px;
		font-size: 16px;
	}

	.q-block {
		margin-top: 16px;
	}

	.q-text {
		font-size: 15.5px;
	}

	.options {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.option {
		text-align: left;
		padding: 11px 15px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
		font-size: 14.5px;
		cursor: pointer;
	}

	.option:hover {
		border-color: var(--up);
	}

	.option.selected {
		border-color: var(--up);
		background: var(--up-soft);
	}

	.done {
		display: flex;
		flex-direction: column;
		gap: 18px;
	}

	.score-card {
		text-align: center;
		padding: 30px;
	}

	.score-num {
		font-family: var(--font-display);
		font-size: 58px;
		font-weight: 800;
		background: linear-gradient(100deg, var(--accent-bright), var(--up));
		-webkit-background-clip: text;
		background-clip: text;
		color: transparent;
		line-height: 1.1;
	}

	.reward-row {
		display: flex;
		flex-wrap: wrap;
		justify-content: center;
		gap: 10px;
		margin-top: 8px;
	}

	.reward {
		font-size: 13.5px;
		font-weight: 650;
		padding: 5px 12px;
		border-radius: 999px;
		border: 1px solid var(--border);
		background: var(--bg-elevated);
	}

	.reward.xp {
		color: var(--gold);
		border-color: color-mix(in srgb, var(--gold) 40%, var(--border));
	}

	.reward.streak {
		color: var(--warn);
		border-color: color-mix(in srgb, var(--warn) 40%, var(--border));
	}

	.reward.lvl {
		color: var(--up);
		border-color: color-mix(in srgb, var(--up) 40%, var(--border));
	}

	.level-progress {
		margin: 18px auto 0;
		max-width: 280px;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	.lp-meta {
		font-size: 12.5px;
	}

	.badge-reveal {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
		gap: 12px;
	}

	.resolved {
		color: var(--up);
		font-weight: 600;
		margin-top: 14px;
	}

	.review-row {
		display: grid;
		grid-template-columns: 74px 1fr;
		gap: 14px;
		padding: 12px 0;
		border-top: 1px solid var(--border);
	}

	.review-row:first-of-type {
		border-top: none;
	}

	.mark {
		font-size: 12px;
		font-weight: 700;
		color: var(--danger);
		text-transform: uppercase;
		letter-spacing: 0.04em;
		padding-top: 3px;
	}

	.mark.good {
		color: var(--up);
	}

	.rq {
		margin-bottom: 4px;
		font-size: 14.5px;
	}

	.rexp {
		font-size: 13.5px;
		margin: 0;
	}
</style>
