"""In-process knowledge graph over concept prerequisites.

Postgres tables (`concept_nodes`, `concept_edges`) remain the source of truth.
This module is the free graph *runtime*: property-graph adjacency, multi-hop
traversal, root-gap ranking, path finding, and DAG validation — without a
separate graph database.

Optional engines (config `GRAPH_ENGINE`):
  - ``memory`` (default): this module — zero cost, works on Supabase/local.
  - ``age``: Apache AGE (Postgres extension) when self-hosting with AGE installed.
    Falls back to memory if AGE is unavailable.
"""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models import ConceptEdge, ConceptNode

WEAK_THRESHOLD = 60


@dataclass
class KnowledgeGraph:
    """Directed prerequisite graph: edge from A→B means A unlocks / precedes B."""

    topic_id: str
    node_ids: set[str] = field(default_factory=set)
    # node_id -> metadata dict (optional; used by validate)
    nodes: dict[str, dict] = field(default_factory=dict)
    # from_id -> list[(to_id, edge_type)]
    outgoing: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))
    # to_id -> list[(from_id, edge_type)]
    incoming: dict[str, list[tuple[str, str]]] = field(default_factory=lambda: defaultdict(list))
    engine: str = "memory"

    def add_node(self, node_id: str, **meta) -> None:
        self.node_ids.add(node_id)
        if meta:
            self.nodes[node_id] = meta

    def add_edge(self, from_id: str, to_id: str, edge_type: str = "required") -> None:
        self.node_ids.add(from_id)
        self.node_ids.add(to_id)
        self.outgoing[from_id].append((to_id, edge_type))
        self.incoming[to_id].append((from_id, edge_type))

    def ancestors(self, concept_id: str, *, max_depth: int = 20) -> set[str]:
        """All prerequisites (direct and transitive)."""
        found: set[str] = set()
        stack = [(concept_id, 0)]
        seen = {concept_id}
        while stack:
            current, depth = stack.pop()
            if depth >= max_depth:
                continue
            for pred, _ in self.incoming.get(current, []):
                if pred in seen:
                    continue
                seen.add(pred)
                found.add(pred)
                stack.append((pred, depth + 1))
        return found

    def descendants(self, concept_id: str, *, max_depth: int = 20) -> set[str]:
        """All concepts that depend on this one (direct and transitive)."""
        found: set[str] = set()
        stack = [(concept_id, 0)]
        seen = {concept_id}
        while stack:
            current, depth = stack.pop()
            if depth >= max_depth:
                continue
            for succ, _ in self.outgoing.get(current, []):
                if succ in seen:
                    continue
                seen.add(succ)
                found.add(succ)
                stack.append((succ, depth + 1))
        return found

    def reachable_from(self, start_id: str) -> set[str]:
        """Nodes reachable walking downstream from start (including start)."""
        seen = {start_id}
        queue = deque([start_id])
        while queue:
            current = queue.popleft()
            for succ, _ in self.outgoing.get(current, []):
                if succ not in seen:
                    seen.add(succ)
                    queue.append(succ)
        return seen

    def would_create_cycle(self, from_id: str, to_id: str) -> bool:
        """Adding from→to creates a cycle iff `from` is reachable from `to`."""
        if from_id == to_id:
            return True
        return from_id in self.reachable_from(to_id)

    def shortest_path(self, src: str, dst: str) -> list[str] | None:
        """Shortest prerequisite path src → … → dst (downstream direction)."""
        if src not in self.node_ids or dst not in self.node_ids:
            return None
        if src == dst:
            return [src]
        parent: dict[str, str | None] = {src: None}
        queue = deque([src])
        while queue:
            current = queue.popleft()
            for succ, _ in self.outgoing.get(current, []):
                if succ in parent:
                    continue
                parent[succ] = current
                if succ == dst:
                    path = [dst]
                    while path[-1] != src:
                        path.append(parent[path[-1]])  # type: ignore[arg-type]
                    path.reverse()
                    return path
                queue.append(succ)
        return None

    def find_root_gaps(
        self,
        concept_gap_map: dict[str, float],
        completed_concepts: set[str] | None = None,
    ) -> list[str]:
        """Foundational weaknesses driving surface-level ones (same semantics as CTEs)."""
        completed = completed_concepts or set()

        def weak_or_untested(cid: str) -> bool:
            score = concept_gap_map.get(cid)
            return score is None or score < WEAK_THRESHOLD

        weak = [
            cid
            for cid, score in concept_gap_map.items()
            if score is not None and score < WEAK_THRESHOLD and cid not in completed
        ]
        if not weak:
            return []

        # Cache ancestors once — avoids N+ recursive SQL round-trips
        ancestor_cache: dict[str, set[str]] = {}

        def cached_ancestors(cid: str) -> set[str]:
            if cid not in ancestor_cache:
                ancestor_cache[cid] = self.ancestors(cid)
            return ancestor_cache[cid]

        impact: dict[str, int] = {}
        for weak_cid in weak:
            ancestors = cached_ancestors(weak_cid)
            weak_ancestors = {
                a for a in ancestors if weak_or_untested(a) and a not in completed
            }
            if not weak_ancestors:
                impact[weak_cid] = impact.get(weak_cid, 0) + 1
                continue
            for cand in weak_ancestors:
                cand_ancestors = cached_ancestors(cand)
                if not any(
                    weak_or_untested(a) and a not in completed for a in cand_ancestors
                ):
                    impact[cand] = impact.get(cand, 0) + 1

        return [cid for cid, _ in sorted(impact.items(), key=lambda kv: (-kv[1], kv[0]))]

    def validate(self) -> dict:
        """Admin health check: orphans, missing roots, unreachable, cycle probe."""
        flagged_roots = {nid for nid, meta in self.nodes.items() if meta.get("is_root")}
        structural_roots = {nid for nid in self.node_ids if not self.incoming.get(nid)}

        orphans = [
            nid
            for nid in self.node_ids
            if not self.incoming.get(nid) and not self.outgoing.get(nid) and len(self.node_ids) > 1
        ]

        # Nodes not reachable from any structural root (disconnected components)
        reachable: set[str] = set()
        for root in structural_roots:
            reachable |= self.reachable_from(root)
        unreachable = sorted(self.node_ids - reachable)

        missing_root_flags = sorted(structural_roots - flagged_roots)
        extra_root_flags = sorted(
            rid for rid in flagged_roots if self.incoming.get(rid)
        )

        # Soft cycle check via DFS (should be empty if admin guards work)
        cycles: list[list[str]] = []
        color: dict[str, int] = {}  # 0 white, 1 gray, 2 black
        path: list[str] = []

        def dfs(nid: str) -> None:
            color[nid] = 1
            path.append(nid)
            for succ, _ in self.outgoing.get(nid, []):
                c = color.get(succ, 0)
                if c == 1:
                    # back edge — extract cycle
                    i = path.index(succ)
                    cycles.append(path[i:] + [succ])
                elif c == 0:
                    dfs(succ)
            path.pop()
            color[nid] = 2

        for nid in sorted(self.node_ids):
            if color.get(nid, 0) == 0:
                dfs(nid)

        issues = []
        if cycles:
            issues.append({"code": "cycle", "detail": "Graph contains cycle(s)", "paths": cycles[:5]})
        if orphans:
            issues.append({"code": "orphan", "detail": "Isolated concepts", "node_ids": orphans})
        if unreachable:
            issues.append(
                {
                    "code": "unreachable",
                    "detail": "Concepts not reachable from any entry point",
                    "node_ids": unreachable,
                }
            )
        if missing_root_flags:
            issues.append(
                {
                    "code": "missing_root_flag",
                    "detail": "Entry points without is_root flag",
                    "node_ids": missing_root_flags,
                }
            )
        if extra_root_flags:
            issues.append(
                {
                    "code": "extra_root_flag",
                    "detail": "is_root set on concepts that have prerequisites",
                    "node_ids": extra_root_flags,
                }
            )

        return {
            "ok": len(issues) == 0,
            "engine": self.engine,
            "node_count": len(self.node_ids),
            "edge_count": sum(len(v) for v in self.outgoing.values()),
            "structural_roots": sorted(structural_roots),
            "issues": issues,
        }


