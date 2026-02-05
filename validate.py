#!/usr/bin/env python3
"""
EPA Validation Script
Runs all 6 simulators and generates validation metrics
Calculates accuracy, precision, recall, F1-score, and confusion matrix
"""

import time
import subprocess
import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from shared.db import get_conn, init_db


class EPAValidator:
    """Validate EPA detection system"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "metrics": {}
        }
        
        # Confusion matrix
        self.true_positives = 0   # Malicious detected as malicious
        self.true_negatives = 0   # Benign detected as benign
        self.false_positives = 0  # Benign detected as malicious
        self.false_negatives = 0  # Malicious detected as benign
    
    def clear_database(self):
        """Clear alerts from database"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM alerts")
        cur.execute("DELETE FROM entropy")
        conn.commit()
        conn.close()
    
    def get_alert_count(self):
        """Get number of alerts in database"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alerts")
        count = cur.fetchone()[0]
        conn.close()
        return count
    
    def run_simulator(self, simulator_path, test_folder, expected_detection=True):
        """Run a simulator and check for detection"""
        print(f"\n{'='*60}")
        print(f"Testing: {Path(simulator_path).stem}")
        print(f"{'='*60}")
        
        # Clear previous data
        self.clear_database()
        
        # Regenerate test data
        print("  Regenerating test data...")
        subprocess.run([
            sys.executable,
            "simulator/generate_test_data.py",
            test_folder,
            "--clean"
        ], capture_output=True, text=True)
        
        # Start EPA in background
        print("  Starting EPA monitoring...")
        epa_process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for EPA to initialize
        time.sleep(2)
        
        # Run simulator
        print(f"  Running simulator...")
        start_time = time.time()
        
        sim_process = subprocess.Popen(
            [sys.executable, simulator_path, test_folder],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Auto-confirm for malicious simulators
        if "malicious" in simulator_path:
            sim_process.communicate(input="yes\n", timeout=30)
        else:
            sim_process.wait(timeout=30)
        
        # Wait for detection
        print("  Waiting for detection...")
        time.sleep(5)
        
        detection_time = time.time() - start_time
        
        # Check for alerts
        alert_count = self.get_alert_count()
        detected = alert_count > 0
        
        # Get detection method
        detection_method = "None"
        if detected:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT message FROM alerts LIMIT 1")
            message = cur.fetchone()[0]
            conn.close()
            
            if "Critical" in message or "High entropy" in message:
                detection_method = "High Entropy (Layer 1)"
            elif "CUSUM" in message:
                detection_method = "CUSUM (Layer 2)"
            elif "spike" in message.lower() or "z-score" in message.lower():
                detection_method = "Z-score (Layer 3)"
        
        # Determine result
        success = detected == expected_detection
        
        # Update confusion matrix
        if expected_detection and detected:
            self.true_positives += 1
            result_type = "True Positive ✓"
        elif expected_detection and not detected:
            self.false_negatives += 1
            result_type = "False Negative ✗"
        elif not expected_detection and detected:
            self.false_positives += 1
            result_type = "False Positive ✗"
        else:  # not expected_detection and not detected
            self.true_negatives += 1
            result_type = "True Negative ✓"
        
        # Store result
        test_result = {
            "simulator": Path(simulator_path).stem,
            "type": "Malicious" if expected_detection else "Benign",
            "expected_detection": expected_detection,
            "detected": detected,
            "alert_count": alert_count,
            "detection_time_sec": round(detection_time, 2),
            "detection_method": detection_method,
            "result": result_type,
            "success": success
        }
        
        self.results["tests"].append(test_result)
        
        # Print result
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n  Result: {status}")
        print(f"  Expected: {'Detection' if expected_detection else 'No Detection'}")
        print(f"  Actual: {'Detected' if detected else 'Not Detected'} ({alert_count} alerts)")
        if detected:
            print(f"  Detection Method: {detection_method}")
            print(f"  Detection Time: {detection_time:.2f}s")
        print(f"  Classification: {result_type}")
        
        # Stop EPA
        epa_process.terminate()
        epa_process.wait(timeout=5)
        
        return test_result
    
    def calculate_metrics(self):
        """Calculate accuracy, precision, recall, F1-score"""
        print(f"\n{'='*60}")
        print("CALCULATING METRICS")
        print(f"{'='*60}")
        
        # Confusion Matrix
        print("\nConfusion Matrix:")
        print(f"  True Positives (TP):  {self.true_positives}")
        print(f"  True Negatives (TN):  {self.true_negatives}")
        print(f"  False Positives (FP): {self.false_positives}")
        print(f"  False Negatives (FN): {self.false_negatives}")
        
        total = self.true_positives + self.true_negatives + self.false_positives + self.false_negatives
        
        # Accuracy
        if total > 0:
            accuracy = (self.true_positives + self.true_negatives) / total
        else:
            accuracy = 0.0
        
        # Precision
        if (self.true_positives + self.false_positives) > 0:
            precision = self.true_positives / (self.true_positives + self.false_positives)
        else:
            precision = 0.0
        
        # Recall (Sensitivity)
        if (self.true_positives + self.false_negatives) > 0:
            recall = self.true_positives / (self.true_positives + self.false_negatives)
        else:
            recall = 0.0
        
        # F1-Score
        if (precision + recall) > 0:
            f1_score = 2 * (precision * recall) / (precision + recall)
        else:
            f1_score = 0.0
        
        # Specificity
        if (self.true_negatives + self.false_positives) > 0:
            specificity = self.true_negatives / (self.true_negatives + self.false_positives)
        else:
            specificity = 0.0
        
        metrics = {
            "confusion_matrix": {
                "true_positives": self.true_positives,
                "true_negatives": self.true_negatives,
                "false_positives": self.false_positives,
                "false_negatives": self.false_negatives
            },
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1_score, 4),
            "specificity": round(specificity, 4)
        }
        
        self.results["metrics"] = metrics
        
        print(f"\nPerformance Metrics:")
        print(f"  Accuracy:    {accuracy*100:.2f}%")
        print(f"  Precision:   {precision*100:.2f}%")
        print(f"  Recall:      {recall*100:.2f}%")
        print(f"  F1-Score:    {f1_score:.4f}")
        print(f"  Specificity: {specificity*100:.2f}%")
        
        return metrics
    
    def print_summary_table(self):
        """Print summary table of all tests"""
        print(f"\n{'='*60}")
        print("VALIDATION SUMMARY")
        print(f"{'='*60}\n")
        
        # Table header
        print(f"{'Simulator':<20} {'Type':<10} {'Detected':<10} {'Time (s)':<10} {'Result':<20}")
        print("-" * 80)
        
        # Table rows
        for test in self.results["tests"]:
            detected_str = "Yes" if test["detected"] else "No"
            print(f"{test['simulator']:<20} {test['type']:<10} {detected_str:<10} "
                  f"{test['detection_time_sec']:<10} {test['result']:<20}")
        
        print("-" * 80)
        
        # Summary
        passed = sum(1 for t in self.results["tests"] if t["success"])
        total = len(self.results["tests"])
        print(f"\nTests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
    
    def save_results(self, filename="validation_results.json"):
        """Save validation results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to {filename}")
    
    def generate_markdown_report(self, filename="VALIDATION_REPORT.md"):
        """Generate markdown report for project documentation"""
        with open(filename, 'w') as f:
            f.write("# EPA Validation Report\n\n")
            f.write(f"**Generated:** {self.results['timestamp']}\n\n")
            
            f.write("## Test Results\n\n")
            f.write("| Simulator | Type | Detected | Alerts | Time (s) | Method | Result |\n")
            f.write("|-----------|------|----------|--------|----------|--------|--------|\n")
            
            for test in self.results["tests"]:
                detected = "✅ Yes" if test["detected"] else "❌ No"
                f.write(f"| {test['simulator']} | {test['type']} | {detected} | "
                       f"{test['alert_count']} | {test['detection_time_sec']} | "
                       f"{test['detection_method']} | {test['result']} |\n")
            
            f.write("\n## Confusion Matrix\n\n")
            cm = self.results["metrics"]["confusion_matrix"]
            f.write("```\n")
            f.write("                Predicted\n")
            f.write("              Malicious  Benign\n")
            f.write(f"Actual Malicious    {cm['true_positives']:<3}      {cm['false_negatives']:<3}\n")
            f.write(f"       Benign       {cm['false_positives']:<3}      {cm['true_negatives']:<3}\n")
            f.write("```\n\n")
            
            f.write("## Performance Metrics\n\n")
            m = self.results["metrics"]
            f.write(f"- **Accuracy:** {m['accuracy']*100:.2f}%\n")
            f.write(f"- **Precision:** {m['precision']*100:.2f}%\n")
            f.write(f"- **Recall:** {m['recall']*100:.2f}%\n")
            f.write(f"- **F1-Score:** {m['f1_score']:.4f}\n")
            f.write(f"- **Specificity:** {m['specificity']*100:.2f}%\n\n")
            
            f.write("## Interpretation\n\n")
            f.write(f"- **True Positives:** {cm['true_positives']} malicious attacks correctly detected\n")
            f.write(f"- **True Negatives:** {cm['true_negatives']} benign activities correctly ignored\n")
            f.write(f"- **False Positives:** {cm['false_positives']} benign activities incorrectly flagged\n")
            f.write(f"- **False Negatives:** {cm['false_negatives']} malicious attacks missed\n")
        
        print(f"✓ Markdown report saved to {filename}")


