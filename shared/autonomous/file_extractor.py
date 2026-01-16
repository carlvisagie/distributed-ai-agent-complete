"""
Extract file paths from LLM understanding phase
"""
import re
from typing import List


def extract_files_from_understanding(understanding_text: str) -> List[str]:
    """
    Extract file paths mentioned in understanding phase
    
    Looks for patterns like:
    - "modify server/routers.ts"
    - "update client/src/App.tsx"
    - "files to modify: server/db.ts, server/routers.ts"
    """
    files = set()
    
    # Pattern 1: "modify/update/change FILE_PATH"
    pattern1 = r'(?:modify|update|change|edit)\s+([a-zA-Z0-9_\-./]+\.(?:ts|tsx|js|jsx|json|css))'
    matches = re.findall(pattern1, understanding_text, re.IGNORECASE)
    files.update(matches)
    
    # Pattern 2: File paths in lists
    pattern2 = r'([a-zA-Z0-9_\-/]+/[a-zA-Z0-9_\-./]+\.(?:ts|tsx|js|jsx|json|css))'
    matches = re.findall(pattern2, understanding_text)
    files.update(matches)
    
    # Pattern 3: "Files to modify:" section
    if 'files to modify' in understanding_text.lower():
        section_start = understanding_text.lower().index('files to modify')
        section = understanding_text[section_start:section_start + 500]
        pattern3 = r'([a-zA-Z0-9_\-/]+\.(?:ts|tsx|js|jsx|json|css))'
        matches = re.findall(pattern3, section)
        files.update(matches)
    
    # Filter out common false positives
    filtered_files = []
    for file_path in files:
        # Skip node_modules, dist, build
        if 'node_modules' in file_path or 'dist/' in file_path or 'build/' in file_path:
            continue
        # Skip very short paths (likely false positives)
        if len(file_path) < 5:
            continue
        filtered_files.append(file_path)
    
    return list(set(filtered_files))[:10]  # Max 10 files
