#!/usr/bin/env python3
"""
Test that agentspec's built-in .agentspecignore works WITHOUT user having one.
"""
from pathlib import Path
import tempfile
import subprocess


def test_builtin_agentspecignore_excludes_venv311():
    """Verify built-in .agentspecignore excludes .venv311 WITHOUT user's .agentspecignore."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # DO NOT create .agentspecignore - testing built-in only
        # DO NOT create .gitignore - testing .agentspecignore only

        # Create source file
        src = tmp / 'app.js'
        src.write_text('export default {}', encoding='utf-8')

        # Create .venv311 virtualenv
        venv = tmp / '.venv311' / 'lib' / 'python3.11' / 'site-packages'
        venv.mkdir(parents=True)
        venv_file = venv / 'test.js'
        venv_file.write_text('// vendor', encoding='utf-8')

        # Discover files
        files = collect_source_files(tmp)

        # Should ONLY find app.js (built-in .agentspecignore excludes .venv311)
        names = [f.name for f in files]
        assert names == ['app.js'], f"Expected ['app.js'], got {names}"


def test_builtin_agentspecignore_excludes_node_modules():
    """Verify built-in .agentspecignore excludes node_modules."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # NO user files

        src = tmp / 'index.js'
        src.write_text('import React from "react"', encoding='utf-8')

        modules = tmp / 'node_modules' / 'react'
        modules.mkdir(parents=True)
        vendor = modules / 'index.js'
        vendor.write_text('// react', encoding='utf-8')

        files = collect_source_files(tmp)

        names = [f.name for f in files]
        assert names == ['index.js'], f"Expected ['index.js'], got {names}"


def test_builtin_agentspecignore_excludes_gh_pages():
    """Verify built-in .agentspecignore excludes gh-pages."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # NO user files

        src = tmp / 'main.js'
        src.write_text('console.log("main")', encoding='utf-8')

        pages = tmp / 'gh-pages' / 'assets'
        pages.mkdir(parents=True)
        build = pages / 'bundle.js'
        build.write_text('// built', encoding='utf-8')

        files = collect_source_files(tmp)

        names = [f.name for f in files]
        assert names == ['main.js'], f"Expected ['main.js'], got {names}"


def test_builtin_agentspecignore_excludes_minified():
    """Verify built-in .agentspecignore excludes *.min.js."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # NO user files

        normal = tmp / "app.js"
        normal.write_text("function test() {}", encoding="utf-8")

        minified = tmp / "app.min.js"
        minified.write_text("!function(){}", encoding="utf-8")

        files = collect_source_files(tmp)

        names = [f.name for f in files]
        assert names == ['app.js'], f"Expected ['app.js'], got {names}"