def main():
    """Run validation tests"""
    print("╔════════════════════════════════════════════════════════╗")
    print("║                                                        ║")
    print("║   EPA Validation Suite                                ║")
    print("║   Testing All Simulators                              ║")
    print("║                                                        ║")
    print("╚════════════════════════════════════════════════════════╝")
    
    validator = EPAValidator()
    
    test_folder = "test-folder"
    
    # Test malicious simulators (should detect)
    print("\n" + "="*60)
    print("TESTING MALICIOUS SIMULATORS (Should Detect)")
    print("="*60)
    
    validator.run_simulator("simulator/malicious/wannacry_sim.py", test_folder, expected_detection=True)
    validator.run_simulator("simulator/malicious/ryuk_sim.py", test_folder, expected_detection=True)
    validator.run_simulator("simulator/malicious/lockbit_sim.py", test_folder, expected_detection=True)
    
    # Test benign simulators (should NOT detect)
    print("\n" + "="*60)
    print("TESTING BENIGN SIMULATORS (Should NOT Detect)")
    print("="*60)
    
    validator.run_simulator("simulator/benign/backup_sim.py", test_folder, expected_detection=False)
    validator.run_simulator("simulator/benign/database_sim.py", test_folder, expected_detection=False)
    validator.run_simulator("simulator/benign/video_sim.py", test_folder, expected_detection=False)
    
    # Calculate metrics
    validator.calculate_metrics()
    
    # Print summary
    validator.print_summary_table()
    
    # Save results
    validator.save_results()
    validator.generate_markdown_report()
    
    print("\n✅ Validation complete!")
    print("\nFiles generated:")
    print("  - validation_results.json (raw data)")
    print("  - VALIDATION_REPORT.md (formatted report for documentation)")
    print("\nUse these files in your project report!\n")


if __name__ == "__main__":
    main()
