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
from agentspec.utils import collect_source_files
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
    '''
    " delimiters.

      Inputs: docstring (str) - a docstring that may contain an embedded agentspec YAML block
      Outputs: Optional[str] - the extracted and whitespace-normalized YAML content, or None if delimiters are absent or malformed

      Behavior:
      - Returns None immediately if docstring is falsy (empty, None)
      - Returns None if opening delimiter "" after the opening delimiter
      - Returns None if closing delimiter is not found (prevents partial/malformed extraction)
      - Strips leading and trailing whitespace from extracted content before returning
      - Performs sequential validation with early-exit pattern for O(n) performance

      Edge cases:
      - Malformed delimiters (missing closing tag) safely return None rather than partial content
      - Multiple delimiter pairs: extracts only the first occurrence
      - Whitespace normalization handles inconsistent indentation in docstrings
        deps:
          calls:
            - docstring.find
            - len
            - strip
          imports:
            - agentspec.utils.collect_python_files
            - ast
            - dataclasses.asdict
            - dataclasses.dataclass
            - dataclasses.field
            - json
            - pathlib.Path
            - typing.Any
            - typing.Dict
            - typing.List
            - typing.Optional
            - yaml


    why: |
      String search via find() is faster than regex for literal delimiter matching and avoids regex compilation overhead. The early-exit validation pattern (docstring exists → opening delimiter → closing delimiter) provides both O(n) performance and graceful degradation when delimiters are missing or incomplete. Explicit, unambiguous delimiters ("") are unlikely to appear accidentally in docstrings, reducing false positives. Returning None on any validation failure allows the extraction pipeline to degrade gracefully without raising exceptions, enabling robust batch processing of heterogeneous docstrings.

    guardrails:
      - DO NOT modify delimiter strings without updating all docstring generation code and documentation, as delimiters are the contract between generators and extractors
      - DO NOT remove closing delimiter validation, as it prevents extraction of incomplete or malformed blocks that could corrupt downstream YAML parsing
      - ALWAYS return None on any validation failure to support graceful pipeline degradation and allow callers to handle missing metadata
      - ALWAYS preserve .strip() to normalize whitespace in extracted blocks, ensuring consistent YAML parsing regardless of docstring indentation style
      - DO NOT use regex for delimiter matching without performance benchmarking, as string search is simpler and faster for literal patterns

        changelog:
          - "- 2025-10-29: feat: honor .gitignore and .venv; add agentspec YAML generation; fix quoting; lazy-load generate"
          - "-    """Extract the agentspec block from a docstring.""""
          - "- 2025-10-29: Enhanced extract.py with full YAML parsing and agent-context format"
          - "-        return """
          - "-        return """
          - "-    return docstring[start:end].strip() if end != -1 else """
          - "- 2025-10-29: Add agent spec extraction and export functionality"
        ---/agentspec
    '''
    if not docstring:
        return None
    if "")
    return docstring[start:end].strip() if end != -1 else None


def _parse_yaml_block(block: str) -> Optional[Dict[str, Any]]:
    '''
        '''
    try:
        return yaml.safe_load(block)
    except yaml.YAMLError:
        return None


