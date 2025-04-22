from typing import Dict, List, Set
from paragraph_model import Paragraph


class ParagraphGraph:
    def __init__(self, paragraphs: Dict[int, Paragraph]):
        self.nodes: Dict[int, Paragraph] = paragraphs
        self.edges: Dict[int, List[int]] = self.build_edges()

    def build_edges(self) -> Dict[int, List[int]]:
        edges = {}
        for number, para in self.nodes.items():
            links = para.get_links()
            edges[number] = links
        return edges

    def get_neighbors(self, number: int) -> List[int]:
        """Zwraca listę paragrafów dostępnych z danego paragrafu."""
        return self.edges.get(number, [])

    def get_backlinks(self, target: int) -> List[int]:
        """Zwraca listę paragrafów, które prowadzą do danego."""
        backlinks = []
        for src, links in self.edges.items():
            if target in links:
                backlinks.append(src)
        return backlinks

    def find_dead_ends(self) -> List[int]:
        """Zwraca paragrafy, które nie prowadzą do żadnego innego."""
        return [num for num, links in self.edges.items() if not links]

    def find_orphans(self) -> List[int]:
        """Zwraca paragrafy, do których nikt nie prowadzi."""
        all_targets: Set[int] = set()
        for targets in self.edges.values():
            all_targets.update(targets)
        all_sources = set(self.nodes.keys())
        return sorted(list(all_sources - all_targets))

    def get_all_paths_from(self, start: int, depth: int = 5) -> List[List[int]]:
        """Zwraca wszystkie ścieżki od startowego paragrafu do zadanego poziomu głębokości."""
        paths = []

        def dfs(current_path: List[int]):
            if len(current_path) >= depth:
                paths.append(current_path[:])
                return
            current = current_path[-1]
            for neighbor in self.get_neighbors(current):
                if neighbor not in current_path:  # unika cykli
                    current_path.append(neighbor)
                    dfs(current_path)
                    current_path.pop()

        dfs([start])
        return paths

    def __str__(self):
        lines = [f"{num} -> {links}" for num, links in self.edges.items()]
        return "\n".join(lines)
