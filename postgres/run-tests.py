#!/usr/bin/env python3
"""
Power Laws & Fractals - PostgreSQL Test Runner

Follows the unified testing protocol:
1. Initialize database with base-data.json (systems + base scales)
2. Insert test-input.json scales (raw facts only)
3. Query vw_scales to get ALL computed values from PostgreSQL (all 8 iterations)
4. Output results to test-results/postgres-results.json
5. Validate against answer-key.json
6. Display with color-coded actual vs projected and ASCII plots

Requires: PostgreSQL running on localhost:5432 with database 'demo'
"""

import json
import subprocess
import sys
import math
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

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
MAGENTA = '\033[95m'
BLUE = '\033[94m'
WHITE = '\033[97m'
BG_DARK = '\033[48;5;236m'

# Database connection
DB_CONN = "postgresql://postgres@localhost:5432/demo"

# Tolerance for validation
TOLERANCE = 0.0001

# ASCII plot characters
PLOT_CHARS = {
    'actual': '●',
    'projected': '◌',
    'line': '─',
    'theoretical': '╌',
    'axis_v': '│',
    'axis_h': '─',
    'corner': '└',
    'cross': '┼'
}


def run_sql(query: str, fetch: bool = True) -> List[List[str]]:
    """Run SQL query using psql and return results"""
    cmd = ['psql', DB_CONN, '-t', '-A', '-F', '|', '-c', query]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        if fetch and result.stdout.strip():
            rows = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    rows.append(line.split('|'))
            return rows
        return []
    except subprocess.CalledProcessError as e:
        print(f"{RED}SQL Error: {e.stderr}{RESET}")
        return []
    except FileNotFoundError:
        print(f"{RED}Error: psql not found. Install PostgreSQL client tools.{RESET}")
        sys.exit(1)


def run_sql_file(filepath: Path) -> bool:
    """Execute a SQL file"""
    cmd = ['psql', DB_CONN, '-f', str(filepath), '-v', 'ON_ERROR_STOP=1']
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"{RED}Error running SQL file: {e}{RESET}")
        return False


def load_json(path: Path) -> Dict:
    """Load JSON file"""
    with open(path, 'r') as f:
        return json.load(f)


