#!/usr/bin/env python3
"""
Quick start script for automotive test framework.

Run tests immediately with common configurations.
"""

import sys
import subprocess
from pathlib import Path


def run_setup():
    """Run setup verification."""
    print("Running setup verification...\n")
    setup_script = Path(__file__).parent / "setup_project.py"
    result = subprocess.run([sys.executable, str(setup_script)])
    return result.returncode == 0


def run_tests(test_filter=None):
    """Run Robot Framework tests."""
    cmd = ["robot"]
    
    if test_filter:
        cmd.extend(["-t", test_filter])
    
    cmd.extend([
        "--outputdir", "results",
        "tests/"
    ])
    
    print(f"\nRunning: {' '.join(cmd)}\n")
    result = subprocess.run(cmd)
    return result.returncode


def run_examples():
    """Run usage examples."""
    examples_script = Path(__file__).parent / "examples.py"
    result = subprocess.run([sys.executable, str(examples_script)])
    return result.returncode


def main():
    """Main menu."""
    print("\n" + "="*60)
    print(" AUTOMOTIVE TEST FRAMEWORK - QUICK START ".center(60, "="))
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("  1. Run setup verification")
        print("  2. Run all tests")
        print("  3. Run specific test")
        print("  4. View usage examples")
        print("  5. Exit")
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            if run_setup():
                print("\n✓ Setup verification passed!")
        
        elif choice == "2":
            run_tests()
        
        elif choice == "3":
            test_name = input("Enter test name: ").strip()
            if test_name:
                run_tests(test_name)
        
        elif choice == "4":
            run_examples()
        
        elif choice == "5":
            print("\nExiting...\n")
            break
        
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
