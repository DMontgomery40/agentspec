#!/usr/bin/env python3
"""
Test that JavaScript adapter properly excludes vendor/minified files.
"""
from pathlib import Path
import tempfile
import shutil
from agentspec.langs import LanguageRegistry


def test_excludes_minified_files():
    """Verify that *.min.js files are excluded from discovery via .gitignore."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / ".gitignore"
        gitignore.write_text("*.min.js\n", encoding="utf-8")

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


def test_excludes_worktrees_directory():
    """Verify that .worktrees directory is excluded via .gitignore."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / ".gitignore"
        gitignore.write_text(".worktrees/\n", encoding="utf-8")

        # Create normal file in root
        normal = tmp / "index.js"
        normal.write_text("export default {}", encoding="utf-8")

        # Create .worktrees directory with files
        worktrees = tmp / ".worktrees" / "gh-pages" / "0abecd77"
        worktrees.mkdir(parents=True)
        vendor = worktrees / "vendor.js"
        vendor.write_text("// vendor code", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find root file, not .worktrees file
        assert len(files) == 1
        assert files[0].name == "index.js"


def test_excludes_gh_pages_directory():
    """Verify that gh-pages directory is excluded via .gitignore."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / ".gitignore"
        gitignore.write_text("gh-pages/\n*.min.js\n", encoding="utf-8")

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
        minified = pages / "bundle.min.js"
        minified.write_text("!function(){}", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find source file
        assert len(files) == 1
        assert files[0].name == "main.js"


def test_excludes_assets_directory():
    """Verify that assets directory is excluded via .gitignore."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / ".gitignore"
        gitignore.write_text("assets/\n*.min.js\n", encoding="utf-8")

        # Create source file
        src = tmp / "source.js"
        src.write_text("export const API = 'v1'", encoding="utf-8")

        # Create assets with vendor code
        assets = tmp / "assets" / "javascripts" / "lunr" / "min"
        assets.mkdir(parents=True)
        vendor = assets / "lunr.nl.min.js"
        vendor.write_text("!function(){}", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find source file
        assert len(files) == 1
        assert files[0].name == "source.js"


def test_excludes_node_modules():
    """Verify that node_modules is excluded via .gitignore."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / ".gitignore"
        gitignore.write_text("node_modules/\n", encoding="utf-8")

        # Create app file
        app = tmp / "app.js"
        app.write_text("import React from 'react'", encoding="utf-8")

        # Create node_modules
        modules = tmp / "node_modules" / "react"
        modules.mkdir(parents=True)
        vendor = modules / "index.js"
        vendor.write_text("// react", encoding="utf-8")

        # Discover files
        files = collect_source_files(tmp)

        # Should only find app file
        assert len(files) == 1
        assert files[0].name == "app.js"



def test_respects_gitignore_venv_pattern():
    """Verify that .gitignore patterns like .venv* exclude versioned virtualenvs."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=tmp, capture_output=True)

        # Create .gitignore with pattern
        gitignore = tmp / '.gitignore'
        gitignore.write_text('.venv*\nnode_modules/\n*.min.js\n', encoding='utf-8')

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

        # Should only find app.js, NOT venv files
        names = [f.name for f in files]
        assert 'app.js' in names
        assert 'urllib3_fetch.js' not in names
        assert 'jp.py' not in names
        assert len(files) == 1


def test_respects_gitignore_node_modules_pattern():
    """Verify that .gitignore node_modules/ pattern works."""
    import subprocess
    from agentspec.utils import collect_source_files

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@test.com'], cwd=tmp, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=tmp, capture_output=True)

        # Create .gitignore
        gitignore = tmp / '.gitignore'
        gitignore.write_text('node_modules/\n', encoding='utf-8')

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
