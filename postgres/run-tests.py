#!/usr/bin/env python3
"""
Power Laws & Fractals - PostgreSQL Test Runner

Demonstrates:
1. Connecting to PostgreSQL database
2. Loading initial mock data  
3. Projecting future iterations
4. Inserting projected data
5. Visualizing existing vs projected data

Requires: psycopg2 (pip install psycopg2-binary)
Database: postgresql://postgres@localhost:5432/demo
"""

import subprocess
import sys
import math

# ANSI colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RED = '\033[91m'
DIM = '\033[2m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Database connection
DB_CONN = "postgresql://postgres@localhost:5432/demo"


def run_sql(query, fetch=True):
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


def reset_database():
    """Reset database to initial state"""
    print(f"  Resetting database...")
    script_dir = subprocess.run(['dirname', sys.argv[0]], capture_output=True, text=True).stdout.strip()
    if not script_dir:
        script_dir = '.'
    
    result = subprocess.run(
        ['bash', f'{script_dir}/init-db.sh', DB_CONN],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}Failed to reset database: {result.stderr}{RESET}")
        return False
    return True


def get_systems():
    """Get all systems from database"""
    rows = run_sql("""
        SELECT system_id, display_name, class, scale_factor, 
               fractal_dimension, theoretical_log_log_slope, base_scale
        FROM vw_systems
        ORDER BY system_id
    """)
    systems = []
    for row in rows:
        systems.append({
            'system_id': row[0],
            'display_name': row[1],
            'class': row[2],
            'scale_factor': float(row[3]) if row[3] else 1.0,
            'fractal_dimension': float(row[4]) if row[4] else None,
            'theoretical_slope': float(row[5]) if row[5] else 0,
            'base_scale': float(row[6]) if row[6] else 1.0
        })
    return systems


def get_scales(system_id=None):
    """Get scales with calculated fields from database"""
    where = f"WHERE system = '{system_id}'" if system_id else ""
    rows = run_sql(f"""
        SELECT scale_id, system, iteration, measure, scale, log_scale, log_measure
        FROM vw_scales
        {where}
        ORDER BY system, iteration
    """)
    scales = []
    for row in rows:
        scales.append({
            'scale_id': row[0],
            'system': row[1],
            'iteration': int(row[2]),
            'measure': float(row[3]) if row[3] else 0,
            'scale': float(row[4]) if row[4] else 0,
            'log_scale': float(row[5]) if row[5] else 0,
            'log_measure': float(row[6]) if row[6] else 0,
            'is_projected': False
        })
    return scales


def get_system_stats():
    """Get system stats with calculated fields"""
    rows = run_sql("""
        SELECT system_stats_id, system, system_display_name, 
               theoretical_log_log_slope, empirical_log_log_slope, slope_error,
               point_count
        FROM vw_system_stats
        ORDER BY system
    """)
    stats = []
    for row in rows:
        stats.append({
            'system_stats_id': row[0],
            'system': row[1],
            'display_name': row[2],
            'theoretical_slope': float(row[3]) if row[3] else 0,
            'empirical_slope': float(row[4]) if row[4] else 0,
            'slope_error': float(row[5]) if row[5] else 0,
            'point_count': int(row[6]) if row[6] else 0
        })
    return stats


def project_future_scales(systems, num_future=4):
    """Generate future scale points"""
    projected = []
    
    for system in systems:
        scales = get_scales(system['system_id'])
        if not scales:
            continue
        
        max_iteration = max(s['iteration'] for s in scales)
        last_measure = [s['measure'] for s in scales if s['iteration'] == max_iteration][0]
        
        for i in range(1, num_future + 1):
            new_iteration = max_iteration + i
            
            if system['class'] == 'fractal' and system['fractal_dimension']:
                growth_factor = (1 / system['scale_factor']) ** system['fractal_dimension']
                new_measure = last_measure * (growth_factor ** i)
            else:
                # Power law: measure scales as scale_factor^slope per iteration
                new_measure = last_measure * (system['scale_factor'] ** (system['theoretical_slope'] * i))
            
            scale = system['base_scale'] * (system['scale_factor'] ** new_iteration)
            log_scale = math.log10(scale) if scale > 0 else 0
            log_measure = math.log10(new_measure) if new_measure > 0 else 0
            
            projected.append({
                'scale_id': f"{system['system_id']}_{new_iteration}",
                'system': system['system_id'],
                'iteration': new_iteration,
                'measure': new_measure,
                'scale': scale,
                'log_scale': log_scale,
                'log_measure': log_measure,
                'is_projected': True
            })
    
    return projected


def insert_projected_scales(projected):
    """Insert projected scales into database"""
    for p in projected:
        run_sql(f"""
            INSERT INTO scales (scale_id, system, iteration, measure)
            VALUES ('{p['scale_id']}', '{p['system']}', {p['iteration']}, {p['measure']})
            ON CONFLICT (scale_id) DO NOTHING
        """, fetch=False)


