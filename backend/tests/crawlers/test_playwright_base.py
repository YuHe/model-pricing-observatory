from __future__ import annotations
import importlib


def test_playwright_base_module_exists():
    """Verify playwright_base module file exists and is valid Python."""
    import ast
    from pathlib import Path
    module_path = Path(__file__).resolve().parents[2] / "app" / "crawlers" / "playwright_base.py"
    assert module_path.exists()
    source = module_path.read_text()
    tree = ast.parse(source)
    func_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)]
    assert "crawl_with_playwright" in func_names
