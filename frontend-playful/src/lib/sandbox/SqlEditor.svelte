<script>
	import { onMount, onDestroy } from 'svelte';
	import { EditorView, keymap, lineNumbers, highlightActiveLine, drawSelection } from '@codemirror/view';
	import { EditorState } from '@codemirror/state';
	import { defaultKeymap, history, historyKeymap, indentWithTab } from '@codemirror/commands';
	import { sql } from '@codemirror/lang-sql';
	import { syntaxHighlighting, defaultHighlightStyle } from '@codemirror/language';

	let {
		value = $bindable('-- your SQL here\n'),
		onRun = () => {},
		placeholder = '-- your SQL here',
		readonly = false,
		minHeight = 180
	} = $props();

	let container;
	let view;

	const runKeymap = keymap.of([
		{
			key: 'Mod-Enter',
			run: () => {
				onRun();
				return true;
			}
		},
		...defaultKeymap,
		...historyKeymap,
		indentWithTab
	]);

	const theme = EditorView.theme({
		'&': {
			backgroundColor: 'var(--pre-bg)',
			color: 'var(--text)',
			fontSize: '14px',
			fontFamily: 'var(--mono)'
		},
		'.cm-content': {
			caretColor: 'var(--accent)',
			padding: '12px 0',
			minHeight: `${minHeight}px`
		},
		'.cm-gutters': {
			backgroundColor: 'var(--bg-elevated)',
			color: 'var(--text-faint)',
			border: 'none',
			borderRight: '1px solid var(--border)'
		},
		'.cm-activeLine': { backgroundColor: 'rgba(61, 139, 253, 0.06)' },
		'.cm-selectionBackground, &.cm-focused .cm-selectionBackground': {
			backgroundColor: 'rgba(61, 139, 253, 0.22) !important'
		},
		'.cm-cursor': { borderLeftColor: 'var(--accent)' },
		'.cm-line': { padding: '0 12px 0 4px' }
	});

	onMount(() => {
		view = new EditorView({
			state: EditorState.create({
				doc: value,
				extensions: [
					lineNumbers(),
					highlightActiveLine(),
					drawSelection(),
					history(),
					sql(),
					syntaxHighlighting(defaultHighlightStyle, { fallback: true }),
					theme,
					runKeymap,
					EditorView.updateListener.of((update) => {
						if (update.docChanged) {
							value = update.state.doc.toString();
						}
					}),
					EditorState.readOnly.of(readonly),
					EditorView.contentAttributes.of({ 'aria-label': 'SQL editor' })
				]
			}),
			parent: container
		});
	});

	onDestroy(() => view?.destroy());

	$effect(() => {
		if (!view) return;
		const current = view.state.doc.toString();
		if (value !== current) {
			view.dispatch({
				changes: { from: 0, to: current.length, insert: value }
			});
		}
	});

	export function insertText(text) {
		if (!view) return;
		const pos = view.state.selection.main.head;
		view.dispatch({
			changes: { from: pos, insert: text },
			selection: { anchor: pos + text.length }
		});
		view.focus();
	}

	export function focus() {
		view?.focus();
	}
</script>

<div class="sql-editor" bind:this={container} style="--min-h: {minHeight}px"></div>

<style>
	.sql-editor {
		border: 1px solid var(--border-strong);
		border-radius: var(--radius-sm);
		overflow: hidden;
		background: var(--pre-bg);
	}

	.sql-editor :global(.cm-editor) {
		min-height: var(--min-h);
	}

	.sql-editor :global(.cm-scroller) {
		overflow: auto;
	}
</style>
