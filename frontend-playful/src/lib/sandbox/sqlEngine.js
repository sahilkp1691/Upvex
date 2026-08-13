import initSqlJs from 'sql.js/dist/sql-wasm.js';
import wasmUrl from 'sql.js/dist/sql-wasm.wasm?url';
import { SQL_DATASETS } from './datasets.js';

let sqlPromise = null;
const dbCache = new Map();

function normalizeCell(value) {
	if (value === null || value === undefined) return 'NULL';
	if (typeof value === 'number') return String(Number(value.toPrecision(12)));
	return String(value).trim();
}

async function getSql() {
	if (!sqlPromise) {
		sqlPromise = initSqlJs({ locateFile: () => wasmUrl });
	}
	return sqlPromise;
}

function buildDatabase(SQL, datasetName) {
	const ds = SQL_DATASETS[datasetName];
	if (!ds) throw new Error(`Unknown dataset: ${datasetName}`);

	const db = new SQL.Database();
	for (const [tname, tdef] of Object.entries(ds.tables)) {
		const colDefs = tdef.columns
			.map((c) => `${c.name} ${c.type}` + (c.pk ? ' PRIMARY KEY' : ''))
			.join(', ');
		db.run(`CREATE TABLE ${tname} (${colDefs})`);
		if (tdef.rows.length) {
			const placeholders = tdef.columns.map(() => '?').join(', ');
			const stmt = db.prepare(`INSERT INTO ${tname} VALUES (${placeholders})`);
			for (const row of tdef.rows) {
				stmt.run(row);
			}
			stmt.free();
		}
	}
	return db;
}

export async function getDb(datasetName) {
	if (dbCache.has(datasetName)) return dbCache.get(datasetName);
	const SQL = await getSql();
	const db = buildDatabase(SQL, datasetName);
	dbCache.set(datasetName, db);
	return db;
}

export function invalidateDb(datasetName) {
	const db = dbCache.get(datasetName);
	if (db) {
		db.close();
		dbCache.delete(datasetName);
	}
}

export async function runQuery(datasetName, sql) {
	const cleaned = sql.trim().replace(/;+\s*$/, '');
	if (!cleaned) throw new Error('Query is empty');

	const upper = cleaned.replace(/\s+/g, ' ').toUpperCase();
	const forbidden = ['INSERT ', 'UPDATE ', 'DELETE ', 'DROP ', 'ALTER ', 'CREATE ', 'ATTACH ', 'PRAGMA '];
	if (forbidden.some((tok) => upper.includes(tok))) {
		throw new Error('Only read-only SELECT queries are allowed');
	}
	if (!upper.startsWith('SELECT') && !upper.startsWith('WITH')) {
		throw new Error('Query must start with SELECT or WITH');
	}

	const start = performance.now();
	const db = await getDb(datasetName);
	try {
		const result = db.exec(cleaned);
		const elapsed = Math.round(performance.now() - start);
		if (!result.length) {
			return { columns: [], rows: [], row_count: 0, elapsed_ms: elapsed };
		}
		const { columns, values } = result[0];
		const rows = values.map((row) => row.map(normalizeCell));
		return { columns, rows, row_count: rows.length, elapsed_ms: elapsed };
	} catch (err) {
		throw new Error(err.message || String(err));
	}
}

function normalizeColumns(columns) {
	return (columns || []).map((c) => c.trim().toLowerCase());
}

function rowSignature(columns, rows, orderSensitive) {
	const normCols = normalizeColumns(columns);
	const payload = orderSensitive
		? { columns: normCols, rows }
		: { columns: [...normCols].sort(), rows: [...rows].sort((a, b) => a.join('|').localeCompare(b.join('|'))) };
	return JSON.stringify(payload);
}

export function compareResults(expected, actual, { orderSensitive = false } = {}) {
	const expCols = normalizeColumns(expected.columns);
	const actCols = normalizeColumns(actual.columns);
	const expRows = expected.rows || [];
	const actRows = actual.rows || [];

	const colMatch =
		expCols.length === actCols.length &&
		(orderSensitive ? expCols.join() === actCols.join() : [...expCols].sort().join() === [...actCols].sort().join());

	const dataMatch =
		colMatch && rowSignature(expected.columns, expRows, orderSensitive) === rowSignature(actual.columns, actRows, orderSensitive);

	const issues = [];
	if (!colMatch) issues.push(`Expected columns [${expCols.join(', ')}], got [${actCols.join(', ')}]`);
	else if (expRows.length !== actRows.length) {
		issues.push(`Expected ${expRows.length} row(s), got ${actRows.length}`);
	} else if (!dataMatch) {
		issues.push('Row values do not match the expected result');
	}

	const cellDiff = buildCellDiff(expCols, expRows, actRows, orderSensitive);

	return {
		passed: colMatch && dataMatch,
		column_match: colMatch,
		row_count_match: expRows.length === actRows.length,
		expected_row_count: expRows.length,
		actual_row_count: actRows.length,
		issues,
		cellDiff
	};
}

function buildCellDiff(columns, expectedRows, actualRows, orderSensitive) {
	const diff = [];
	const maxRows = Math.max(expectedRows.length, actualRows.length);
	for (let r = 0; r < maxRows; r++) {
		const expRow = expectedRows[r] || [];
		const actRow = actualRows[r] || [];
		const cells = [];
		for (let c = 0; c < columns.length; c++) {
			const exp = expRow[c] ?? '';
			const act = actRow[c] ?? '';
			cells.push({ expected: exp, actual: act, match: exp === act });
		}
		diff.push({ row: r, cells, rowMatch: cells.every((cell) => cell.match) });
	}
	if (!orderSensitive && diff.length > 1) {
		return diff;
	}
	return diff;
}

export async function checkAnswer(datasetName, userSql, solutionSql, { orderSensitive = false } = {}) {
	const expected = await runQuery(datasetName, solutionSql);
	let actual;
	try {
		actual = await runQuery(datasetName, userSql);
	} catch (err) {
		return {
			passed: false,
			error: err.message,
			issues: [err.message],
			expected
		};
	}
	const comparison = compareResults(expected, actual, { orderSensitive });
	return { ...comparison, expected, actual };
}
