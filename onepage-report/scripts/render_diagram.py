#!/usr/bin/env python3
"""
Mermaid diagram to PNG converter.
Usage: python render_diagram.py <input.md> <output.png>
"""

import subprocess
import sys
import tempfile
import re
import platform
from pathlib import Path


def extract_mermaid(md_content: str) -> str:
    """Extract mermaid code block from markdown."""
    pattern = r'```mermaid\s*([\s\S]*?)\s*```'
    match = re.search(pattern, md_content)
    if not match:
        raise ValueError("No mermaid code block found in markdown")
    return match.group(1).strip()


def render_mermaid_to_png(mermaid_code: str, output_path: str) -> None:
    """Render mermaid code to PNG using mmdc CLI."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False, encoding='utf-8') as f:
        f.write(mermaid_code)
        temp_mmd = f.name

    try:
        # Windows 需要 shell=True 來找到 npm 全局安裝的命令
        use_shell = platform.system() == 'Windows'
        result = subprocess.run(
            ['mmdc', '-i', temp_mmd, '-o', output_path, '-b', 'white'],
            capture_output=True,
            text=True,
            shell=use_shell
        )
        if result.returncode != 0:
            raise RuntimeError(f"mmdc failed: {result.stderr}")
    finally:
        Path(temp_mmd).unlink(missing_ok=True)


def main():
    if len(sys.argv) != 3:
        print("Usage: python render_diagram.py <input.md> <output.png>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    md_content = Path(input_path).read_text(encoding='utf-8')
    mermaid_code = extract_mermaid(md_content)
    render_mermaid_to_png(mermaid_code, output_path)
    print(f"Diagram saved to {output_path}")


if __name__ == '__main__':
    main()
