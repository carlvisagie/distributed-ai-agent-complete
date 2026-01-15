"""
Code Protection System
Prevents destruction or unwanted modification of autonomous agent code by other agents
"""
import os
import json
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeProtection:
    """
    Protects critical autonomous agent code from modification
    
    Features:
    - File integrity checking (checksums)
    - Protected file registry
    - Automatic backup before changes
    - Change validation
    - Restoration capability
    - Modification logging
    """
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.protection_dir = self.project_root / ".protection"
        self.backup_dir = self.protection_dir / "backups"
        self.registry_file = self.protection_dir / "protected_files.json"
        self.checksums_file = self.protection_dir / "checksums.json"
        self.log_file = self.protection_dir / "modifications.log"
        
        # Create protection directories
        self.protection_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load protected files registry
        self.protected_files: Set[str] = self._load_registry()
        self.checksums: Dict[str, str] = self._load_checksums()
    
    def _load_registry(self) -> Set[str]:
        """Load protected files registry"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
                return set(data.get('protected_files', []))
        return set()
    
    def _save_registry(self):
        """Save protected files registry"""
        with open(self.registry_file, 'w') as f:
            json.dump({
                'protected_files': list(self.protected_files),
                'last_updated': datetime.utcnow().isoformat()
            }, f, indent=2)
    
    def _load_checksums(self) -> Dict[str, str]:
        """Load file checksums"""
        if self.checksums_file.exists():
            with open(self.checksums_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_checksums(self):
        """Save file checksums"""
        with open(self.checksums_file, 'w') as f:
            json.dump(self.checksums, f, indent=2)
    
    def _calculate_checksum(self, filepath: Path) -> str:
        """Calculate SHA256 checksum of file"""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _log_modification(self, filepath: str, action: str, details: str = ""):
        """Log modification attempt"""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {action}: {filepath}"
        if details:
            log_entry += f" - {details}"
        
        with open(self.log_file, 'a') as f:
            f.write(log_entry + "\n")
        
        logger.info(log_entry)
    
    def protect_file(self, filepath: str) -> bool:
        """
        Add file to protected registry
        
        Args:
            filepath: Relative path from project root
        
        Returns:
            True if successful
        """
        try:
            full_path = self.project_root / filepath
            
            if not full_path.exists():
                logger.error(f"File not found: {filepath}")
                return False
            
            # Add to registry
            self.protected_files.add(filepath)
            
            # Calculate and store checksum
            checksum = self._calculate_checksum(full_path)
            self.checksums[filepath] = checksum
            
            # Save
            self._save_registry()
            self._save_checksums()
            
            # Create initial backup
            self._create_backup(filepath)
            
            self._log_modification(filepath, "PROTECTED", f"Checksum: {checksum[:16]}...")
            
            logger.info(f"Protected: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to protect {filepath}: {e}")
            return False
    
    def protect_directory(self, directory: str, extensions: Optional[List[str]] = None) -> int:
        """
        Protect all files in directory
        
        Args:
            directory: Relative path from project root
            extensions: List of file extensions to protect (e.g., ['.py', '.md'])
        
        Returns:
            Number of files protected
        """
        dir_path = self.project_root / directory
        
        if not dir_path.exists():
            logger.error(f"Directory not found: {directory}")
            return 0
        
        count = 0
        for file_path in dir_path.rglob('*'):
            if file_path.is_file():
                # Check extension filter
                if extensions and file_path.suffix not in extensions:
                    continue
                
                # Get relative path
                rel_path = str(file_path.relative_to(self.project_root))
                
                if self.protect_file(rel_path):
                    count += 1
        
        logger.info(f"Protected {count} files in {directory}")
        return count
    
    def _create_backup(self, filepath: str) -> str:
        """
        Create backup of file
        
        Args:
            filepath: Relative path from project root
        
        Returns:
            Backup filepath
        """
        full_path = self.project_root / filepath
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        
        # Create backup path preserving directory structure
        backup_path = self.backup_dir / f"{filepath}.{timestamp}.bak"
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        shutil.copy2(full_path, backup_path)
        
        return str(backup_path)
    
    def check_integrity(self, filepath: Optional[str] = None) -> Dict[str, any]:
        """
        Check file integrity against stored checksums
        
        Args:
            filepath: Specific file to check (None = check all)
        
        Returns:
            Integrity report
        """
        files_to_check = [filepath] if filepath else self.protected_files
        
        report = {
            'checked': 0,
            'intact': 0,
            'modified': 0,
            'missing': 0,
            'details': []
        }
        
        for file in files_to_check:
            report['checked'] += 1
            full_path = self.project_root / file
            
            if not full_path.exists():
                report['missing'] += 1
                report['details'].append({
                    'file': file,
                    'status': 'missing'
                })
                self._log_modification(file, "MISSING", "File not found")
                continue
            
            # Calculate current checksum
            current_checksum = self._calculate_checksum(full_path)
            stored_checksum = self.checksums.get(file)
            
            if current_checksum == stored_checksum:
                report['intact'] += 1
                report['details'].append({
                    'file': file,
                    'status': 'intact'
                })
            else:
                report['modified'] += 1
                report['details'].append({
                    'file': file,
                    'status': 'modified',
                    'stored_checksum': stored_checksum[:16] if stored_checksum else None,
                    'current_checksum': current_checksum[:16]
                })
                self._log_modification(file, "MODIFIED", "Checksum mismatch")
        
        return report
    
    def validate_change(self, filepath: str, reason: str = "") -> bool:
        """
        Validate and approve a change to protected file
        
        Args:
            filepath: Relative path from project root
            reason: Reason for change
        
        Returns:
            True if change is approved
        """
        if filepath not in self.protected_files:
            return True  # Not protected, allow change
        
        # Create backup before change
        backup_path = self._create_backup(filepath)
        self._log_modification(filepath, "CHANGE_APPROVED", f"Reason: {reason}, Backup: {backup_path}")
        
        # Update checksum after change
        full_path = self.project_root / filepath
        if full_path.exists():
            new_checksum = self._calculate_checksum(full_path)
            self.checksums[filepath] = new_checksum
            self._save_checksums()
        
        return True
    
    def restore_file(self, filepath: str, backup_timestamp: Optional[str] = None) -> bool:
        """
        Restore file from backup
        
        Args:
            filepath: Relative path from project root
            backup_timestamp: Specific backup timestamp (None = latest)
        
        Returns:
            True if successful
        """
        try:
            # Find backup
            backup_pattern = f"{filepath}.*.bak"
            backups = list(self.backup_dir.glob(backup_pattern))
            
            if not backups:
                logger.error(f"No backups found for {filepath}")
                return False
            
            # Get latest or specific backup
            if backup_timestamp:
                backup_file = self.backup_dir / f"{filepath}.{backup_timestamp}.bak"
                if not backup_file.exists():
                    logger.error(f"Backup not found: {backup_timestamp}")
                    return False
            else:
                backup_file = max(backups, key=lambda p: p.stat().st_mtime)
            
            # Restore
            full_path = self.project_root / filepath
            shutil.copy2(backup_file, full_path)
            
            # Update checksum
            new_checksum = self._calculate_checksum(full_path)
            self.checksums[filepath] = new_checksum
            self._save_checksums()
            
            self._log_modification(filepath, "RESTORED", f"From: {backup_file.name}")
            
            logger.info(f"Restored: {filepath} from {backup_file.name}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to restore {filepath}: {e}")
            return False
    
    def get_protection_status(self) -> Dict[str, any]:
        """Get overall protection status"""
        integrity = self.check_integrity()
        
        return {
            'total_protected': len(self.protected_files),
            'integrity_check': integrity,
            'backup_directory': str(self.backup_dir),
            'protection_active': True
        }
    
    def list_protected_files(self) -> List[str]:
        """Get list of all protected files"""
        return sorted(list(self.protected_files))
    
    def list_backups(self, filepath: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available backups
        
        Args:
            filepath: Specific file (None = all backups)
        
        Returns:
            List of backup info
        """
        pattern = f"{filepath}.*.bak" if filepath else "*.bak"
        backups = []
        
        for backup_file in self.backup_dir.rglob(pattern):
            stat = backup_file.stat()
            backups.append({
                'file': backup_file.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'path': str(backup_file)
            })
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)


