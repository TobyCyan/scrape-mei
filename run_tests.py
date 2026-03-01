"""
Test runner for ScrapeMei project.

Run all test suites with: python run_tests.py
Run specific test: python run_tests.py TestBugFixes
Run with verbose output: python run_tests.py -v
"""
import sys
import unittest
from pathlib import Path

# Add src/tests to path
tests_path = Path(__file__).parent / 'src' / 'tests'
sys.path.insert(0, str(tests_path))

def run_all_tests(verbosity=2):
    """
    Discover and run all tests in the src/tests directory.
    
    Args:
        verbosity: Test output verbosity (0=quiet, 1=normal, 2=verbose)
        
    Returns:
        True if all tests passed, False otherwise
    """
    # Discover all tests in src/tests directory
    loader = unittest.TestLoader()
    start_dir = str(tests_path)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    # Parse command line arguments
    verbosity = 2
    if '-q' in sys.argv or '--quiet' in sys.argv:
        verbosity = 0
    elif '-v' in sys.argv or '--verbose' in sys.argv:
        verbosity = 2
    
    print("=" * 70)
    print("RUNNING ALL TESTS")
    print("=" * 70)
    print()
    
    success = run_all_tests(verbosity=verbosity)
    
    sys.exit(0 if success else 1)
