<script>
	import { goto } from '$app/navigation';
	import { post, get } from '$lib/api.js';
	import { currentUser, userLoaded } from '$lib/stores.js';
	import Logo from '$lib/Logo.svelte';
	import ThemeToggle from '$lib/ThemeToggle.svelte';

	const steps = [
		{
			key: 'display_name',
			title: 'What should we call you?',
			sub: 'This shows on the leaderboard.',
			type: 'text'
		},
		{
			key: 'learning_style',
			title: 'How do you learn best?',
			sub: 'Lessons are generated to match — this really changes the content.',
			options: [
				{ value: 'visual', label: 'Visual', hint: 'Diagrams, structure, the big picture first' },
				{ value: 'reading', label: 'Reading', hint: 'Well-written prose with depth' },
				{ value: 'hands_on', label: 'Hands-on', hint: 'Code and concrete scenarios to trace' },
				{ value: 'mixed', label: 'Mix it up', hint: 'A blend of all three' }
			]
		},
		{
			key: 'time_availability',
			title: 'How much time can you give it?',
			sub: 'We use this to suggest pacing, not to guilt you.',
			options: [
				{ value: 'under_30', label: 'Under 30 min/day', hint: 'Short focused sessions' },
				{ value: '30_to_60', label: '30-60 min/day', hint: 'A solid daily block' },
				{ value: 'over_60', label: '1 hour+/day', hint: 'Deep immersion' }
			]
		},
		{
			key: 'motivation',
			title: 'What brings you here?',
			sub: 'Context shapes what "job done" looks like.',
			options: [
				{ value: 'career_switch', label: 'Career switch', hint: 'Moving into a new field' },
				{ value: 'upskilling', label: 'Upskilling', hint: 'Leveling up for my current role' },
				{ value: 'interview_prep', label: 'Interview prep', hint: 'A specific bar to clear' },
				{ value: 'curiosity', label: 'Curiosity', hint: 'Learning for its own sake' }
			]
		},
		{
			key: 'tech_background',
			title: 'Where are you starting from?',
			sub: 'General background — the diagnostic will find your topic-specific level.',
			options: [
				{ value: 'none', label: 'New to tech', hint: 'Little or no programming yet' },
				{ value: 'some_scripting', label: 'Some scripting', hint: 'Python, spreadsheets, SQL basics' },
				{ value: 'data_adjacent', label: 'Data-adjacent', hint: 'Analyst, BI, or similar' },
				{ value: 'professional_dev', label: 'Professional developer', hint: 'Writing software daily' }
			]
		},
		{
			key: 'tone_preference',
			title: 'How should lessons talk to you?',
			sub: 'You can change this later.',
			options: [
				{ value: 'playful', label: 'Playful', hint: 'Energy, personality, the occasional joke' },
				{ value: 'professional', label: 'Professional', hint: 'Crisp and workplace-neutral' },
				{ value: 'neutral', label: 'Neutral', hint: 'Friendly but plain' }
			]
		}
	];

	let stepIndex = $state(0);
	let answers = $state({ display_name: '' });
	let busy = $state(false);
	let error = $state('');

	let step = $derived(steps[stepIndex]);
	let canNext = $derived(
		step.type === 'text' ? answers.display_name?.trim().length > 0 : !!answers[step.key]
	);

	$effect(() => {
		if ($userLoaded && !$currentUser) goto('/auth');
	});

	function pick(value) {
		answers[step.key] = value;
		if (stepIndex < steps.length - 1) setTimeout(() => stepIndex++, 150);
	}

	async function finish() {
		busy = true;
		error = '';
		try {
			await post('/onboarding', {
				learning_style: answers.learning_style,
				time_availability: answers.time_availability,
				motivation: answers.motivation,
				tech_background: answers.tech_background,
				tone_preference: answers.tone_preference,
				display_name: answers.display_name?.trim() || null,
				raw_answers: answers
			});
			currentUser.set(await get('/me'));
			goto('/topics');
		} catch (err) {
			error = err.message;
		} finally {
			busy = false;
		}
	}
</script>

<svelte:head><title>Welcome — Upvex</title></svelte:head>

<div class="page onboard">
	<div class="head">
		<Logo size={24} />
		<ThemeToggle />
	</div>

	<div class="progress">
		{#each steps as s, i (s.key)}
			<div class="seg" class:done={i < stepIndex} class:current={i === stepIndex}></div>
		{/each}
	</div>

	<div class="step-card">
		<h2>{step.title}</h2>
		<p class="muted">{step.sub}</p>

		{#if step.type === 'text'}
			<input
				class="input name-input"
				placeholder="Your name"
				bind:value={answers.display_name}
				onkeydown={(e) => e.key === 'Enter' && canNext && stepIndex++}
			/>
		{:else}
			<div class="options">
				{#each step.options as opt (opt.value)}
					<button
						class="option"
						class:selected={answers[step.key] === opt.value}
						onclick={() => pick(opt.value)}
					>
						<span class="opt-label">{opt.label}</span>
						<span class="opt-hint">{opt.hint}</span>
					</button>
				{/each}
			</div>
		{/if}

		<div class="nav">
			{#if stepIndex > 0}
				<button class="btn" onclick={() => stepIndex--}>Back</button>
			{:else}
				<span></span>
			{/if}
			{#if stepIndex < steps.length - 1}
				<button class="btn btn-primary" disabled={!canNext} onclick={() => stepIndex++}>
					Continue
				</button>
			{:else}
				<button class="btn btn-primary" disabled={!canNext || busy} onclick={finish}>
					{busy ? 'Saving...' : 'Finish'}
				</button>
			{/if}
		</div>
		{#if error}<p class="error">{error}</p>{/if}
	</div>
</div>

<style>
	.onboard {
		max-width: 640px;
	}

	.head {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 26px;
	}

	.progress {
		display: flex;
		gap: 6px;
		margin-bottom: 22px;
	}

	.seg {
		flex: 1;
		height: 4px;
		border-radius: 2px;
		background: var(--border);
	}

	.seg.done {
		background: var(--up);
	}

	.seg.current {
		background: var(--up);
	}

	.step-card {
		padding: 8px 0 30px;
	}

	.name-input {
		margin-top: 12px;
		font-size: 17px;
		padding: 13px 16px;
	}

	.options {
		display: flex;
		flex-direction: column;
		gap: 10px;
		margin-top: 16px;
	}

	.option {
		display: flex;
		flex-direction: column;
		gap: 3px;
		text-align: left;
		padding: 14px 18px;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-strong);
		background: var(--bg-elevated);
		color: var(--text);
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

	.opt-label {
		font-weight: 620;
		font-size: 15.5px;
	}

	.opt-hint {
		color: var(--text-dim);
		font-size: 13.5px;
	}

	.nav {
		display: flex;
		justify-content: space-between;
		margin-top: 26px;
	}

	.error {
		color: var(--danger);
		margin-top: 14px;
	}
</style>
