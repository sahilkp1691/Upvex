<script>
	import { goto } from '$app/navigation';
	import { get, post } from '$lib/api.js';
	import { currentUser, userLoaded, pushToast } from '$lib/stores.js';

	let catalog = $state([]);
	let goals = $state([]);
	let loading = $state(true);
	let busyTopic = $state(null);

	$effect(() => {
		if (!$userLoaded) return;
		if (!$currentUser) {
			goto('/auth');
			return;
		}
		if (!$currentUser.onboarded) {
			goto('/onboarding');
			return;
		}
		load();
	});

	async function load() {
		try {
			[catalog, goals] = await Promise.all([get('/catalog'), get('/goals')]);
		} catch (err) {
			pushToast('Failed to load topics', err.message, 'error');
		} finally {
			loading = false;
		}
	}

	function goalFor(topicId) {
		return goals.find((g) => g.topic_id === topicId);
	}

	async function startTopic(topic) {
		busyTopic = topic.id;
		try {
			const goal = await post('/goals', { topic_id: topic.id });
			if (goal.status === 'diagnostic_pending') goto(`/diagnostic/${goal.id}`);
			else goto(`/roadmap/${goal.id}`);
		} catch (err) {
			pushToast('Could not start topic', err.message, 'error');
		} finally {
			busyTopic = null;
		}
	}
</script>

<svelte:head><title>Learn — Upvex</title></svelte:head>

<div class="page">
	<h1>Pick your next climb</h1>
	<p class="muted">
		Choose a topic and take a short diagnostic — Upvex maps what you already know before building
		your roadmap.
	</p>

	{#if loading}
		<p class="faint">Loading catalog...</p>
	{:else}
		{#each catalog as category (category.id)}
			<section>
				<h2 class="cat-name">{category.name}</h2>
				<p class="muted">{category.description}</p>
				<div class="topics">
					{#each category.topics as topic (topic.id)}
						{@const goal = goalFor(topic.id)}
						<div class="card topic-card">
							<div class="topic-head">
								<h3>{topic.name}</h3>
								<span class="tag tag-dim">{topic.concept_count} concepts</span>
							</div>
							<p class="muted desc">{topic.description}</p>
							{#if goal && goal.status === 'active'}
								<div class="row">
									<span class="tag tag-up">Level {Math.round(goal.level_score ?? 0)}</span>
									<span class="muted small">
										{goal.completed_concepts.length} concept{goal.completed_concepts.length === 1
											? ''
											: 's'} done
									</span>
								</div>
								<button class="btn btn-primary" onclick={() => goto(`/roadmap/${goal.id}`)}>
									Continue
								</button>
							{:else if goal && goal.status === 'diagnostic_pending'}
								<button class="btn btn-primary" onclick={() => goto(`/diagnostic/${goal.id}`)}>
									Resume diagnostic
								</button>
							{:else}
								<button
									class="btn btn-primary"
									disabled={busyTopic === topic.id}
									onclick={() => startTopic(topic)}
								>
									{busyTopic === topic.id ? 'Starting...' : 'Start'}
								</button>
							{/if}
						</div>
					{/each}
				</div>
			</section>
		{/each}
	{/if}
</div>

<style>
	.cat-name {
		margin-top: 34px;
	}

	.topics {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 18px;
		margin-top: 16px;
	}

	.topic-card {
		display: flex;
		flex-direction: column;
		gap: 10px;
	}

	.topic-head {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.topic-head h3 {
		margin: 0;
	}

	.desc {
		flex: 1;
	}

	.row {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.small {
		font-size: 13px;
	}

	.btn {
		align-self: flex-start;
	}
</style>
