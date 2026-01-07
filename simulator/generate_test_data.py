"""
Quick test data generator script
Creates realistic test files for ransomware simulation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulator.core.test_data_generator import TestDataGenerator


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test data for ransomware simulation")
    parser.add_argument("target", help="Target directory to create test files in")
    parser.add_argument("--text", type=int, default=50, help="Number of .txt files (default: 50)")
    parser.add_argument("--docs", type=int, default=30, help="Number of .doc files (default: 30)")
    parser.add_argument("--pdfs", type=int, default=20, help="Number of .pdf files (default: 20)")
    parser.add_argument("--images", type=int, default=20, help="Number of .jpg files (default: 20)")
    parser.add_argument("--spreadsheets", type=int, default=15, help="Number of .xlsx files (default: 15)")
    parser.add_argument("--databases", type=int, default=5, help="Number of .sql/.bak files (default: 5)")
    parser.add_argument("--clean", action="store_true", help="Clean existing files before generating")
    
    args = parser.parse_args()
    
    # Create generator
    generator = TestDataGenerator(args.target)
    
    # Clean if requested
    if args.clean:
        print(f"Cleaning {args.target}...")
        generator.clean()
    
    # Generate files
    stats = generator.generate_all(
        text=args.text,
        docs=args.docs,
        pdfs=args.pdfs,
        images=args.images,
        spreadsheets=args.spreadsheets,
        databases=args.databases
    )
    
    print("\n" + "=" * 60)
    print("Test Data Generation Complete!")
    print("=" * 60)
    for file_type, count in stats.items():
        print(f"{file_type}: {count} files")
    print("=" * 60)


if __name__ == "__main__":
    main()