def save_json(path: Path, data: Dict):
    """Save JSON file"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def init_database() -> bool:
    """Initialize database with schema"""
    print(f"  Initializing database schema...")
    
    # Run schema files in order
    sql_files = [
        SCRIPT_DIR / '01-drop-and-create-tables.sql',
        SCRIPT_DIR / '02-create-functions.sql',
        SCRIPT_DIR / '03-create-views.sql',
    ]
    
    for sql_file in sql_files:
        if not sql_file.exists():
            print(f"  {RED}SQL file not found: {sql_file.name}{RESET}")
            return False
        if not run_sql_file(sql_file):
            print(f"  {RED}Failed to run: {sql_file.name}{RESET}")
            return False
    
    return True


def insert_systems(systems: List[Dict]) -> bool:
    """Insert systems from base data"""
    print(f"  Inserting {len(systems)} systems...")
    
    for s in systems:
        # Handle NULL for fractal_dimension
        fd = 'NULL' if s.get('FractalDimension') is None else s['FractalDimension']
        
        query = f"""
            INSERT INTO systems (system_id, display_name, class, base_scale, scale_factor, 
                                measure_name, fractal_dimension, theoretical_log_log_slope)
            VALUES ('{s['SystemID']}', '{s['DisplayName']}', '{s['Class']}', 
                   {s['BaseScale']}, {s['ScaleFactor']}, '{s['MeasureName']}', 
                   {fd}, {s['TheoreticalLogLogSlope']})
            ON CONFLICT (system_id) DO NOTHING
        """
        run_sql(query, fetch=False)
    
    return True


def insert_base_scales(scales: List[Dict]) -> bool:
    """Insert base scales from base data"""
    print(f"  Inserting {len(scales)} base scales...")
    
    for s in scales:
        is_projected = 'true' if s.get('IsProjected', False) else 'false'
        query = f"""
            INSERT INTO scales (scale_id, "system", iteration, measure, is_projected)
            VALUES ('{s['ScaleID']}', '{s['System']}', {s['Iteration']}, {s['Measure']}, {is_projected})
            ON CONFLICT (scale_id) DO NOTHING
        """
        run_sql(query, fetch=False)
    
    return True


def insert_test_scales(scales: List[Dict]) -> bool:
    """Insert test scales (raw facts only)"""
    print(f"  Inserting {len(scales)} test scales...")
    
    for s in scales:
        is_projected = 'true' if s.get('IsProjected', True) else 'false'
        query = f"""
            INSERT INTO scales (scale_id, "system", iteration, measure, is_projected)
            VALUES ('{s['ScaleID']}', '{s['System']}', {s['Iteration']}, {s['Measure']}, {is_projected})
            ON CONFLICT (scale_id) DO NOTHING
        """
        run_sql(query, fetch=False)
    
    return True


def query_all_scales() -> List[Dict]:
    """Query ALL computed values from vw_scales view"""
    
    query = """
        SELECT scale_id, "system", iteration, measure, 
               base_scale, scale_factor, scale_factor_power, 
               scale, log_scale, log_measure, is_projected
        FROM vw_scales
        ORDER BY "system", iteration
    """
    
    rows = run_sql(query)
    
    scales = []
    for row in rows:
        scales.append({
            'ScaleID': row[0],
            'System': row[1],
            'Iteration': int(row[2]) if row[2] else 0,
            'Measure': float(row[3]) if row[3] else 0,
            'BaseScale': round(float(row[4]), 5) if row[4] else None,
            'ScaleFactor': round(float(row[5]), 5) if row[5] else None,
            'ScaleFactorPower': round(float(row[6]), 5) if row[6] else None,
            'Scale': round(float(row[7]), 5) if row[7] else None,
            'LogScale': round(float(row[8]), 5) if row[8] else None,
            'LogMeasure': round(float(row[9]), 5) if row[9] else None,
            'IsProjected': row[10] == 't' if row[10] else False
        })
    
    return scales


def query_test_scales(test_scale_ids: List[str]) -> List[Dict]:
    """Query computed values for test scales only (for validation)"""
    
    ids_str = "', '".join(test_scale_ids)
    
    query = f"""
        SELECT scale_id, "system", iteration, measure, 
               base_scale, scale_factor, scale_factor_power, 
               scale, log_scale, log_measure, is_projected
        FROM vw_scales
        WHERE scale_id IN ('{ids_str}')
        ORDER BY scale_id
    """
    
    rows = run_sql(query)
    
    scales = []
    for row in rows:
        scales.append({
            'ScaleID': row[0],
            'System': row[1],
            'Iteration': int(row[2]) if row[2] else 0,
            'Measure': float(row[3]) if row[3] else 0,
            'BaseScale': round(float(row[4]), 5) if row[4] else None,
            'ScaleFactor': round(float(row[5]), 5) if row[5] else None,
            'ScaleFactorPower': round(float(row[6]), 5) if row[6] else None,
            'Scale': round(float(row[7]), 5) if row[7] else None,
            'LogScale': round(float(row[8]), 5) if row[8] else None,
            'LogMeasure': round(float(row[9]), 5) if row[9] else None,
            'IsProjected': row[10] == 't' if row[10] else True
        })
    
    return scales


def compare_values(expected, actual, tolerance: float = TOLERANCE) -> bool:
    """Compare two values with tolerance for floats"""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(expected - actual) < tolerance
    return expected == actual


def validate_results(computed_scales: List[Dict], answer_key: Dict) -> Tuple[int, int, List]:
    """Validate computed scales against answer key"""
    expected_by_id = {s['ScaleID']: s for s in answer_key.get('scales', [])}
    
    pass_count = 0
    fail_count = 0
    failures = []
    
    computed_fields = ['BaseScale', 'ScaleFactor', 'ScaleFactorPower', 'Scale', 'LogScale', 'LogMeasure']
    
    for scale in computed_scales:
        expected = expected_by_id.get(scale['ScaleID'])
        if not expected:
            # Not a test scale - skip validation
            continue
        
        mismatches = []
        
        for field in computed_fields:
            exp_val = expected.get(field)
            act_val = scale.get(field)
            
            if not compare_values(exp_val, act_val):
                mismatches.append(f"{field}: expected {exp_val}, got {act_val}")
        
        if mismatches:
            fail_count += 1
            failures.append((scale['ScaleID'], mismatches))
        else:
            pass_count += 1
    
    return pass_count, fail_count, failures


def render_ascii_plot(scales: List[Dict], system: Dict, width: int = 50, height: int = 12) -> str:
    """Render an ASCII plot for log-log data"""
    
    if not scales:
        return "  (No data)"
    
    # Get data points
    points = [(s['LogScale'], s['LogMeasure'], s['IsProjected']) for s in scales if s['LogScale'] is not None and s['LogMeasure'] is not None]
    
    if not points:
        return "  (No valid data points)"
    
    # Calculate bounds
    x_vals = [p[0] for p in points]
    y_vals = [p[1] for p in points]
    
    x_min, x_max = min(x_vals), max(x_vals)
    y_min, y_max = min(y_vals), max(y_vals)
    
    # Add padding
    x_range = x_max - x_min if x_max != x_min else 1
    y_range = y_max - y_min if y_max != y_min else 1
    
    # Create plot grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    # Map coordinates to grid
    def to_grid(x, y):
        gx = int((x - x_min) / x_range * (width - 1)) if x_range else width // 2
        gy = height - 1 - int((y - y_min) / y_range * (height - 1)) if y_range else height // 2
        return max(0, min(width - 1, gx)), max(0, min(height - 1, gy))
    
    # Draw theoretical slope line
    slope = system.get('TheoreticalLogLogSlope', 0)
    if slope != 0:
        # Line passes through first point with given slope
        x0, y0 = x_vals[0], y_vals[0]
        for i in range(width):
            x = x_min + (i / (width - 1)) * x_range
            y = y0 + slope * (x - x0)
            if y_min <= y <= y_max:
                gx, gy = to_grid(x, y)
                if grid[gy][gx] == ' ':
                    grid[gy][gx] = f'{DIM}·{RESET}'
    
    # Plot data points
    for x, y, is_projected in points:
        gx, gy = to_grid(x, y)
        if is_projected:
            grid[gy][gx] = f'{MAGENTA}{PLOT_CHARS["projected"]}{RESET}'
        else:
            grid[gy][gx] = f'{GREEN}{PLOT_CHARS["actual"]}{RESET}'
    
    # Build output
    lines = []
    
    # Y-axis label
    lines.append(f"  {DIM}log(Measure){RESET}")
    
    # Top y value
    lines.append(f"  {y_max:>7.2f} ┤")
    
    # Grid rows
    for i, row in enumerate(grid):
        prefix = "        │" if i != len(grid) - 1 else f"  {y_min:>7.2f} ┤"
        lines.append(prefix + ''.join(row))
    
    # X-axis
    lines.append(f"         └{'─' * width}")
    lines.append(f"         {x_min:<7.2f}{' ' * (width - 14)}{x_max:>7.2f}")
    lines.append(f"  {DIM}{'log(Scale)':^{width + 9}}{RESET}")
    
    # Legend
    lines.append(f"  {GREEN}●{RESET} Actual   {MAGENTA}◌{RESET} Projected   {DIM}·{RESET} Theoretical (slope={slope})")
    
    return '\n'.join(lines)


def print_console_output(all_scales: List[Dict], base_data: Dict,
                         pass_count: int, fail_count: int, failures: List):
    """Print results to console with all 8 rows and colors"""
    print(f"\n{'=' * 80}")
    print(f"  {BOLD}🐘 POWER LAWS & FRACTALS - PostgreSQL Test Runner{RESET}")
    print(f"{'=' * 80}")
    
    # Build systems lookup
    systems = {s['SystemID']: s for s in base_data.get('systems', [])}
    
    # Group scales by system
    by_system = {}
    for scale in all_scales:
        if scale['System'] not in by_system:
            by_system[scale['System']] = []
        by_system[scale['System']].append(scale)
    
    print(f"\n{CYAN}All Computed Values (from PostgreSQL views):{RESET}")
    print(f"  {GREEN}● Green{RESET} = Actual Data (iterations 0-3)")
    print(f"  {MAGENTA}◌ Magenta{RESET} = Projected/Computed (iterations 4-7)")
    print(f"{'─' * 80}")
    
    for system_id in sorted(by_system.keys()):
        scales = by_system[system_id]
        system = systems.get(system_id, {})
        icon = "🔺" if system.get('Class') == "fractal" else "📈"
        
        print(f"\n{icon} {BOLD}{system.get('DisplayName', system_id)}{RESET}")
        print(f"  {DIM}Theoretical slope: {system.get('TheoreticalLogLogSlope', 'N/A')}{RESET}")
        
        # Header
        print(f"\n  {'Iter':>4}  {'Measure':>12}  {'Scale':>14}  {'LogScale':>10}  {'LogMeasure':>12}  {'Type':>10}")
        print(f"  {'─' * 70}")
        
        # Data rows with colors
        for s in sorted(scales, key=lambda x: x['Iteration']):
            is_proj = s.get('IsProjected', False)
            color = MAGENTA if is_proj else GREEN
            marker = "◌" if is_proj else "●"
            type_label = "projected" if is_proj else "actual"
            
            print(f"  {color}{s['Iteration']:>4}  {s['Measure']:>12.6f}  {s['Scale']:>14.8f}  {s['LogScale']:>10.5f}  {s['LogMeasure']:>12.5f}  {marker} {type_label}{RESET}")
        
        print(f"\n  {DIM}Row count: {len(scales)}{RESET}")
        
        # ASCII Plot
        print(f"\n{CYAN}  Log-Log Plot:{RESET}")
        plot = render_ascii_plot(scales, system)
        print(plot)
    
    # Validation results
    print(f"\n{'=' * 80}")
    print(f"{CYAN}Validation Results (projected scales vs answer-key):{RESET}")
    print(f"{'─' * 80}")
    
    if fail_count == 0:
        print(f"  {GREEN}✓ All {pass_count} projected scales validated successfully!{RESET}")
    else:
        print(f"  {YELLOW}⚠ {pass_count} passed, {fail_count} failed{RESET}")
        for scale_id, mismatches in failures[:5]:
            print(f"    • {scale_id}:")
            if isinstance(mismatches, list):
                for m in mismatches:
                    print(f"      - {m}")
            else:
                print(f"      - {mismatches}")
    
    # Summary stats
    total_scales = len(all_scales)
    systems_count = len(by_system)
    
    print(f"\n{'=' * 80}")
    print(f"  {BOLD}Summary:{RESET}")
    print(f"    Systems: {systems_count}")
    print(f"    Total scales: {total_scales} ({total_scales // systems_count} per system)")
    print(f"    Actual (0-3): {sum(1 for s in all_scales if not s.get('IsProjected', False))}")
    print(f"    Projected (4-7): {sum(1 for s in all_scales if s.get('IsProjected', False))}")
    print(f"{'=' * 80}")
    print(f"  {GREEN}✓ PostgreSQL test run complete!{RESET}")
    print(f"{'=' * 80}\n")


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
    
    print(f"\n{CYAN}Initializing PostgreSQL database...{RESET}")
    
    # Initialize database schema
    if not init_database():
        print(f"{RED}Failed to initialize database. Is PostgreSQL running?{RESET}")
        print(f"{DIM}Start with: docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres{RESET}")
        sys.exit(1)
    
    # Insert systems
    if not insert_systems(base_data.get('systems', [])):
        print(f"{RED}Failed to insert systems{RESET}")
        sys.exit(1)
    
    # Insert base scales (iterations 0-3)
    if not insert_base_scales(base_data.get('scales', [])):
        print(f"{RED}Failed to insert base scales{RESET}")
        sys.exit(1)
    
    # Insert test scales (iterations 4-7)
    if not insert_test_scales(test_input.get('scales', [])):
        print(f"{RED}Failed to insert test scales{RESET}")
        sys.exit(1)
    
    print(f"  {GREEN}✓ Database initialized with test data{RESET}")
    
    # Query ALL computed values from view (all 8 iterations)
    print(f"\n{CYAN}Querying ALL computed values from vw_scales...{RESET}")
    all_scales = query_all_scales()
    print(f"  Retrieved {len(all_scales)} computed scales (all iterations)")
    
    # Save full results (all 8 iterations per system)
    full_results = {
        'platform': 'postgres',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'scales': all_scales
    }
    
    full_results_path = TEST_RESULTS_DIR / 'postgres-results.json'
    save_json(full_results_path, full_results)
    
    # Validate only the projected scales against answer key
    answer_key = load_json(answer_key_path)
    test_scale_ids = [s['ScaleID'] for s in test_input.get('scales', [])]
    test_scales = [s for s in all_scales if s['ScaleID'] in test_scale_ids]
    pass_count, fail_count, failures = validate_results(test_scales, answer_key)
    
    # Print console output with all data
    print_console_output(all_scales, base_data, pass_count, fail_count, failures)
    
    # Exit with appropriate code
    sys.exit(0 if fail_count == 0 else 1)


if __name__ == '__main__':
    main()
