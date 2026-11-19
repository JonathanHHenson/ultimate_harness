#!/usr/bin/env python3
"""Check branch complexity in Python functions without executing source files."""

import argparse
import ast
from pathlib import Path
import sys
from typing import cast


FUNCTIONS = (ast.FunctionDef, ast.AsyncFunctionDef)
BRANCHES = (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While, ast.ExceptHandler)


def branch_cost(node: ast.AST) -> int:
    if isinstance(node, BRANCHES):
        return 1
    if isinstance(node, ast.BoolOp):
        return len(node.values) - 1
    if isinstance(node, ast.comprehension):
        return 1 + len(node.ifs)
    if isinstance(node, ast.Match):
        last = node.cases[-1]
        default = isinstance(last.pattern, ast.MatchAs) and last.pattern.pattern is None and last.guard is None
        return len(node.cases) - int(default)
    if isinstance(node, ast.match_case):
        return int(node.guard is not None)
    if isinstance(node, ast.MatchOr):
        return len(node.patterns) - 1
    return 0


class FunctionComplexity(ast.NodeVisitor):
    def __init__(self) -> None:
        self.score = 1

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, (*FUNCTIONS, ast.ClassDef)):
            # Nested functions and methods get their own scores.
            return
        self.score += branch_cost(node)
        super().generic_visit(node)


def python_sources(paths: list[Path]) -> list[Path]:
    sources: set[Path] = set()
    for path in paths:
        if path.is_dir() and not path.is_symlink():
            sources.update(path.rglob("*.py"))
        elif path.suffix == ".py":
            sources.add(path)
        else:
            raise ValueError(f"Expected a Python file or local directory: {str(path)!r}")
    if not sources:
        raise ValueError("No Python files found.")
    return sorted(sources)


def audit_tree(tree: ast.AST, path: Path, limit: int) -> tuple[int, list[str]]:
    findings: list[str] = []
    functions = [node for node in ast.walk(tree) if isinstance(node, FUNCTIONS)]
    for function in sorted(functions, key=lambda item: (item.lineno, item.col_offset)):
        visitor = FunctionComplexity()
        for statement in function.body:
            visitor.visit(statement)
        if visitor.score > limit:
            findings.append(f"{str(path)!r}:{function.lineno}: {function.name} has complexity {visitor.score} (limit {limit})")
    return len(functions), findings


def audit_file(path: Path, limit: int) -> tuple[int, list[str]]:
    if path.is_symlink() or not path.is_file():
        return 0, [f"{str(path)!r}: expected a regular Python file"]
    try:
        return audit_tree(ast.parse(path.read_bytes(), filename=str(path)), path, limit)
    except SyntaxError as error:
        return 0, [f"{str(path)!r}:{error.lineno or 1}: could not parse Python source"]
    except (OSError, ValueError, RecursionError):
        return 0, [f"{str(path)!r}: could not read or parse Python source"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    _ = parser.add_argument("paths", type=Path, nargs="+", help="Python files and directories to check")
    _ = parser.add_argument("--max-complexity", type=int, default=10, help="Maximum function complexity (default: 10)")
    arguments = parser.parse_args()
    limit = cast(int, arguments.max_complexity)
    if limit < 1:
        parser.error("--max-complexity must be positive")
    try:
        sources = python_sources(cast(list[Path], arguments.paths))
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    function_count = 0
    has_findings = False
    for path in sources:
        count, findings = audit_file(path, limit)
        function_count += count
        if findings:
            has_findings = True
            print("\n".join(findings), file=sys.stderr)
    if has_findings:
        return 1
    print(f"Checked {function_count} functions in {len(sources)} Python files (maximum complexity {limit}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
