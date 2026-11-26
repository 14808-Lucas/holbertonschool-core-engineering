#!/usr/bin/env python3
"""Deterministic tool that checks a study guide has every section.

It does not judge the quality of the content, only its structure:
each required section must appear as a Markdown heading.
"""
REQUIRED_SECTIONS = [
    "Topic",
    "Simple Explanation",
    "Key Concepts",
    "Example",
    "Practice Exercise",
    "Common Mistakes",
    "Review Comments",
    "Final Summary",
]


def _normalize_heading(line: str) -> str:
    """Turn a heading line like '## Key Concepts:' into 'key concepts'."""
    return line.lstrip("#").strip().rstrip(":").strip().lower()


def get_headings(markdown: str) -> list:
    """Return the normalized Markdown headings, skipping code blocks."""
    headings = []
    in_code_block = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if not in_code_block and stripped.startswith("#"):
            headings.append(_normalize_heading(stripped))
    return headings


def fix_section_headings(markdown: str) -> str:
    """Rewrite required section headings at the expected level.

    "Topic" becomes "# Topic" and every other required section becomes
    "## <Section>", so "### key concepts:" turns into "## Key Concepts".
    Other headings and code blocks are left unchanged.
    """
    levels = {}
    for section in REQUIRED_SECTIONS:
        prefix = "#" if section == "Topic" else "##"
        levels[section.lower()] = "{} {}".format(prefix, section)

    fixed_lines = []
    in_code_block = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
        elif not in_code_block and stripped.startswith("#"):
            key = _normalize_heading(stripped)
            if key in levels:
                line = levels[key]
        fixed_lines.append(line)
    return "\n".join(fixed_lines)


def validate_required_sections(markdown: str) -> dict:
    """Check that Markdown content contains every required section.

    Args:
        markdown: The generated study guide in Markdown.

    Returns:
        A dict with "valid" (True if no section is missing) and
        "missing_sections" (the names of the missing sections, in order).
    """
    if not isinstance(markdown, str):
        markdown = ""

    headings = get_headings(markdown)
    missing = []
    for section in REQUIRED_SECTIONS:
        if section.lower() not in headings:
            missing.append(section)

    return {"valid": len(missing) == 0, "missing_sections": missing}
