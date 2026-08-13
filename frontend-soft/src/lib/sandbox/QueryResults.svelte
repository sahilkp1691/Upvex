<script>
	let {
		result = null,
		error = '',
		diffMode = false,
		expected = null,
		checkResult = null
	} = $props();
</script>

<div class="results-panel">
	{#if error}
		<div class="error-box">
			<span class="err-label">Error</span>
			<pre>{error}</pre>
		</div>
	{:else if result}
		<div class="stats">
			<span>{result.row_count} row{result.row_count === 1 ? '' : 's'}</span>
			<span class="dot">·</span>
			<span>{result.columns.length} col{result.columns.length === 1 ? '' : 's'}</span>
			{#if result.elapsed_ms != null}
				<span class="dot">·</span>
				<span class="timing">{result.elapsed_ms}ms</span>
			{/if}
			{#if checkResult?.passed}
				<span class="pass-badge">Match</span>
			{:else if checkResult && !checkResult.passed}
				<span class="fail-badge">Mismatch</span>
			{/if}
		</div>

		{#if result.columns.length}
			<div class="table-wrap">
				<table>
					<thead>
						<tr>
							{#each result.columns as col, i (i)}
								<th>{col}</th>
							{/each}
						</tr>
					</thead>
					<tbody>
						{#each result.rows as row, ri (ri)}
							<tr class:diff-row={diffMode && checkResult?.cellDiff?.[ri] && !checkResult.cellDiff[ri].rowMatch}>
								{#each row as cell, ci (ci)}
									{@const cellDiff = checkResult?.cellDiff?.[ri]?.cells?.[ci]}
									<td
										class:cell-match={diffMode && cellDiff?.match}
										class:cell-miss={diffMode && cellDiff && !cellDiff.match}
									>
										{cell === '' ? '—' : cell}
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{:else}
			<p class="empty">Query returned no rows.</p>
		{/if}

		{#if diffMode && checkResult && !checkResult.passed && expected}
			<div class="expected-block">
				<span class="exp-label">Expected ({expected.row_count} rows)</span>
				<div class="table-wrap mini">
					<table>
						<thead>
							<tr>
								{#each expected.columns as col, i (i)}
									<th>{col}</th>
								{/each}
							</tr>
						</thead>
						<tbody>
							{#each expected.rows as row, ri (ri)}
								<tr>
									{#each row as cell, ci (ci)}
										<td>{cell}</td>
									{/each}
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	{:else}
		<div class="placeholder">
			<span>Run your query to see results</span>
		</div>
	{/if}
</div>

<style>
	.results-panel {
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		background: var(--bg-card);
		min-height: 120px;
		overflow: hidden;
	}

	.stats {
		display: flex;
		align-items: center;
		gap: 6px;
		padding: 8px 12px;
		font-size: 12px;
		color: var(--text-faint);
		border-bottom: 1px solid var(--border);
		background: var(--bg-elevated);
	}

	.dot {
		opacity: 0.5;
	}

	.timing {
		color: var(--up);
		font-weight: 600;
	}

	.pass-badge {
		margin-left: auto;
		font-weight: 700;
		color: var(--up);
		background: var(--up-soft);
		padding: 2px 8px;
		border-radius: 999px;
		font-size: 11px;
	}

	.fail-badge {
		margin-left: auto;
		font-weight: 700;
		color: var(--danger);
		background: var(--danger-soft);
		padding: 2px 8px;
		border-radius: 999px;
		font-size: 11px;
	}

	.table-wrap {
		overflow-x: auto;
		max-height: 280px;
		overflow-y: auto;
	}

	.table-wrap.mini {
		max-height: 160px;
		margin-top: 6px;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 13px;
		font-family: var(--mono);
	}

	th {
		position: sticky;
		top: 0;
		background: var(--bg-elevated);
		padding: 8px 12px;
		text-align: left;
		font-weight: 650;
		color: var(--text);
		border-bottom: 1px solid var(--border);
		white-space: nowrap;
	}

	td {
		padding: 7px 12px;
		border-bottom: 1px solid var(--border);
		color: var(--text-dim);
	}

	tr:hover td {
		background: var(--bg-hover);
	}

	.cell-match {
		background: var(--up-soft) !important;
		color: var(--up) !important;
	}

	.cell-miss {
		background: var(--danger-soft) !important;
		color: var(--danger) !important;
	}

	.diff-row td {
		border-bottom-color: color-mix(in srgb, var(--danger) 30%, var(--border));
	}

	.error-box {
		padding: 12px;
	}

	.err-label {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		color: var(--danger);
		letter-spacing: 0.06em;
	}

	.error-box pre {
		margin: 6px 0 0;
		font-size: 13px;
		color: var(--danger);
		white-space: pre-wrap;
		font-family: var(--mono);
	}

	.empty,
	.placeholder {
		padding: 24px;
		text-align: center;
		color: var(--text-faint);
		font-size: 13px;
	}

	.expected-block {
		padding: 10px 12px;
		border-top: 1px solid var(--border);
		background: var(--bg-elevated);
	}

	.exp-label {
		font-size: 11px;
		font-weight: 650;
		color: var(--text-faint);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}
</style>
