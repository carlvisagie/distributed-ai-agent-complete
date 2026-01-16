"""
Smart File Editor - Targeted Edit Operations

Supports:
- insert_after: Add code after a marker
- insert_before: Add code before a marker
- replace: Replace specific code section
- append: Add to end of file
- prepend: Add to start of file
- create: Create new file
"""
import re
from pathlib import Path
from typing import Dict, Any, Optional


class SmartEditor:
    """Handles targeted file edits without full rewrites"""
    
    @staticmethod
    def apply_edit(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply a single edit operation
        
        Args:
            file_path: Path to file
            edit: {
                "operation": "insert_after" | "replace" | "create" | ...,
                "marker": "line to find" (for insert_after/before),
                "find": "code to find" (for replace),
                "content": "new code"
            }
        
        Returns:
            {"success": bool, "message": str}
        """
        operation = edit.get("operation")
        
        try:
            if operation == "create":
                return SmartEditor._create_file(file_path, edit)
            elif operation == "insert_after":
                return SmartEditor._insert_after(file_path, edit)
            elif operation == "insert_before":
                return SmartEditor._insert_before(file_path, edit)
            elif operation == "replace":
                return SmartEditor._replace(file_path, edit)
            elif operation == "append":
                return SmartEditor._append(file_path, edit)
            elif operation == "prepend":
                return SmartEditor._prepend(file_path, edit)
            else:
                return {
                    "success": False,
                    "message": f"Unknown operation: {operation}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Edit failed: {str(e)}"
            }
    
    @staticmethod
    def _create_file(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.write(edit["content"])
        
        return {
            "success": True,
            "message": f"Created {file_path}"
        }
    
    @staticmethod
    def _insert_after(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Insert content after a marker line"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        marker = edit["marker"]
        content = edit["content"]
        
        # Ensure content ends with newline
        if not content.endswith('\n'):
            content += '\n'
        
        # Find marker
        inserted = False
        for i, line in enumerate(lines):
            if marker in line:
                # Insert after this line
                lines.insert(i + 1, content)
                inserted = True
                break
        
        if not inserted:
            return {
                "success": False,
                "message": f"Marker not found: {marker}"
            }
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        return {
            "success": True,
            "message": f"Inserted after '{marker}'"
        }
    
    @staticmethod
    def _insert_before(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Insert content before a marker line"""
        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        marker = edit["marker"]
        content = edit["content"]
        
        if not content.endswith('\n'):
            content += '\n'
        
        inserted = False
        for i, line in enumerate(lines):
            if marker in line:
                lines.insert(i, content)
                inserted = True
                break
        
        if not inserted:
            return {
                "success": False,
                "message": f"Marker not found: {marker}"
            }
        
        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        return {
            "success": True,
            "message": f"Inserted before '{marker}'"
        }
    
    @staticmethod
    def _replace(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Replace a specific code section"""
        with open(file_path, 'r') as f:
            content = f.read()
        
        find = edit["find"]
        replace = edit["content"]
        
        if find not in content:
            return {
                "success": False,
                "message": f"Code to replace not found: {find[:50]}..."
            }
        
        # Replace first occurrence
        new_content = content.replace(find, replace, 1)
        
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        return {
            "success": True,
            "message": f"Replaced code section"
        }
    
    @staticmethod
    def _append(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Append content to end of file"""
        content = edit["content"]
        
        if not content.startswith('\n'):
            content = '\n' + content
        
        with open(file_path, 'a') as f:
            f.write(content)
        
        return {
            "success": True,
            "message": "Appended to end of file"
        }
    
    @staticmethod
    def _prepend(file_path: Path, edit: Dict[str, Any]) -> Dict[str, Any]:
        """Prepend content to start of file"""
        with open(file_path, 'r') as f:
            existing = f.read()
        
        content = edit["content"]
        
        if not content.endswith('\n'):
            content += '\n'
        
        with open(file_path, 'w') as f:
            f.write(content + existing)
        
        return {
            "success": True,
            "message": "Prepended to start of file"
        }
    
    @staticmethod
    def backup_file(file_path: Path) -> Optional[str]:
        """Create backup of file, return backup content"""
        if file_path.exists():
            with open(file_path, 'r') as f:
                return f.read()
        return None
    
    @staticmethod
    def restore_backup(file_path: Path, backup_content: Optional[str]):
        """Restore file from backup"""
        if backup_content is not None:
            with open(file_path, 'w') as f:
                f.write(backup_content)
        elif file_path.exists():
            file_path.unlink()
