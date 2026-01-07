"""
File selector for intelligent file targeting based on attack patterns
"""

from pathlib import Path
from typing import List, Optional
import random


class FileSelector:
    """Selects target files based on attack pattern and priorities"""
    
    def __init__(
        self,
        target_dir: str,
        extensions: List[str],
        recursive: bool = True,
        priority_extensions: Optional[List[str]] = None,
        max_files: Optional[int] = None,
        randomize: bool = False
    ):
        """
        Initialize file selector
        
        Args:
            target_dir: Directory to search for files
            extensions: List of file extensions to target (e.g., ['.txt', '.doc'])
            recursive: Whether to search subdirectories
            priority_extensions: High-priority extensions to target first
            max_files: Maximum number of files to select (None for all)
            randomize: Whether to randomize file order
        """
        self.target_dir = Path(target_dir)
        self.extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
        self.recursive = recursive
        self.priority_extensions = priority_extensions or []
        self.max_files = max_files
        self.randomize = randomize
        
        # Ensure priority extensions are in main extensions list
        for ext in self.priority_extensions:
            if ext not in self.extensions:
                self.extensions.append(ext)
    
    def find_targets(self) -> List[Path]:
        """
        Find all target files based on configuration
        
        Returns:
            List of file paths to target
        """
        priority_files = []
        secondary_files = []
        
        # Find priority files first
        if self.priority_extensions:
            for ext in self.priority_extensions:
                priority_files.extend(self._find_by_extension(ext))
        
        # Find secondary files
        for ext in self.extensions:
            if ext not in self.priority_extensions:
                secondary_files.extend(self._find_by_extension(ext))
        
        # Combine priority first, then secondary
        all_files = priority_files + secondary_files
        
        # Remove duplicates while preserving order
        seen = set()
        unique_files = []
        for f in all_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        
        # Randomize if requested
        if self.randomize:
            random.shuffle(unique_files)
        
        # Limit to max_files if specified
        if self.max_files:
            unique_files = unique_files[:self.max_files]
        
        return unique_files
    
    def _find_by_extension(self, extension: str) -> List[Path]:
        """
        Find files with specific extension
        
        Args:
            extension: File extension to search for
            
        Returns:
            List of matching file paths
        """
        pattern = f'*{extension}'
        
        if self.recursive:
            return list(self.target_dir.rglob(pattern))
        else:
            return list(self.target_dir.glob(pattern))
    
    def count_targets(self) -> int:
        """
        Count total number of target files without loading all paths
        
        Returns:
            Number of target files
        """
        return len(self.find_targets())
    
    def get_stats(self) -> dict:
        """
        Get statistics about target files
        
        Returns:
            Dictionary with file statistics
        """
        targets = self.find_targets()
        
        stats = {
            'total_files': len(targets),
            'by_extension': {},
            'total_size_bytes': 0
        }
        
        for file_path in targets:
            ext = file_path.suffix
            stats['by_extension'][ext] = stats['by_extension'].get(ext, 0) + 1
            
            try:
                stats['total_size_bytes'] += file_path.stat().st_size
            except:
                pass
        
        return stats
