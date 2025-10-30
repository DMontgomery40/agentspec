#!/usr/bin/env python3
"""
agentspec.extract
--------------------------------
Extracts agent spec blocks from Python files into Markdown or JSON.
"""

import ast
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List


@dataclass
class AgentSpec:
    name: str
    lineno: int
    filepath: str
    block: str


def _extract_block(docstring: str) -> str:
    if not docstring:
        return ""
    if "---agentspec" not in docstring:
        return ""
    start = docstring.find("---agentspec") + len("---agentspec")
    end = docstring.find("---/agentspec")
    return docstring[start:end].strip() if end != -1 else ""


class AgentSpecExtractor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.specs: List[AgentSpec] = []

    def visit_FunctionDef(self, node):
        self._extract(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self._extract(node)
        self.generic_visit(node)

    def _extract(self, node):
        doc = ast.get_docstring(node)
        block = _extract_block(doc)
        if block:
            self.specs.append(
                AgentSpec(name=node.name, lineno=node.lineno, filepath=self.filepath, block=block)
            )


def extract_from_file(path: Path) -> List[AgentSpec]:
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        extractor = AgentSpecExtractor(str(path))
        extractor.visit(tree)
        return extractor.specs
    except Exception:
        return []


def export_markdown(specs: List[AgentSpec], out: Path):
    with out.open("w", encoding="utf-8") as f:
        f.write("# Extracted Agent Specs\n\n")
        for s in specs:
            f.write(f"## {s.name} ({s.filepath}:{s.lineno})\n\n")
            f.write("```yaml\n" + s.block + "\n```\n\n---\n\n")


def export_json(specs: List[AgentSpec], out: Path):
    with out.open("w", encoding="utf-8") as f:
        json.dump([asdict(s) for s in specs], f, indent=2)


def run(target: str, fmt: str = "markdown") -> int:
    path = Path(target)
    files = [path] if path.is_file() else list(path.rglob("*.py"))
    all_specs: List[AgentSpec] = []

    for file in files:
        all_specs.extend(extract_from_file(file))

    if not all_specs:
        print("⚠️ No agent spec blocks found.")
        return 1

    out = Path(f"agent_specs.{ 'json' if fmt == 'json' else 'md'}")
    if fmt == "json":
        export_json(all_specs, out)
    else:
        export_markdown(all_specs, out)

    print(f"✅ Exported {len(all_specs)} specs → {out}")
    return 0
