"""Evaluation script for Decision-Minutes Copilot"""
import json
import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.extraction import extract_action_items

def load_test_cases():
    """Load test cases from JSON file."""
    test_file = Path(__file__).parent / 'test_cases.json'
    with open(test_file) as f:
        return json.load(f)['test_cases']

def evaluate_extraction(test_case: dict) -> dict:
    """Run extraction on a test case and compare results."""
    transcript = test_case['transcript']
    expected = test_case['expected']
    
    try:
        result = extract_action_items(transcript)
        
        # Compare action items count
        expected_actions = len(expected.get('action_items', []))
        actual_actions = len(result.get('action_items', []))
        
        # Compare decisions count
        expected_decisions = len(expected.get('decisions', []))
        actual_decisions = len(result.get('decisions', []))
        
        return {
            'id': test_case['id'],
            'name': test_case['name'],
            'passed': True,
            'expected_actions': expected_actions,
            'actual_actions': actual_actions,
            'expected_decisions': expected_decisions,
            'actual_decisions': actual_decisions,
            'result': result
        }
    except Exception as e:
        return {
            'id': test_case['id'],
            'name': test_case['name'],
            'passed': False,
            'error': str(e)
        }

def run_evals():
    """Run all evaluation cases."""
    print("=" * 60)
    print("Decision-Minutes Copilot - Evaluation Suite")
    print("=" * 60)
    
    test_cases = load_test_cases()
    results = []
    
    for tc in test_cases:
        print(f"\nRunning: {tc['id']} - {tc['name']}")
        result = evaluate_extraction(tc)
        results.append(result)
        
        if result['passed']:
            print(f"  ✓ Actions: {result['actual_actions']} (expected {result['expected_actions']})")
            print(f"  ✓ Decisions: {result['actual_decisions']} (expected {result['expected_decisions']})")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown')}")
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    total = len(results)
    
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    return results

if __name__ == '__main__':
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not set")
        print("Please set your API key: set OPENAI_API_KEY=your_key_here")
        sys.exit(1)
    
    run_evals()
