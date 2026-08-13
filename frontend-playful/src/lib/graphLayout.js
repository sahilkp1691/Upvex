/** Longest-path DAG layering shared by learner roadmap and admin graph editor. */

export const DEFAULT_NODE_W = 230;
export const DEFAULT_NODE_H = 96;
export const DEFAULT_GAP_X = 26;
export const DEFAULT_GAP_Y = 70;

/**
 * @param {{ nodes: Array<{ id: string, title: string }>, edges: Array<{ id?: string, from: string, to: string, type?: string }> }} graph
 * @param {{ nodeW?: number, nodeH?: number, gapX?: number, gapY?: number }} [opts]
 * @returns {{ pos: Record<string, { x: number, y: number }>, paths: Array<{ d: string, type: string, id?: string, from: string, to: string }>, width: number, height: number, nodes: typeof graph.nodes }}
 */
export function layoutDag(graph, opts = {}) {
	const NODE_W = opts.nodeW ?? DEFAULT_NODE_W;
	const NODE_H = opts.nodeH ?? DEFAULT_NODE_H;
	const GAP_X = opts.gapX ?? DEFAULT_GAP_X;
	const GAP_Y = opts.gapY ?? DEFAULT_GAP_Y;

	const nodes = graph.nodes ?? [];
	const edges = graph.edges ?? [];

	if (!nodes.length) {
		return { pos: {}, paths: [], width: NODE_W + GAP_X * 2, height: NODE_H + GAP_Y, nodes };
	}

	const preds = {};
	for (const e of edges) (preds[e.to] ??= []).push(e.from);

	const layerOf = {};
	const resolve = (id, seen = new Set()) => {
		if (layerOf[id] !== undefined) return layerOf[id];
		if (seen.has(id)) return 0;
		seen.add(id);
		const ps = preds[id] || [];
		const layer = ps.length ? 1 + Math.max(...ps.map((p) => resolve(p, seen))) : 0;
		layerOf[id] = layer;
		return layer;
	};
	nodes.forEach((n) => resolve(n.id));

	const layers = [];
	for (const n of nodes) (layers[layerOf[n.id]] ??= []).push(n);
	layers.forEach((l) => l.sort((a, b) => a.title.localeCompare(b.title)));

	const maxPerLayer = Math.max(1, ...layers.map((l) => (l ? l.length : 0)));
	const width = maxPerLayer * (NODE_W + GAP_X) + GAP_X;
	const height = layers.length * (NODE_H + GAP_Y) + GAP_Y;

	const pos = {};
	layers.forEach((layerNodes, li) => {
		if (!layerNodes?.length) return;
		const rowWidth = layerNodes.length * (NODE_W + GAP_X) - GAP_X;
		const startX = (width - rowWidth) / 2;
		layerNodes.forEach((n, i) => {
			pos[n.id] = {
				x: startX + i * (NODE_W + GAP_X),
				y: GAP_Y / 2 + li * (NODE_H + GAP_Y)
			};
		});
	});

	const paths = edges
		.filter((e) => pos[e.from] && pos[e.to])
		.map((e) => {
			const a = pos[e.from];
			const b = pos[e.to];
			const x1 = a.x + NODE_W / 2;
			const y1 = a.y + NODE_H;
			const x2 = b.x + NODE_W / 2;
			const y2 = b.y;
			const my = (y1 + y2) / 2;
			return {
				id: e.id,
				from: e.from,
				to: e.to,
				d: `M ${x1} ${y1} C ${x1} ${my}, ${x2} ${my}, ${x2} ${y2}`,
				type: e.type ?? 'required'
			};
		});

	return { pos, paths, width, height, nodes };
}