class AgentSpecExtractor(ast.NodeVisitor):
    def __init__(self, filepath: str):
        """
                """
        self.filepath = filepath
        self.specs: List[AgentSpec] = []

    def visit_FunctionDef(self, node):
        """
                """
        self._extract(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """
                """
        self._extract(node)
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """
                """
        self._extract(node)
        self.generic_visit(node)

    def _extract(self, node):
        '''
                '''
        doc = ast.get_docstring(node)
        block = _extract_block(doc)

        if not block:
            # Fallback: treat raw docstring as a basic spec so extraction works
            if not doc:
                return
            spec = AgentSpec(
                name=node.name,
                lineno=node.lineno,
                filepath=self.filepath,
                raw_block=doc,
                parsed_data={},
            )
            # Use the first non-empty paragraph or line as 'what'
            parts = [p.strip() for p in doc.split("\n\n") if p.strip()] or [p.strip() for p in doc.splitlines() if p.strip()]
            spec.what = parts[0] if parts else ""
            self.specs.append(spec)
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


def extract_agentspec_blocks_text(path: Path) -> List[AgentSpec]:
    """
    Extract agentspec blocks from any source file using text-based parsing.

    Works for JavaScript, TypeScript, and any language with agentspec blocks in comments.
    Looks for  markers in file text.

    
      Parses YAML content within blocks and creates AgentSpec objects.
      Used for JS, TS, and other languages where AST parsing isn't available.

    why: |
      agentspec blocks can appear in ANY language's comments.
      Text-based extraction is language-agnostic and works universally.

      Alternative: Implement AST parsers for every language
      Rejected: Too much work, text-based works for 95% of cases

    guardrails:
      - DO NOT assume Python syntax
      - ALWAYS handle malformed YAML gracefully
      - DO NOT fail entire file on one bad block
    ---/agentspec
    """
    specs = []
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        i = 0
        while i < len(lines):
            line = lines[i]

            # Look for start marker
            if "" in lines[i]:
                        # Found end marker
                        block_text = "\n".join(block_lines)

                        # Try to parse YAML
                        try:
                            parsed = yaml.safe_load(block_text) or {}

                            # Create AgentSpec
                            spec = AgentSpec(
                                name=f"{path.name}:{start_line}",
                                lineno=start_line,
                                filepath=str(path),
                                raw_block=block_text,
                                parsed_data=parsed,
                                what=parsed.get("what", ""),
                                deps=parsed.get("deps", {}),
                                why=parsed.get("why", ""),
                                guardrails=parsed.get("guardrails", []),
                                changelog=parsed.get("changelog", [])
                            )
                            specs.append(spec)
                        except yaml.YAMLError:
                            # Skip malformed YAML blocks
                            pass

                        break
                    else:
                        # Remove comment markers while preserving indentation
                        line_content = lines[i]

                        # Strip leading whitespace to find comment marker
                        stripped = line_content.lstrip()
                        leading_space = len(line_content) - len(stripped)

                        # Remove comment marker but preserve relative indentation
                        if stripped.startswith("* "):
                            # JSDoc-style: "  * content" -> "content"
                            cleaned = stripped[2:]
                        elif stripped.startswith("*"):
                            # JSDoc-style: "  *content" -> "content"
                            cleaned = stripped[1:].lstrip()
                        elif stripped.startswith("// "):
                            # C-style: "  // content" -> "content"
                            cleaned = stripped[3:]
                        elif stripped.startswith("//"):
                            # C-style: "  //content" -> "content"
                            cleaned = stripped[2:].lstrip()
                        elif stripped.startswith("# "):
                            # Python-style: "  # content" -> "content"
                            cleaned = stripped[2:]
                        elif stripped.startswith("#"):
                            # Python-style: "  #content" -> "content"
                            cleaned = stripped[1:].lstrip()
                        else:
                            cleaned = stripped

                        block_lines.append(cleaned)
                        i += 1

            i += 1

    except Exception as e:
        print(f"Warning: Could not extract from {path}: {e}")

    return specs


def extract_from_file(path: Path) -> List[AgentSpec]:
    '''
        '''
    # Detect language by file extension
    if path.suffix == ".py":
        # Use AST-based extraction for Python
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(path))
            extractor = AgentSpecExtractor(str(path))
            extractor.visit(tree)
            return extractor.specs
        except Exception as e:
            print(f"Warning: Could not parse {path}: {e}")
            return []
    else:
        # Use text-based extraction for JS/TS/other languages
        return extract_agentspec_blocks_text(path)


def export_markdown(specs: List[AgentSpec], out: Path):
    '''
        '''
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
    '''
        '''
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
            
            if s.parsed_data:
                f.write(f"**Full Specification (YAML):**\n\n")
                f.write(f"```yaml\n{s.raw_block}\n```\n\n")
            else:
                f.write(f"**Full Specification (Raw Docstring):**\n\n")
                f.write(f"```\n{s.raw_block}\n```\n\n")
            f.write("---\n\n")


def run(target: str, fmt: str = "markdown") -> int:
    """
        """
    path = Path(target)
    files = collect_source_files(path)  # Supports .py, .js, .jsx, .ts, .tsx
    all_specs: List[AgentSpec] = []

    for file in files:
        all_specs.extend(extract_from_file(file))

    if not all_specs:
        print("⚠️  No agent spec blocks or docstrings found.")
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
