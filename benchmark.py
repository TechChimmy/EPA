#!/usr/bin/env python3
"""
EPA Performance Benchmarking Script
Measures detection latency, CPU/memory usage, and system performance
"""

import time
import psutil
import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from simulator.generate_test_data import generate_test_files
from entropy.entropy import shannon_entropy
from detection.cusum import CUSUM
from detection.zscore import is_anomaly


class EPABenchmark:
    """Benchmark EPA system performance"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": self._get_system_info(),
            "benchmarks": {}
        }
    
    def _get_system_info(self):
        """Get system information"""
        return {
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "python_version": sys.version.split()[0],
            "platform": sys.platform
        }
    
    def benchmark_entropy_calculation(self, iterations=1000):
        """Benchmark Shannon entropy calculation speed"""
        print("\n" + "="*60)
        print("BENCHMARK 1: Entropy Calculation Speed")
        print("="*60)
        
        # Generate test data of different sizes
        sizes = [1024, 4096, 8192, 16384]  # bytes
        results = {}
        
        for size in sizes:
            data = os.urandom(size)
            
            start_time = time.time()
            for _ in range(iterations):
                shannon_entropy(data)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = (total_time / iterations) * 1000  # ms
            
            results[f"{size}_bytes"] = {
                "avg_time_ms": round(avg_time, 4),
                "throughput_ops_per_sec": round(iterations / total_time, 2)
            }
            
            print(f"  {size:>6} bytes: {avg_time:.4f} ms/operation ({iterations/total_time:.2f} ops/sec)")
        
        self.results["benchmarks"]["entropy_calculation"] = results
        return results
    
    def benchmark_detection_algorithms(self, iterations=10000):
        """Benchmark CUSUM and Z-score detection speed"""
        print("\n" + "="*60)
        print("BENCHMARK 2: Detection Algorithm Speed")
        print("="*60)
        
        results = {}
        
        # Benchmark CUSUM
        cusum = CUSUM(drift=0.1, threshold=1.5)
        start_time = time.time()
        for i in range(iterations):
            cusum.update(0.2)
        end_time = time.time()
        
        cusum_time = (end_time - start_time) / iterations * 1000000  # microseconds
        results["cusum"] = {
            "avg_time_us": round(cusum_time, 2),
            "throughput_ops_per_sec": round(iterations / (end_time - start_time), 2)
        }
        print(f"  CUSUM: {cusum_time:.2f} μs/operation ({iterations/(end_time-start_time):.2f} ops/sec)")
        
        # Benchmark Z-score
        start_time = time.time()
        for i in range(iterations):
            is_anomaly(5.5, 4.0, 0.5, 3.0)
        end_time = time.time()
        
        zscore_time = (end_time - start_time) / iterations * 1000000  # microseconds
        results["zscore"] = {
            "avg_time_us": round(zscore_time, 2),
            "throughput_ops_per_sec": round(iterations / (end_time - start_time), 2)
        }
        print(f"  Z-score: {zscore_time:.2f} μs/operation ({iterations/(end_time-start_time):.2f} ops/sec)")
        
        self.results["benchmarks"]["detection_algorithms"] = results
        return results
    
    def benchmark_file_processing(self, file_counts=[100, 500, 1000]):
        """Benchmark file processing at different scales"""
        print("\n" + "="*60)
        print("BENCHMARK 3: File Processing Performance")
        print("="*60)
        
        results = {}
        
        for count in file_counts:
            # Create temporary test directory
            test_dir = Path(f"benchmark_test_{count}")
            test_dir.mkdir(exist_ok=True)
            
            print(f"\n  Testing with {count} files...")
            
            # Generate test files
            print(f"    Generating {count} test files...")
            start_gen = time.time()
            generate_test_files(str(test_dir), text_count=count, doc_count=0, image_count=0)
            gen_time = time.time() - start_gen
            
            # Measure entropy calculation for all files
            print(f"    Calculating entropy for {count} files...")
            start_calc = time.time()
            
            for file_path in test_dir.glob("*.txt"):
                try:
                    with open(file_path, 'rb') as f:
                        data = f.read(4096)  # Sample 4KB
                    shannon_entropy(data)
                except Exception:
                    pass
            
            calc_time = time.time() - start_calc
            
            # Calculate metrics
            files_per_sec = count / calc_time if calc_time > 0 else 0
            
            results[f"{count}_files"] = {
                "generation_time_sec": round(gen_time, 2),
                "processing_time_sec": round(calc_time, 2),
                "throughput_files_per_sec": round(files_per_sec, 2),
                "avg_time_per_file_ms": round((calc_time / count) * 1000, 2)
            }
            
            print(f"    ✓ Processed {count} files in {calc_time:.2f}s ({files_per_sec:.2f} files/sec)")
            
            # Cleanup
            import shutil
            shutil.rmtree(test_dir)
        
        self.results["benchmarks"]["file_processing"] = results
        return results
    
    def benchmark_memory_usage(self):
        """Benchmark memory usage during operation"""
        print("\n" + "="*60)
        print("BENCHMARK 4: Memory Usage")
        print("="*60)
        
        process = psutil.Process(os.getpid())
        
        # Baseline memory
        baseline_mb = process.memory_info().rss / (1024 * 1024)
        print(f"  Baseline memory: {baseline_mb:.2f} MB")
        
        # Simulate monitoring 1000 files
        from entropy.rolling import RollingEntropy
        from detection.cusum import CUSUM
        
        stores = {}
        for i in range(1000):
            stores[f"file_{i}"] = {
                "rolling": RollingEntropy(),
                "cusum": CUSUM()
            }
            
            # Add some data
            for j in range(10):
                stores[f"file_{i}"]["rolling"].add(4.0 + j * 0.1)
                stores[f"file_{i}"]["cusum"].update(0.1)
        
        # Measure memory after simulation
        loaded_mb = process.memory_info().rss / (1024 * 1024)
        memory_increase = loaded_mb - baseline_mb
        
        print(f"  Memory with 1000 files tracked: {loaded_mb:.2f} MB")
        print(f"  Memory increase: {memory_increase:.2f} MB")
        print(f"  Memory per file: {(memory_increase / 1000) * 1024:.2f} KB")
        
        results = {
            "baseline_mb": round(baseline_mb, 2),
            "with_1000_files_mb": round(loaded_mb, 2),
            "increase_mb": round(memory_increase, 2),
            "per_file_kb": round((memory_increase / 1000) * 1024, 2)
        }
        
        self.results["benchmarks"]["memory_usage"] = results
        return results
    
    def benchmark_database_operations(self, operations=1000):
        """Benchmark database insert/query performance"""
        print("\n" + "="*60)
        print("BENCHMARK 5: Database Performance")
        print("="*60)
        
        from shared.db import init_db, get_conn
        
        # Use test database
        test_db = "benchmark_test.db"
        import shared.db
        original_db = shared.db.DB_PATH
        shared.db.DB_PATH = test_db
        
        # Initialize
        init_db()
        
        results = {}
        
        # Benchmark entropy inserts
        print(f"  Testing {operations} entropy inserts...")
        conn = get_conn()
        cur = conn.cursor()
        
        start_time = time.time()
        for i in range(operations):
            cur.execute(
                "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
                (f"/test/file_{i}.txt", 4.0 + (i % 100) * 0.05)
            )
        conn.commit()
        end_time = time.time()
        
        insert_time = end_time - start_time
        results["entropy_insert"] = {
            "total_time_sec": round(insert_time, 2),
            "throughput_ops_per_sec": round(operations / insert_time, 2),
            "avg_time_ms": round((insert_time / operations) * 1000, 4)
        }
        print(f"    ✓ {operations} inserts in {insert_time:.2f}s ({operations/insert_time:.2f} ops/sec)")
        
        # Benchmark queries
        print(f"  Testing {operations} queries...")
        start_time = time.time()
        for i in range(operations):
            cur.execute("SELECT * FROM entropy WHERE file = ?", (f"/test/file_{i % 100}.txt",))
            cur.fetchall()
        end_time = time.time()
        
        query_time = end_time - start_time
        results["entropy_query"] = {
            "total_time_sec": round(query_time, 2),
            "throughput_ops_per_sec": round(operations / query_time, 2),
            "avg_time_ms": round((query_time / operations) * 1000, 4)
        }
        print(f"    ✓ {operations} queries in {query_time:.2f}s ({operations/query_time:.2f} ops/sec)")
        
        conn.close()
        
        # Cleanup
        os.remove(test_db)
        shared.db.DB_PATH = original_db
        
        self.results["benchmarks"]["database_operations"] = results
        return results
    
    def save_results(self, filename="benchmark_results.json"):
        """Save benchmark results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to {filename}")
    
    def print_summary(self):
        """Print benchmark summary"""
        print("\n" + "="*60)
        print("BENCHMARK SUMMARY")
        print("="*60)
        
        print(f"\nSystem: {self.results['system_info']['cpu_count']} CPUs, "
              f"{self.results['system_info']['total_memory_gb']} GB RAM")
        
        # Key metrics
        if "file_processing" in self.results["benchmarks"]:
            fp = self.results["benchmarks"]["file_processing"]
            if "1000_files" in fp:
                print(f"\nFile Processing (1000 files):")
                print(f"  Throughput: {fp['1000_files']['throughput_files_per_sec']:.2f} files/sec")
                print(f"  Avg time per file: {fp['1000_files']['avg_time_per_file_ms']:.2f} ms")
        
        if "memory_usage" in self.results["benchmarks"]:
            mem = self.results["benchmarks"]["memory_usage"]
            print(f"\nMemory Usage:")
            print(f"  Baseline: {mem['baseline_mb']:.2f} MB")
            print(f"  With 1000 files: {mem['with_1000_files_mb']:.2f} MB")
            print(f"  Per file: {mem['per_file_kb']:.2f} KB")
        
        if "detection_algorithms" in self.results["benchmarks"]:
            det = self.results["benchmarks"]["detection_algorithms"]
            print(f"\nDetection Speed:")
            print(f"  CUSUM: {det['cusum']['throughput_ops_per_sec']:.2f} ops/sec")
            print(f"  Z-score: {det['zscore']['throughput_ops_per_sec']:.2f} ops/sec")
        
        print("\n" + "="*60)


def main():
    """Run all benchmarks"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║   EPA Performance Benchmarking Suite                  ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    benchmark = EPABenchmark()
    
    # Run benchmarks
    benchmark.benchmark_entropy_calculation(iterations=1000)
    benchmark.benchmark_detection_algorithms(iterations=10000)
    benchmark.benchmark_file_processing(file_counts=[100, 500, 1000])
    benchmark.benchmark_memory_usage()
    benchmark.benchmark_database_operations(operations=1000)
    
    # Print summary
    benchmark.print_summary()
    
    # Save results
    benchmark.save_results()
    
    print("\n✅ Benchmarking complete!")
    print("\nResults saved to: benchmark_results.json")
    print("Use this data for your project report performance analysis.\n")


if __name__ == "__main__":
    main()
