<script>
	import { getDatasetSchema } from './datasets.js';

	let { dataset = 'employees', onInsert = () => {} } = $props();

	let expanded = $state({});

	let schema = $derived(getDatasetSchema(dataset));

	function toggle(table) {
		expanded[table] = !expanded[table];
	}

	function typeLabel(type) {
		return type.replace('INTEGER', 'int').replace('TEXT', 'text').replace('REAL', 'float');
	}

	function insertRef(table, col) {
		onInsert(`${table}.${col}`);
	}
</script>

<aside class="schema-browser">
	<div class="schema-head">
		<span class="schema-title">Schema</span>
		{#if schema}
			<span class="schema-ds">{schema.label}</span>
		{/if}
	</div>

	{#if schema}
		{#each Object.entries(schema.tables) as [tname, tdef] (tname)}
			<div class="table-block">
				<button class="table-name" onclick={() => toggle(tname)}>
					<span class="chev" class:open={expanded[tname]}>&#9656;</span>
					<span class="tbl">{tname}</span>
					<span class="cnt">{tdef.row_count} rows</span>
				</button>
				{#if expanded[tname] !== false}
					<ul class="cols">
						{#each tdef.columns as col (col.name)}
							<li>
								<button class="col-btn" onclick={() => insertRef(tname, col.name)} title="Click to insert">
									<span class="col-name">{col.name}</span>
									<span class="col-type">{typeLabel(col.type)}</span>
									{#if col.pk}<span class="pk">PK</span>{/if}
								</button>
							</li>
						{/each}
					</ul>
				{/if}
			</div>
		{/each}
	{:else}
		<p class="muted">No schema loaded</p>
	{/if}
</aside>

<style>
	.schema-browser {
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 12px;
		font-size: 13px;
		overflow-y: auto;
		max-height: 100%;
	}

	.schema-head {
		display: flex;
		flex-direction: column;
		gap: 2px;
		margin-bottom: 12px;
		padding-bottom: 10px;
		border-bottom: 1px solid var(--border);
	}

	.schema-title {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-faint);
	}

	.schema-ds {
		font-weight: 650;
		color: var(--text);
		font-size: 13px;
	}

	.table-block {
		margin-bottom: 4px;
	}

	.table-name {
		display: flex;
		align-items: center;
		gap: 6px;
		width: 100%;
		padding: 6px 4px;
		background: none;
		border: none;
		color: var(--accent-bright);
		font-family: var(--mono);
		font-size: 13px;
		font-weight: 600;
		cursor: pointer;
		text-align: left;
		border-radius: 4px;
	}

	.table-name:hover {
		background: var(--bg-hover);
	}

	.chev {
		display: inline-block;
		transition: transform 0.15s;
		font-size: 10px;
		color: var(--text-faint);
	}

	.chev.open {
		transform: rotate(90deg);
	}

	.tbl {
		flex: 1;
	}

	.cnt {
		font-size: 11px;
		color: var(--text-faint);
		font-weight: 400;
		font-family: var(--font);
	}

	.cols {
		list-style: none;
		margin: 0;
		padding: 0 0 4px 18px;
	}

	.col-btn {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		padding: 4px 6px;
		background: none;
		border: none;
		color: var(--text-dim);
		font-family: var(--mono);
		font-size: 12px;
		cursor: pointer;
		text-align: left;
		border-radius: 4px;
	}

	.col-btn:hover {
		background: var(--accent-soft);
		color: var(--text);
	}

	.col-name {
		flex: 1;
	}

	.col-type {
		font-size: 10px;
		color: var(--text-faint);
		text-transform: lowercase;
	}

	.pk {
		font-size: 9px;
		font-weight: 700;
		color: var(--gold);
		background: var(--gold-soft);
		padding: 1px 4px;
		border-radius: 3px;
	}

	.muted {
		color: var(--text-faint);
		font-size: 12px;
	}
</style>