# Global protection instance
_protection_instance: Optional[CodeProtection] = None


def get_protection(project_root: str = "/home/ubuntu/distributed-ai-agent-complete") -> CodeProtection:
    """Get or create global protection instance"""
    global _protection_instance
    if _protection_instance is None:
        _protection_instance = CodeProtection(project_root)
    return _protection_instance


# Example usage
if __name__ == "__main__":
    # Initialize protection
    protection = CodeProtection("/home/ubuntu/distributed-ai-agent-complete")
    
    # Protect critical files
    print("Protecting autonomous agent code...")
    
    # Protect core modules
    protection.protect_directory("shared/autonomous", extensions=['.py'])
    protection.protect_directory("shared/security", extensions=['.py'])
    protection.protect_directory("shared/protection", extensions=['.py'])
    
    # Protect documentation
    protection.protect_file("README.md")
    protection.protect_file("CONTINUITY_SYSTEM_README.md")
    protection.protect_file("SYSTEM_SUMMARY.md")
    
    # Check integrity
    print("\nChecking integrity...")
    status = protection.get_protection_status()
    print(f"Protected files: {status['total_protected']}")
    print(f"Intact: {status['integrity_check']['intact']}")
    print(f"Modified: {status['integrity_check']['modified']}")
    print(f"Missing: {status['integrity_check']['missing']}")
    
    print("\nProtection system active!")
