#!/usr/bin/env python3
"""
Power Laws & Fractals - Python Test Runner

Follows the unified testing protocol:
1. Load base-data.json (for systems configuration)
2. Load test-input.json (raw facts only)
3. Compute derived values for test scales
4. Output results to test-results/python-results.json
5. Validate against answer-key.json
"""

import json
import math
import sys
from pathlib import Path
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEST_DATA_DIR = PROJECT_ROOT / 'test-data'
TEST_RESULTS_DIR = PROJECT_ROOT / 'test-results'

# ANSI colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RED = '\033[91m'
DIM = '\033[2m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Tolerance for validation (SSoT has pre-rounded values, so 0.0001 allows for rounding differences)
TOLERANCE = 0.0001


@dataclass
class System:
    """System configuration from ERB"""
    SystemID: str
    DisplayName: str
    Class: str
    BaseScale: float
    ScaleFactor: float
    MeasureName: str
    FractalDimension: Optional[float]
    TheoreticalLogLogSlope: float


@dataclass
class Scale:
    """Scale measurement with computed values"""
    ScaleID: str
    System: str
    Iteration: int
    Measure: float
    BaseScale: Optional[float] = None
    ScaleFactor: Optional[float] = None
    ScaleFactorPower: Optional[float] = None
    Scale: Optional[float] = None
    LogScale: Optional[float] = None
    LogMeasure: Optional[float] = None
    IsProjected: bool = False


