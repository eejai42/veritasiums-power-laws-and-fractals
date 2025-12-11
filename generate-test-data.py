#!/usr/bin/env python3
"""
Generate Test Data from SSoT

Creates the test-data/ directory with:
- base-data.json: Iterations 0-3 with all values (for platform initialization)
- test-input.json: Iterations 4-7 with only raw facts (for testing)
- answer-key.json: Iterations 4-7 with all computed values (for validation)
"""

import json
import os
from pathlib import Path
from datetime import datetime, timezone

# Paths
SCRIPT_DIR = Path(__file__).parent
SSOT_PATH = SCRIPT_DIR / 'ssot' / 'ERB_veritasium-power-laws-and-fractals.json'
TEST_DATA_DIR = SCRIPT_DIR / 'test-data'
TEST_RESULTS_DIR = SCRIPT_DIR / 'test-results'

# Raw fact fields (what platforms receive in test input)
RAW_SCALE_FIELDS = ['ScaleID', 'System', 'Iteration', 'Measure', 'IsProjected']

# All fields for scales (for base data and answer key)
ALL_SCALE_FIELDS = [
    'ScaleID', 'System', 'Iteration', 'Measure', 'BaseScale', 'ScaleFactor',
    'ScaleFactorPower', 'Scale', 'LogScale', 'LogMeasure', 'IsProjected'
]


def load_ssot():
    """Load the SSoT JSON file"""
    with open(SSOT_PATH, 'r') as f:
        return json.load(f)


def extract_raw_facts(scale):
    """Extract only raw fact fields from a scale record"""
    return {k: scale.get(k) for k in RAW_SCALE_FIELDS}


def extract_all_fields(scale):
    """Extract all fields from a scale record"""
    return {k: scale.get(k) for k in ALL_SCALE_FIELDS}


def generate_test_data():
    """Generate all test data files"""
    print("Generating test data from SSoT...")
    
    # Load SSoT
    ssot = load_ssot()
    
    # Create output directories
    TEST_DATA_DIR.mkdir(exist_ok=True)
    TEST_RESULTS_DIR.mkdir(exist_ok=True)
    
    # Extract systems (all of them, as they are needed for lookups)
    systems = ssot['systems']['data']
    
    # Extract scales
    all_scales = ssot['scales']['data']
    
    # Separate base data (IsProjected=false) from test data (IsProjected=true)
    base_scales = [s for s in all_scales if not s.get('IsProjected', False)]
    test_scales = [s for s in all_scales if s.get('IsProjected', False)]
    
    print(f"  Found {len(base_scales)} base scale records (iterations 0-3)")
    print(f"  Found {len(test_scales)} test scale records (iterations 4-7)")
    
    # Generate base-data.json
    base_data = {
        'description': 'Base data for platform initialization (iterations 0-3)',
        'generated': datetime.now(timezone.utc).isoformat(),
        'source': 'ssot/ERB_veritasium-power-laws-and-fractals.json',
        'systems': systems,
        'scales': [extract_all_fields(s) for s in base_scales]
    }
    
    base_data_path = TEST_DATA_DIR / 'base-data.json'
    with open(base_data_path, 'w') as f:
        json.dump(base_data, f, indent=2)
    print(f"  ✓ Generated {base_data_path}")
    
    # Generate test-input.json (only raw facts)
    test_input = {
        'description': 'Test input with only raw facts (platforms must compute derived values)',
        'generated': datetime.now(timezone.utc).isoformat(),
        'source': 'ssot/ERB_veritasium-power-laws-and-fractals.json',
        'scales': [extract_raw_facts(s) for s in test_scales]
    }
    
    test_input_path = TEST_DATA_DIR / 'test-input.json'
    with open(test_input_path, 'w') as f:
        json.dump(test_input, f, indent=2)
    print(f"  ✓ Generated {test_input_path}")
    
    # Generate answer-key.json (all computed values)
    answer_key = {
        'description': 'Expected results for test validation (all computed values)',
        'generated': datetime.now(timezone.utc).isoformat(),
        'source': 'ssot/ERB_veritasium-power-laws-and-fractals.json',
        'scales': [extract_all_fields(s) for s in test_scales]
    }
    
    answer_key_path = TEST_DATA_DIR / 'answer-key.json'
    with open(answer_key_path, 'w') as f:
        json.dump(answer_key, f, indent=2)
    print(f"  ✓ Generated {answer_key_path}")
    
    # Create empty .gitkeep for test-results (results are generated, not committed)
    gitkeep_path = TEST_RESULTS_DIR / '.gitkeep'
    gitkeep_path.touch()
    print(f"  ✓ Created {TEST_RESULTS_DIR}")
    
    print("\n✓ Test data generation complete!")
    print(f"\nTest data structure:")
    print(f"  test-data/base-data.json   - {len(base_scales)} scales (init platforms)")
    print(f"  test-data/test-input.json  - {len(test_scales)} scales (raw facts only)")
    print(f"  test-data/answer-key.json  - {len(test_scales)} scales (expected results)")


if __name__ == '__main__':
    generate_test_data()

