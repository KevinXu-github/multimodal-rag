"""Script to add logging to all Python files and replace print statements."""

import re
from pathlib import Path


def add_logging_to_file(file_path: Path) -> tuple[bool, int]:
    """
    Add logging import and replace print statements in a file.

    Returns:
        (modified, num_replacements)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements = 0

    # Check if file already has logger
    if 'logger = logging.getLogger(__name__)' in content:
        print(f"[SKIP] {file_path.name} (already has logger)")
        return False, 0

    # Check if file has print statements
    print_matches = list(re.finditer(r'print\s*\([^)]+\)', content))
    if not print_matches:
        return False, 0

    # Add logging import after other imports
    if 'import logging' not in content:
        # Find last import statement
        import_pattern = r'((?:from|import)\s+[^\n]+\n)+'
        import_matches = list(re.finditer(import_pattern, content))

        if import_matches:
            last_import = import_matches[-1]
            insert_pos = last_import.end()

            # Insert logging import
            content = (
                content[:insert_pos] +
                '\nimport logging\n' +
                content[insert_pos:]
            )

    # Add logger instance after docstring or imports
    if '"""' in content[:500]:  # Has docstring
        # After docstring and imports
        docstring_end = content.find('"""', 3) + 3
        next_section = content.find('\n\n', docstring_end)
        if next_section > 0:
            # Check if imports follow
            imports_section = content[docstring_end:next_section]
            if 'import' in imports_section:
                # After imports
                insert_pos = next_section + 2
            else:
                # After docstring
                insert_pos = docstring_end + 1

            content = (
                content[:insert_pos] +
                '\nlogger = logging.getLogger(__name__)\n' +
                content[insert_pos:]
            )

    # Replace print statements with logger.info
    def replace_print(match):
        nonlocal replacements
        print_content = match.group(0)

        # Extract the message from print()
        msg_match = re.search(r'print\s*\((.+)\)', print_content, re.DOTALL)
        if msg_match:
            msg = msg_match.group(1).strip()

            # Determine log level based on content
            msg_lower = msg.lower()
            if 'error' in msg_lower or 'failed' in msg_lower:
                replacements += 1
                if 'exc_info' not in msg:
                    return f'logger.error({msg}, exc_info=True)'
                return f'logger.error({msg})'
            elif 'warning' in msg_lower or 'warn' in msg_lower:
                replacements += 1
                return f'logger.warning({msg})'
            else:
                replacements += 1
                return f'logger.info({msg})'

        return print_content

    content = re.sub(r'print\s*\([^)]+\)', replace_print, content)

    # Only write if changes were made
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True, replacements

    return False, 0


def main():
    """Add logging to all source files."""
    src_dir = Path(__file__).parent.parent / 'src'

    print("=" * 60)
    print("Adding Logging to Source Files")
    print("=" * 60)

    total_files = 0
    total_replacements = 0

    for py_file in src_dir.rglob('*.py'):
        if '__pycache__' in str(py_file):
            continue

        modified, replacements = add_logging_to_file(py_file)
        if modified:
            total_files += 1
            total_replacements += replacements
            print(f"[OK] {py_file.relative_to(src_dir)}: {replacements} replacements")

    print("=" * 60)
    print(f"Modified {total_files} files")
    print(f"Replaced {total_replacements} print statements")
    print("=" * 60)


if __name__ == "__main__":
    main()
