#!/usr/bin/env python3
"""
agentspec.extract
--------------------------------
Extracts agent spec blocks from Python files into Markdown or JSON with full YAML parsing.
"""

import ast
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class AgentSpec:
    name: str
    lineno: int
    filepath: str
    raw_block: str
    parsed_data: Dict[str, Any] = field(default_factory=dict)
    
    # Structured fields
    what: str = ""
    deps: Dict[str, Any] = field(default_factory=dict)
    why: str = ""
    guardrails: List[str] = field(default_factory=list)
    changelog: List[str] = field(default_factory=list)
    testing: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)


def _extract_block(docstring: str) -> Optional[str]:
    """Extract the agentspec block from a docstring."""
    if not docstring:
        return None
    if "---agentspec" not in docstring:
        return None
    start = docstring.find("---agentspec") + len("---agentspec")
    end = docstring.find("---/agentspec")
    return docstring[start:end].strip() if end != -1 else None


def _parse_yaml_block(block: str) -> Optional[Dict[str, Any]]:
    """Parse YAML from agentspec block."""
    try:
        return yaml.safe_load(block)
    except yaml.YAMLError:
        return None


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
    
    def visit_ClassDef(self, node):
        self._extract(node)
        self.generic_visit(node)

    def _extract(self, node):
        doc = ast.get_docstring(node)
        block = _extract_block(doc)
        
        if not block:
            return
        
        parsed = _parse_yaml_block(block)
        
        spec = AgentSpec(
            name=node.name,
            lineno=node.lineno,
            filepath=self.filepath,
            raw_block=block,
            parsed_data=parsed or {}
        )
        
        # Extract structured fields if parsing succeeded
        if parsed:
            spec.what = str(parsed.get('what', '')).strip()
            spec.deps = parsed.get('deps', {})
            spec.why = str(parsed.get('why', '')).strip()
            spec.guardrails = parsed.get('guardrails', [])
            spec.changelog = parsed.get('changelog', [])
            spec.testing = parsed.get('testing', {})
            spec.performance = parsed.get('performance', {})
        
        self.specs.append(spec)


def extract_from_file(path: Path) -> List[AgentSpec]:
    """Extract all agentspecs from a Python file."""
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(path))
        extractor = AgentSpecExtractor(str(path))
        extractor.visit(tree)
        return extractor.specs
    except Exception as e:
        print(f"Warning: Could not parse {path}: {e}")
        return []


def export_markdown(specs: List[AgentSpec], out: Path):
    """Export to verbose markdown format for agent consumption."""
    with out.open("w", encoding="utf-8") as f:
        f.write("# 🤖 Extracted Agent Specifications\n\n")
        f.write("**This document is auto-generated for AI agent consumption.**\n\n")
        f.write("---\n\n")
        
        for s in specs:
            f.write(f"## {s.name}\n\n")
            f.write(f"**Location:** `{s.filepath}:{s.lineno}`\n\n")
            
            if s.what:
                f.write(f"### What This Does\n\n{s.what}\n\n")
            
            if s.deps:
                f.write(f"### Dependencies\n\n")
                if 'calls' in s.deps:
                    f.write(f"**Calls:**\n")
                    for call in s.deps['calls']:
                        f.write(f"- `{call}`\n")
                    f.write("\n")
                
                if 'called_by' in s.deps:
                    f.write(f"**Called By:**\n")
                    for caller in s.deps['called_by']:
                        f.write(f"- `{caller}`\n")
                    f.write("\n")
                
                if 'config_files' in s.deps:
                    f.write(f"**Config Files:**\n")
                    for cfg in s.deps['config_files']:
                        f.write(f"- `{cfg}`\n")
                    f.write("\n")
            
            if s.why:
                f.write(f"### Why This Approach\n\n{s.why}\n\n")
            
            if s.guardrails:
                f.write(f"### ⚠️ Guardrails (CRITICAL)\n\n")
                for guard in s.guardrails:
                    f.write(f"- **{guard}**\n")
                f.write("\n")
            
            if s.changelog:
                f.write(f"### Changelog\n\n")
                for entry in s.changelog:
                    f.write(f"- {entry}\n")
                f.write("\n")
            
            if s.testing:
                f.write(f"### Testing\n\n")
                f.write(f"```yaml\n{yaml.dump(s.testing, default_flow_style=False)}```\n\n")
            
            if s.performance:
                f.write(f"### Performance Characteristics\n\n")
                for key, value in s.performance.items():
                    f.write(f"- **{key}:** {value}\n")
                f.write("\n")
            
            f.write(f"### Raw YAML Block\n\n")
            f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def export_json(specs: List[AgentSpec], out: Path):
    """Export to JSON for programmatic consumption."""
    data = []
    for s in specs:
        spec_dict = {
            'name': s.name,
            'lineno': s.lineno,
            'filepath': s.filepath,
            'what': s.what,
            'deps': s.deps,
            'why': s.why,
            'guardrails': s.guardrails,
            'changelog': s.changelog,
            'testing': s.testing,
            'performance': s.performance,
            'raw_block': s.raw_block
        }
        data.append(spec_dict)
    
    with out.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def export_agent_context(specs: List[AgentSpec], out: Path):
    """
    Export in a format optimized for injecting into agent context.
    Extremely verbose, includes print() statements.
    """
    with out.open("w", encoding="utf-8") as f:
        f.write("# 🤖 AGENT CONTEXT: Function Specifications\n\n")
        f.write("**AGENTS: You MUST print() and read these specifications before modifying code.**\n\n")
        
        for s in specs:
            f.write(f"## SPEC: {s.name} ({s.filepath}:{s.lineno})\n\n")
            f.write(f"```python\n")
            f.write(f'print("[AGENTSPEC] Reading spec for {s.name}")\n')
            f.write(f'print("[AGENTSPEC] Location: {s.filepath}:{s.lineno}")\n')
            
            if s.what:
                f.write(f'print("[AGENTSPEC] What: {s.what[:100]}...")\n')
            
            if s.guardrails:
                f.write(f'print("[AGENTSPEC] GUARDRAILS ({len(s.guardrails)} items):")\n')
                for i, guard in enumerate(s.guardrails, 1):
                    f.write(f'print("[AGENTSPEC]   {i}. {guard}")\n')
            
            f.write(f"```\n\n")
            
            f.write(f"**Full Specification:**\n\n")
            f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def run(target: str, fmt: str = "markdown") -> int:
    """
    Main extraction runner for CLI.
    
    Args:
        target: File or directory to extract from
        fmt: Output format ('markdown', 'json', 'agent-context')
    """
    path = Path(target)
    files = [path] if path.is_file() else list(path.rglob("*.py"))
    all_specs: List[AgentSpec] = []

    for file in files:
        all_specs.extend(extract_from_file(file))

    if not all_specs:
        print("⚠️  No agent spec blocks found.")
        return 1

    # Determine output file
    if fmt == "json":
        out = Path("agent_specs.json")
        export_json(all_specs, out)
    elif fmt == "agent-context":
        out = Path("AGENT_CONTEXT.md")
        export_agent_context(all_specs, out)
    else:
        out = Path("agent_specs.md")
        export_markdown(all_specs, out)

    print(f"✅ Extracted {len(all_specs)} specs → {out}")
    return 0
