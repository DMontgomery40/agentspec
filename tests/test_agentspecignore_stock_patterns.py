#!/usr/bin/env python3
"""
Test that .agentspecignore stock patterns work WITHOUT .gitignore.
"""
from pathlib import Path
import tempfile
import shutil
import subprocess


def test_agentspecignore_excludes_venv311_without_gitignore():
    """Verify .agentspecignore patterns work even without .gitignore."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo (so repo_root is found)
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Copy agentspec's .agentspecignore to the test repo
        agentspec_root = Path(__file__).parent.parent
        src_ignore = agentspec_root / '.agentspecignore'
        dst_ignore = tmp / '.agentspecignore'
        shutil.copy(src_ignore, dst_ignore)

        # DO NOT create .gitignore - we're testing .agentspecignore alone

        # Create normal source file
        src = tmp / 'app.js'
        src.write_text('export default {}', encoding='utf-8')

        # Create .venv311 virtualenv with files
        venv = tmp / '.venv311' / 'lib' / 'python3.11' / 'site-packages'
        venv.mkdir(parents=True)
        venv_file = venv / 'urllib3_fetch.js'
        venv_file.write_text('// vendor', encoding='utf-8')

        # Also create a Python file in the venv
        venv_py = tmp / '.venv311' / 'bin' / 'jp.py'
        venv_py.parent.mkdir(parents=True, exist_ok=True)
        venv_py.write_text('#!/usr/bin/env python3\nprint("hello")', encoding='utf-8')

        # Discover files
        files = collect_source_files(tmp)

        # Should only find app.js, NOT venv files (via .agentspecignore)
        names = [f.name for f in files]
        assert 'app.js' in names
        assert 'urllib3_fetch.js' not in names
        assert 'jp.py' not in names
        assert len(files) == 1


def test_agentspecignore_excludes_node_modules_without_gitignore():
    """Verify .agentspecignore node_modules/ pattern works without .gitignore."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Copy .agentspecignore
        agentspec_root = Path(__file__).parent.parent
        src_ignore = agentspec_root / '.agentspecignore'
        dst_ignore = tmp / '.agentspecignore'
        shutil.copy(src_ignore, dst_ignore)

        # NO .gitignore

        # Create source file
        src = tmp / 'index.js'
        src.write_text('import React from "react"', encoding='utf-8')

        # Create node_modules
        modules = tmp / 'node_modules' / 'react'
        modules.mkdir(parents=True)
        vendor = modules / 'index.js'
        vendor.write_text('// react', encoding='utf-8')

        # Discover files
        files = collect_source_files(tmp)

        # Should only find source, not node_modules
        names = [f.name for f in files]
        assert names == ['index.js']


def test_agentspecignore_excludes_minified_without_gitignore():
    """Verify .agentspecignore *.min.js pattern works without .gitignore."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Copy .agentspecignore
        agentspec_root = Path(__file__).parent.parent
        src_ignore = agentspec_root / '.agentspecignore'
        dst_ignore = tmp / '.agentspecignore'
        shutil.copy(src_ignore, dst_ignore)

        # NO .gitignore

        # Create normal JS file
        normal = tmp / "app.js"
        normal.write_text("function test() {}", encoding="utf-8")

        # Create minified file
        minified = tmp / "app.min.js"
        minified.write_text("!function(){}", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find normal file, not minified
        assert len(files) == 1
        assert files[0].name == "app.js"


def test_agentspecignore_excludes_gh_pages_without_gitignore():
    """Verify .agentspecignore gh-pages/ pattern works without .gitignore."""
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Copy .agentspecignore
        agentspec_root = Path(__file__).parent.parent
        src_ignore = agentspec_root / '.agentspecignore'
        dst_ignore = tmp / '.agentspecignore'
        shutil.copy(src_ignore, dst_ignore)

        # NO .gitignore

        # Create normal file
        src = tmp / "src"
        src.mkdir()
        normal = src / "main.js"
        normal.write_text("console.log('main')", encoding="utf-8")

        # Create gh-pages build dir
        pages = tmp / "gh-pages" / "assets" / "javascripts"
        pages.mkdir(parents=True)
        build = pages / "bundle.js"
        build.write_text("// built", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find source file
        assert len(files) == 1
        assert files[0].name == "main.js"
