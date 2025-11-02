#!/usr/bin/env python3
"""
Advanced example parser for AgentSpec training examples.

Adds LLM-in-the-middle analysis for both bad and good documentation and
anchors examples to real repository context (file, function, subject function).

Use stub mode in tests by setting AGENTSPEC_EXAMPLES_STUB=1.

CLI usage (examples):
  python -m agentspec.tools.add_example \
    --file tests/test_extract_javascript_agentspec.py \
    --function test_extract_from_jsdoc_agentspec_block \
    --subject-function agentspec.extract.extract_from_js_file \
    --bad-output "confirms JSDoc parsing..." \
    --correction "Only checks 'what' key exists, not content" \
    --dry-run

  python -m agentspec.tools.add_example \
    --file tests/test_extract_javascript_agentspec.py \
    --function test_extract_from_jsdoc_agentspec_block \
    --subject-function agentspec.extract.extract_from_js_file \
    --good-output "Checks presence of 'what' key..." \
    --require-ask-user \
    --dry-run
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

try:
    import click  # optional for CLI; not required for importing ExampleParser in tests
    _CLICK_AVAILABLE = True
except Exception:  # pragma: no cover - only exercised when click is missing
    click = None  # type: ignore
    _CLICK_AVAILABLE = False

from agentspec.llm import generate_chat


EXAMPLES_FILE = Path(__file__).resolve().parent.parent / "prompts" / "examples.json"


@dataclass
class CodeContext:
    code: str
    language: str
    file: str
    lines: str


class ExampleParser:
    """
    ---agentspec
    what: |
      Orchestrates LLM-driven analysis of documentation quality and converts user-provided examples (bad and/or good) into structured training records anchored to real code context. Provides utilities to extract code context from a repository source file (with function scoping where possible), analyze documentation using an LLM middle layer, enforce best-practice guardrails (including mandatory ASK USER guardrails when requested), and compute dataset composition ratios for quality control.

      Key behaviors:
      - extract_code_context(): returns code snippet and metadata (language, file path, line span) for an anchor function where possible; falls back to whole file
      - analyze_documentation(): calls an LLM (or deterministic stub) to produce JSON with fields why_bad, good_what, good_why, good_guardrails, lesson, pattern_type; supports analyzing both bad_output and good_output
      - make_example(): assembles an example record with code_context, good/bad docs, and guardrails; injects an ASK USER guardrail when required
      - load/save dataset: appends to examples.json unless dry-run
      - compute_ratio(): counts good vs bad examples to help maintain a recommended ratio

      Inputs: user-provided file, function, subject-function, and example texts
      Outputs: structured example record and optional dataset file update

    deps:
      calls:
        - generate_chat
        - json.loads
        - json.dumps
        - Path.read_text
        - Path.write_text
      imports:
        - click
        - dataclasses.dataclass
        - json
        - os
        - pathlib.Path
        - typing

    why: |
      Python string rules and heuristics are insufficient to accurately judge documentation quality or extract generalizable lessons; an LLM is placed in the middle to analyze both bad and good documentation and propose guardrails. Deterministic stub mode enables fast, stable tests without external API calls, aligning with the repository's testing philosophy.

    guardrails:
      - DO NOT write to examples.json unless explicitly requested (dry-run default is safer)
      - DO NOT drop the ASK USER guardrail when require_ask_user=True; inject it if missing
      - ALWAYS anchor examples to real files/functions for context
      - ALWAYS expose a stub mode (AGENTSPEC_EXAMPLES_STUB=1) for tests; never require network in unit tests

    changelog:
      - "2025-11-02: feat: Initial implementation of LLM-backed training example parser (handoff execution)"
    ---/agentspec
    """

    def extract_code_context(self, file_path: str, function_name: Optional[str]) -> CodeContext:
        file = Path(file_path)
        content = file.read_text(encoding="utf-8")

        # Detect language by suffix
        language = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
        }.get(file.suffix, "unknown")

        if language == "python" and function_name:
            try:
                import ast

                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        start = node.lineno
                        end = getattr(node, "end_lineno", node.lineno)
                        lines = content.splitlines()[start - 1 : end]
                        return CodeContext(
                            code="\n".join(lines),
                            language=language,
                            file=str(file),
                            lines=f"{start}-{end}",
                        )
            except Exception:
                # Fall through to whole-file context
                pass

        return CodeContext(code=content, language=language, file=str(file), lines="full file")

    def _stub_analysis(
        self,
        code: str,
        bad_output: Optional[str],
        good_output: Optional[str],
        correction: Optional[str],
    ) -> Dict[str, Any]:
        """Deterministic analysis used when AGENTSPEC_EXAMPLES_STUB=1."""
        guardrails = [
            "DO NOT infer semantic validation from key-existence checks",
            "ASK USER: Clarify whether the goal is content quality or existence",
            "ALWAYS separate structure vs semantics tests",
        ]
        return {
            "why_bad": (
                "Claims validation that does not occur (only checks key existence)"
                if bad_output
                else ""
            ),
            "good_what": good_output
            or "Checks presence of the 'what' key; does not assess quality.",
            "good_why": "Integration path sanity-check; not intended for semantic validation.",
            "good_guardrails": guardrails,
            "lesson": "Document actual checks; add ASK USER for ambiguous intent.",
            "pattern_type": "lie_about_validation" if bad_output else "good_pattern",
        }

    def analyze_documentation(
        self,
        code: str,
        bad_output: Optional[str],
        good_output: Optional[str],
        correction: Optional[str],
    ) -> Dict[str, Any]:
        """
        ---agentspec
        what: |
          Analyze documentation using an LLM middle layer (or deterministic stub). Produces a JSON-like dict containing why_bad, good_what, good_why, good_guardrails, lesson, and pattern_type. Accepts both bad_output and good_output so users can upload balanced datasets of good/bad examples.

        deps:
          calls:
            - generate_chat
            - json.loads
          imports:
            - json

        why: |
          Quality judgements and generalized lessons require semantic reasoning that static rules cannot provide reliably; the LLM performs classification and drafting under explicit instructions.

        guardrails:
          - DO NOT make network calls when AGENTSPEC_EXAMPLES_STUB=1; return stubbed result
          - ALWAYS include fields listed above; callers depend on consistent structure
        ---/agentspec
        """
        if os.getenv("AGENTSPEC_EXAMPLES_STUB") == "1":
            return self._stub_analysis(code, bad_output, good_output, correction)

        prompt = (
            "You are a documentation quality analyst for AgentSpec.\n"
            "Analyze the provided CODE and documentation samples. Return ONLY JSON with keys: \n"
            "why_bad, good_what, good_why, good_guardrails (array), lesson, pattern_type.\n"
            "pattern_type ∈ {lie_about_validation, line_by_line_bloat, extrapolate_intent, stub_not_flagged, missing_edge_cases, good_pattern}.\n\n"
            f"CODE:\n```\n{code}\n```\n\n"
            f"BAD_DOC:\n{bad_output or ''}\n\n"
            f"GOOD_DOC:\n{good_output or ''}\n\n"
            f"USER_CORRECTION:\n{correction or ''}\n"
        )

        # Use OpenAI-compatible path via generate_chat to maximize compatibility
        text = generate_chat(
            model=os.getenv("AGENTSPEC_OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {
                    "role": "system",
                    "content": "Return strict JSON. Be concise, honest, and include ASK USER when appropriate.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=800,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            provider=os.getenv("AGENTSPEC_PROVIDER", "openai"),
            reasoning_effort="minimal",
            verbosity="low",
        )

        try:
            return json.loads(text)
        except Exception as e:
            raise RuntimeError(f"LLM returned non-JSON output: {e}: {text[:200]}")

    def make_example(
        self,
        code_context: CodeContext,
        subject_function: Optional[str],
        bad_output: Optional[str],
        good_output: Optional[str],
        correction: Optional[str],
        require_ask_user: bool = False,
    ) -> Dict[str, Any]:
        analysis = self.analyze_documentation(code_context.code, bad_output, good_output, correction)

        guardrails = list(analysis.get("good_guardrails") or [])
        if require_ask_user and not any("ASK USER" in g for g in guardrails):
            guardrails.insert(0, "ASK USER: Clarify ambiguous intent before editing or refactoring")

        record: Dict[str, Any] = {
            "id": f"user_example_auto",
            "type": "negative_then_positive" if bad_output else "positive",
            "language": code_context.language,
            "code": code_context.code,
            "code_context": {
                "file": code_context.file,
                "function": None,  # filled by caller if known
                "subject_function": subject_function,
                "lines": code_context.lines,
            },
            "bad_documentation": None,
            "good_documentation": {
                "what": analysis["good_what"],
                "why": analysis["good_why"],
                "guardrails": guardrails,
            },
            "lesson": analysis["lesson"],
        }
        if bad_output:
            record["bad_documentation"] = {
                "text": bad_output,
                "why_bad": analysis.get("why_bad", ""),
                "pattern": analysis.get("pattern_type", ""),
            }
        return record

    def load_dataset(self) -> Dict[str, Any]:
        data = json.loads(EXAMPLES_FILE.read_text(encoding="utf-8"))
        return data

    def save_dataset(self, data: Dict[str, Any]) -> None:
        EXAMPLES_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @staticmethod
    def compute_ratio(data: Dict[str, Any]) -> Tuple[int, int, float]:
        good = 0
        bad = 0
        for ex in data.get("examples", []):
            if ex.get("good_documentation"):
                good += 1
            if ex.get("bad_documentation"):
                bad += 1
        total = max(1, good + bad)
        return good, bad, good / total


def _main_impl(
    file_path: str,
    function_name: Optional[str],
    subject_function: Optional[str],
    bad_output: Optional[str],
    good_output: Optional[str],
    correction: Optional[str],
    require_ask_user: bool,
    dry_run: bool,
    strict_ratio: bool,
):
    """
    ---agentspec
    what: |
      CLI entrypoint to add an anchored training example. Loads code context, runs LLM analysis, composes a record, validates the good/bad ratio policy, and optionally writes to the dataset file.

    deps:
      calls:
        - ExampleParser.extract_code_context
        - ExampleParser.analyze_documentation
        - ExampleParser.make_example
        - ExampleParser.load_dataset
        - ExampleParser.save_dataset
        - ExampleParser.compute_ratio
      imports:
        - click

    why: |
      A one-command path from observed bad (or good) documentation to a living dataset accelerates iteration and closes the feedback loop described in the handoff.

    guardrails:
      - DO NOT write by default; require explicit consent (no surprises)
      - DO NOT allow the dataset good ratio to silently degrade below minimum unless user opts out of strict enforcement
    ---/agentspec
    """
    parser = ExampleParser()
    ctx = parser.extract_code_context(file_path, function_name)
    record = parser.make_example(
        code_context=ctx,
        subject_function=subject_function,
        bad_output=bad_output,
        good_output=good_output,
        correction=correction,
        require_ask_user=require_ask_user,
    )

    # Fill back function name in context block
    record["code_context"]["function"] = function_name

    # Ratio policy (configurable)
    min_good_ratio = float(os.getenv("AGENTSPEC_EXAMPLE_GOOD_RATIO_MIN", "0.6"))
    data = parser.load_dataset()

    # Preview impact
    preview = {**data}
    preview_examples = list(preview.get("examples", []))
    preview_examples.append(record)
    preview["examples"] = preview_examples

    g, b, r = parser.compute_ratio(preview)

    print(f"Proposed record id={record['id']} type={record['type']} language={record['language']}")
    print(f"Ratio preview: good={g} bad={b} good_ratio={r:.2f} (min={min_good_ratio:.2f})")

    if strict_ratio and r < min_good_ratio:
        raise SystemExit(
            f"❌ Adding this example would reduce good_ratio to {r:.2f} below minimum {min_good_ratio:.2f}."
        )

    if dry_run:
        print(json.dumps(record, indent=2))
        return

    # Persist
    data["examples"].append(record)
    parser.save_dataset(data)
    print(f"✅ Appended to {EXAMPLES_FILE}")


# Expose a CLI only if click is available to avoid hard dependency during tests
if _CLICK_AVAILABLE:
    @click.command()
    @click.option("--file", "file_path", required=True, help="Path to file containing code to anchor the example")
    @click.option("--function", "function_name", required=False, help="Function name inside the file to scope the code context")
    @click.option("--subject-function", "subject_function", required=False, help="Fully qualified name of the function under discussion (e.g., module.func)")
    @click.option("--bad-output", "bad_output", required=False, help="Bad documentation text to analyze")
    @click.option("--good-output", "good_output", required=False, help="Good documentation text to analyze/validate")
    @click.option("--correction", "correction", required=False, help="What the bad documentation should say instead")
    @click.option("--require-ask-user", is_flag=True, help="Ensure an ASK USER guardrail is included in the good guardrails")
    @click.option("--dry-run", is_flag=True, help="Do not write to the dataset; just print the record and ratio")
    @click.option("--strict-ratio", is_flag=True, help="Fail if adding this example would violate the minimum good ratio")
    def main(
        file_path: str,
        function_name: Optional[str],
        subject_function: Optional[str],
        bad_output: Optional[str],
        good_output: Optional[str],
        correction: Optional[str],
        require_ask_user: bool,
        dry_run: bool,
        strict_ratio: bool,
    ):
        _main_impl(
            file_path,
            function_name,
            subject_function,
            bad_output,
            good_output,
            correction,
            require_ask_user,
            dry_run,
            strict_ratio,
        )
else:
    def main():  # pragma: no cover - CLI unavailable without click
        raise SystemExit(
            "The add_example CLI requires 'click'. Install with `pip install click` or use programmatic APIs."
        )


if __name__ == "__main__":
    main()
