"""
Test data generator for creating realistic test files
"""

from pathlib import Path
import random
import string
import os


class TestDataGenerator:
    """Generates realistic test files for ransomware simulation"""
    
    def __init__(self, output_dir: str):
        """
        Initialize test data generator
        
        Args:
            output_dir: Directory to create test files in
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_text_files(self, count: int = 50, size_kb: int = 1) -> int:
        """
        Generate text documents
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            content = self._generate_text_content(size_kb * 1024)
            file_path = self.output_dir / f"document_{i:03d}.txt"
            
            try:
                file_path.write_text(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {file_path}: {e}")
        
        return created
    
    def generate_doc_files(self, count: int = 30, size_kb: int = 2) -> int:
        """
        Generate .doc files (simulated Word documents)
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            content = f"Report {i}\n\n" + self._generate_text_content(size_kb * 1024)
            file_path = self.output_dir / f"report_{i:03d}.doc"
            
            try:
                file_path.write_text(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {file_path}: {e}")
        
        return created
    
    def generate_pdf_files(self, count: int = 20, size_kb: int = 5) -> int:
        """
        Generate .pdf files (simulated PDFs with random content)
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            # Simulate PDF with mixed text and binary
            content = f"PDF Document {i}\n" + self._generate_text_content(size_kb * 1024)
            file_path = self.output_dir / f"invoice_{i:03d}.pdf"
            
            try:
                file_path.write_text(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {file_path}: {e}")
        
        return created
    
    def generate_image_files(self, count: int = 20, size_kb: int = 50) -> int:
        """
        Generate image files (random binary data simulating images)
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            # Random bytes simulating image data
            content = os.urandom(size_kb * 1024)
            file_path = self.output_dir / f"photo_{i:03d}.jpg"
            
            try:
                file_path.write_bytes(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {file_path}: {e}")
        
        return created
    
    def generate_spreadsheet_files(self, count: int = 15, size_kb: int = 3) -> int:
        """
        Generate .xlsx files (simulated Excel spreadsheets)
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            # Simulate spreadsheet with CSV-like data
            rows = []
            for row in range(50):
                rows.append(f"{row},{random.randint(1, 1000)},{random.choice(['A', 'B', 'C'])}")
            content = "\n".join(rows)
            
            file_path = self.output_dir / f"data_{i:03d}.xlsx"
            
            try:
                file_path.write_text(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {file_path}: {e}")
        
        return created
    
    def generate_database_files(self, count: int = 5, size_kb: int = 100) -> int:
        """
        Generate .sql and .bak files (simulated database files)
        
        Args:
            count: Number of files to create
            size_kb: Approximate size of each file in KB
            
        Returns:
            Number of files created
        """
        created = 0
        for i in range(count):
            content = f"-- Database backup {i}\n" + self._generate_text_content(size_kb * 1024)
            
            # Create .sql file
            sql_path = self.output_dir / f"backup_{i:03d}.sql"
            try:
                sql_path.write_text(content)
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {sql_path}: {e}")
            
            # Create .bak file
            bak_path = self.output_dir / f"backup_{i:03d}.bak"
            try:
                bak_path.write_bytes(os.urandom(size_kb * 1024))
                created += 1
            except Exception as e:
                print(f"[ERROR] Failed to create {bak_path}: {e}")
        
        return created
    
    def generate_all(
        self,
        text=50,
        docs=30,
        pdfs=20,
        images=20,
        spreadsheets=15,
        databases=5
    ) -> dict:
        """
        Generate all file types
        
        Args:
            text: Number of .txt files
            docs: Number of .doc files
            pdfs: Number of .pdf files
            images: Number of .jpg files
            spreadsheets: Number of .xlsx files
            databases: Number of .sql/.bak files
            
        Returns:
            Dictionary with creation statistics
        """
        print(f"[GENERATOR] Creating test files in {self.output_dir}")
        
        stats = {
            'text_files': self.generate_text_files(text),
            'doc_files': self.generate_doc_files(docs),
            'pdf_files': self.generate_pdf_files(pdfs),
            'image_files': self.generate_image_files(images),
            'spreadsheet_files': self.generate_spreadsheet_files(spreadsheets),
            'database_files': self.generate_database_files(databases)
        }
        
        total = sum(stats.values())
        print(f"[GENERATOR] Created {total} files successfully")
        
        return stats
    
    def _generate_text_content(self, size_bytes: int) -> str:
        """
        Generate random text content
        
        Args:
            size_bytes: Approximate size in bytes
            
        Returns:
            Random text string
        """
        # Generate random words
        words = []
        current_size = 0
        
        while current_size < size_bytes:
            word_length = random.randint(3, 12)
            word = ''.join(random.choices(string.ascii_lowercase, k=word_length))
            words.append(word)
            current_size += word_length + 1  # +1 for space
        
        return ' '.join(words)
    
    def clean(self):
        """Remove all generated files"""
        if self.output_dir.exists():
            for file in self.output_dir.iterdir():
                if file.is_file():
                    file.unlink()
            print(f"[GENERATOR] Cleaned {self.output_dir}")