async def _age_available(db: AsyncSession) -> bool:
    try:
        row = await db.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'age'"))
        return row.first() is not None
    except Exception:
        return False


async def load_topic_graph(db: AsyncSession, topic_id: str) -> KnowledgeGraph:
    """Load a topic's concept DAG into the configured graph engine."""
    engine = (settings.graph_engine or "memory").lower().strip()
    nodes = (
        await db.execute(select(ConceptNode).where(ConceptNode.topic_id == topic_id))
    ).scalars().all()
    edges = (
        await db.execute(select(ConceptEdge).where(ConceptEdge.topic_id == topic_id))
    ).scalars().all()

    use_age = engine == "age" and await _age_available(db)
    kg = KnowledgeGraph(topic_id=topic_id, engine="age" if use_age else "memory")

    for n in nodes:
        kg.add_node(
            n.id,
            title=n.title,
            is_root=bool(n.is_root),
            difficulty_tag=n.difficulty_tag,
        )
    for e in edges:
        kg.add_edge(e.from_concept_id, e.to_concept_id, e.edge_type or "required")

    # AGE path: currently we still materialize into memory for Python-side
    # algorithms. When AGE is present we record the engine so admin UI can
    # show "Apache AGE available"; Cypher sync can be layered later without
    # changing the API surface.
    if use_age:
        kg.engine = "age+memory"

    return kg