def load_json(path: Path) -> Dict:
    """Load JSON file"""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: Dict):
    """Save JSON file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def load_systems(base_data: Dict) -> Dict[str, System]:
    """Load systems from base data and create lookup dict"""
    systems = {}
    for s in base_data.get('systems', []):
        system = System(
            SystemID=s['SystemID'],
            DisplayName=s['DisplayName'],
            Class=s['Class'],
            BaseScale=s['BaseScale'],
            ScaleFactor=s['ScaleFactor'],
            MeasureName=s['MeasureName'],
            FractalDimension=s.get('FractalDimension'),
            TheoreticalLogLogSlope=s['TheoreticalLogLogSlope']
        )
        systems[system.SystemID] = system
    return systems


def load_test_scales(test_input: Dict) -> List[Scale]:
    """Load test scales from test input (raw facts only)"""
    scales = []
    for s in test_input.get('scales', []):
        scale = Scale(
            ScaleID=s['ScaleID'],
            System=s['System'],
            Iteration=s['Iteration'],
            Measure=s['Measure'],
            IsProjected=s.get('IsProjected', True)
        )
        scales.append(scale)
    return scales


def compute_derived_values(scale: Scale, systems: Dict[str, System]) -> Scale:
    """Compute all derived values for a scale"""
    system = systems.get(scale.System)
    if not system:
        raise ValueError(f"System not found: {scale.System}")
    
    # Lookup values from parent system
    scale.BaseScale = system.BaseScale
    scale.ScaleFactor = system.ScaleFactor
    
    # Calculated values
    scale.ScaleFactorPower = math.pow(scale.ScaleFactor, scale.Iteration)
    scale.Scale = scale.BaseScale * scale.ScaleFactorPower
    scale.LogScale = math.log10(scale.Scale) if scale.Scale > 0 else 0
    scale.LogMeasure = math.log10(scale.Measure) if scale.Measure > 0 else 0
    
    return scale


def round_for_comparison(value: float, decimals: int = 5) -> float:
    """Round a float for consistent comparison"""
    if value is None:
        return None
    return round(value, decimals)


def scale_to_dict(scale: Scale) -> Dict:
    """Convert Scale to dict with rounded values for JSON output"""
    return {
        'ScaleID': scale.ScaleID,
        'System': scale.System,
        'Iteration': scale.Iteration,
        'Measure': scale.Measure,
        'BaseScale': round_for_comparison(scale.BaseScale),
        'ScaleFactor': round_for_comparison(scale.ScaleFactor),
        'ScaleFactorPower': round_for_comparison(scale.ScaleFactorPower),
        'Scale': round_for_comparison(scale.Scale),
        'LogScale': round_for_comparison(scale.LogScale),
        'LogMeasure': round_for_comparison(scale.LogMeasure),
        'IsProjected': scale.IsProjected
    }


def compare_values(expected, actual, tolerance: float = TOLERANCE) -> bool:
    """Compare two values with tolerance for floats"""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(expected - actual) < tolerance
    return expected == actual


def validate_results(computed_scales: List[Scale], answer_key: Dict) -> tuple:
    """Validate computed scales against answer key"""
    expected_by_id = {s['ScaleID']: s for s in answer_key.get('scales', [])}
    
    pass_count = 0
    fail_count = 0
    failures = []
    
    computed_fields = ['BaseScale', 'ScaleFactor', 'ScaleFactorPower', 'Scale', 'LogScale', 'LogMeasure']
    
    for scale in computed_scales:
        expected = expected_by_id.get(scale.ScaleID)
        if not expected:
            fail_count += 1
            failures.append((scale.ScaleID, "Not found in answer key"))
            continue
        
        scale_dict = scale_to_dict(scale)
        mismatches = []
        
        for field in computed_fields:
            exp_val = expected.get(field)
            act_val = scale_dict.get(field)
            
            if not compare_values(exp_val, act_val):
                mismatches.append(f"{field}: expected {exp_val}, got {act_val}")
        
        if mismatches:
            fail_count += 1
            failures.append((scale.ScaleID, mismatches))
        else:
            pass_count += 1
    
    return pass_count, fail_count, failures


def print_console_output(systems: Dict[str, System], computed_scales: List[Scale],
                         pass_count: int, fail_count: int, failures: List):
    """Print results to console"""
    print(f"\n{'=' * 70}")
    print(f"  {BOLD}🐍 POWER LAWS & FRACTALS - Python Test Runner{RESET}")
    print(f"{'=' * 70}")
    
    # Group scales by system
    by_system = {}
    for scale in computed_scales:
        if scale.System not in by_system:
            by_system[scale.System] = []
        by_system[scale.System].append(scale)
    
    print(f"\n{CYAN}Computed Values for Test Scales:{RESET}")
    print(f"{'─' * 70}")
    
    for system_id, scales in sorted(by_system.items()):
        system = systems.get(system_id)
        icon = "🔺" if system and system.Class == "fractal" else "📈"
        print(f"\n{icon} {BOLD}{system.DisplayName if system else system_id}{RESET}")
        print(f"  {'Iter':>4} {'Measure':>12} {'Scale':>12} {'LogScale':>10} {'LogMeasure':>12}")
        print(f"  {'-' * 54}")
        
        for s in sorted(scales, key=lambda x: x.Iteration):
            print(f"  {s.Iteration:>4} {s.Measure:>12.6f} {s.Scale:>12.8f} {s.LogScale:>10.5f} {s.LogMeasure:>12.5f}")
    
    # Validation results
    print(f"\n{CYAN}Validation Results:{RESET}")
    print(f"{'─' * 70}")
    
    if fail_count == 0:
        print(f"  {GREEN}✓ All {pass_count} scales validated successfully!{RESET}")
    else:
        print(f"  {YELLOW}⚠ {pass_count} passed, {fail_count} failed{RESET}")
        for scale_id, mismatches in failures[:5]:
            print(f"    • {scale_id}:")
            if isinstance(mismatches, list):
                for m in mismatches:
                    print(f"      - {m}")
            else:
                print(f"      - {mismatches}")
    
    print(f"\n{'=' * 70}")
    print(f"  {GREEN}✓ Python test run complete!{RESET}")
    print(f"{'=' * 70}\n")


def main():
    """Main test runner"""
    # Check if test data exists
    base_data_path = TEST_DATA_DIR / 'base-data.json'
    test_input_path = TEST_DATA_DIR / 'test-input.json'
    answer_key_path = TEST_DATA_DIR / 'answer-key.json'
    
    if not base_data_path.exists() or not test_input_path.exists():
        print(f"{RED}Error: Test data not found. Run generate-test-data.py first.{RESET}")
        sys.exit(1)
    
    # Load data
    base_data = load_json(base_data_path)
    test_input = load_json(test_input_path)
    
    # Load systems
    systems = load_systems(base_data)
    
    # Load test scales (raw facts only)
    test_scales = load_test_scales(test_input)
    
    # Compute derived values
    computed_scales = []
    for scale in test_scales:
        computed = compute_derived_values(scale, systems)
        computed_scales.append(computed)
    
    # Save results
    results = {
        'platform': 'python',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scales': [scale_to_dict(s) for s in computed_scales]
    }
    
    results_path = TEST_RESULTS_DIR / 'python-results.json'
    save_json(results_path, results)
    
    # Validate against answer key
    answer_key = load_json(answer_key_path)
    pass_count, fail_count, failures = validate_results(computed_scales, answer_key)
    
    # Print console output
    print_console_output(systems, computed_scales, pass_count, fail_count, failures)
    
    # Exit with appropriate code
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == '__main__':
    main()