def print_data_table(system, existing_scales, projected_scales):
    """Print a table of existing and projected data"""
    print(f"\n{BOLD}{system['display_name']}{RESET}")
    print(f"{'─' * 75}")
    print(f"  {'Iter':>4}  {'Measure':>14}  {'Scale':>12}  {'Log(Scale)':>10}  {'Log(Measure)':>12}  {'Status'}")
    print(f"{'─' * 75}")
    
    for s in sorted(existing_scales, key=lambda x: x['iteration']):
        print(f"  {s['iteration']:>4}  {s['measure']:>14.6f}  {s['scale']:>12.8f}  {s['log_scale']:>10.4f}  {s['log_measure']:>12.4f}  {GREEN}existing{RESET}")
    
    for s in sorted(projected_scales, key=lambda x: x['iteration']):
        print(f"  {s['iteration']:>4}  {s['measure']:>14.6f}  {s['scale']:>12.8f}  {s['log_scale']:>10.4f}  {s['log_measure']:>12.4f}  {YELLOW}projected{RESET}")
    
    print(f"{'─' * 75}")


def visualize_log_log(system, existing_scales, projected_scales):
    """Create ASCII log-log plot"""
    all_points = existing_scales + projected_scales
    if not all_points:
        return
    
    width = 50
    height = 10
    
    min_x = min(p['log_scale'] for p in all_points)
    max_x = max(p['log_scale'] for p in all_points)
    min_y = min(p['log_measure'] for p in all_points)
    max_y = max(p['log_measure'] for p in all_points)
    
    x_range = max_x - min_x if max_x != min_x else 1
    y_range = max_y - min_y if max_y != min_y else 1
    
    print(f"\n  {DIM}Log-Log Plot:{RESET}")
    
    grid = [[' ' for _ in range(width)] for _ in range(height)]
    
    for p in all_points:
        x = int((p['log_scale'] - min_x) / x_range * (width - 1)) if x_range else width // 2
        y = int((p['log_measure'] - min_y) / y_range * (height - 1)) if y_range else height // 2
        y = height - 1 - y
        
        x = max(0, min(width - 1, x))
        y = max(0, min(height - 1, y))
        
        grid[y][x] = '○' if p['is_projected'] else '●'
    
    print(f"  {max_y:+.2f} ┤{''.join(grid[0])}")
    for row in grid[1:]:
        print(f"        │{''.join(row)}")
    print(f"        └{'─' * width}┘")
    print(f"        {min_x:+.2f}{' ' * (width - 12)}{max_x:+.2f}")
    
    print(f"\n  {GREEN}●{RESET} Existing  {YELLOW}○{RESET} Projected")


def main():
    print(f"\n{'=' * 75}")
    print(f"  {BOLD}🐘 POWER LAWS & FRACTALS - PostgreSQL Test Runner{RESET}")
    print(f"{'=' * 75}")
    
    # Step 1: Reset database
    print(f"\n{CYAN}Step 1: Resetting database to initial state...{RESET}")
    if not reset_database():
        print(f"{RED}Failed to reset database. Is PostgreSQL running?{RESET}")
        print(f"{DIM}Start with: docker run -d -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust postgres{RESET}")
        return
    print(f"  {GREEN}✓ Database reset complete{RESET}")
    
    # Step 2: Load initial data
    print(f"\n{CYAN}Step 2: Loading initial mock data from database...{RESET}")
    systems = get_systems()
    all_scales = get_scales()
    print(f"  Loaded {len(systems)} systems, {len(all_scales)} scale points")
    
    # Step 3: Validate existing data
    print(f"\n{CYAN}Step 3: Validating existing data...{RESET}")
    stats = get_system_stats()
    for st in stats:
        valid = abs(st['slope_error']) < 0.001
        status = f"{GREEN}✓ PASS{RESET}" if valid else f"{YELLOW}✗ FAIL{RESET}"
        print(f"  {st['display_name']:35} {status} (error: {st['slope_error']:.6f})")
    
    # Step 4: Project future data
    print(f"\n{CYAN}Step 4: Projecting future iterations...{RESET}")
    projected = project_future_scales(systems, num_future=4)
    print(f"  Generated {len(projected)} projected points")
    
    # Step 5: Insert projected data
    print(f"\n{CYAN}Step 5: Inserting projected data into database...{RESET}")
    insert_projected_scales(projected)
    print(f"  {GREEN}✓ Inserted {len(projected)} new scale points{RESET}")
    
    # Step 6: Re-fetch and visualize
    print(f"\n{CYAN}Step 6: Visualization (existing vs projected){RESET}")
    print(f"{'=' * 75}")
    
    for system in systems[:2]:
        existing = [s for s in all_scales if s['system'] == system['system_id']]
        proj = [s for s in projected if s['system'] == system['system_id']]
        print_data_table(system, existing, proj)
        visualize_log_log(system, existing, proj)
    
    # Summary
    print(f"\n{BOLD}Summary - All Systems:{RESET}")
    print(f"{'─' * 75}")
    
    # Re-fetch stats after insert
    new_stats = get_system_stats()
    for system in systems:
        existing_count = len([s for s in all_scales if s['system'] == system['system_id']])
        projected_count = len([s for s in projected if s['system'] == system['system_id']])
        new_stat = next((s for s in new_stats if s['system'] == system['system_id']), None)
        new_count = new_stat['point_count'] if new_stat else 0
        icon = "🔺" if system['class'] == 'fractal' else "📈"
        print(f"  {icon} {system['display_name']:35} {GREEN}{existing_count} existing{RESET} + {YELLOW}{projected_count} projected{RESET} = {CYAN}{new_count} total{RESET}")
    
    print(f"\n{'=' * 75}")
    print(f"  {GREEN}✓ PostgreSQL test run complete!{RESET}")
    print(f"{'=' * 75}\n")


if __name__ == '__main__':
    main()

