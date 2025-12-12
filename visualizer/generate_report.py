#!/usr/bin/env python3
"""
Comprehensive HTML Report Generator with Validation

Generates a full data report with:
- Platform validation status (pass/fail for each scale)
- Failures highlighted in RED
- All 8 iterations per system (actual + projected)
- Full data tables with computed values
- Large interactive log-log charts
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEST_DATA_DIR = PROJECT_ROOT / 'test-data'
TEST_RESULTS_DIR = PROJECT_ROOT / 'test-results'

# Tolerance for floating point comparisons (6 decimal places)
TOLERANCE = 0.0000015

def load_json(path: Path) -> dict:
    if path.exists():
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def compare_values(expected, actual):
    """Compare two values with tolerance"""
    if expected is None and actual is None:
        return True
    if expected is None or actual is None:
        return False
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(expected - actual) < TOLERANCE
    return expected == actual

def validate_platform(platform_name, answer_key):
    """Validate platform results against answer key, return dict of scale_id -> {field -> {expected, actual, match}}"""
    results_path = TEST_RESULTS_DIR / f'{platform_name}-results.json'
    if not results_path.exists():
        return None
    
    results = load_json(results_path)
    actual_by_id = {s['ScaleID']: s for s in results.get('scales', [])}
    
    # Only validate projected scales
    projected_scales = [s for s in answer_key.get('scales', []) if s.get('IsProjected', False)]
    
    validation = {}
    fields = ['Scale', 'ScaleFactorPower', 'LogScale', 'LogMeasure']
    
    for expected in projected_scales:
        scale_id = expected['ScaleID']
        actual = actual_by_id.get(scale_id)
        
        field_results = {}
        all_match = True
        
        for field in fields:
            exp_val = expected.get(field)
            act_val = actual.get(field) if actual else None
            match = compare_values(exp_val, act_val)
            
            field_results[field] = {
                'expected': exp_val,
                'actual': act_val,
                'match': match
            }
            if not match:
                all_match = False
        
        validation[scale_id] = {
            'fields': field_results,
            'all_match': all_match,
            'missing': actual is None
        }
    
    return validation

def generate_report():
    """Generate comprehensive HTML report with validation"""
    
    # Load all data
    base_data = load_json(TEST_DATA_DIR / 'base-data.json')
    answer_key = load_json(TEST_DATA_DIR / 'answer-key.json')
    
    systems = base_data.get('systems', [])
    all_scales = answer_key.get('scales', [])
    
    # Validate all platforms
    platform_names = ['python', 'postgres', 'golang']
    platform_validations = {}
    platform_summaries = {}
    
    for name in platform_names:
        validation = validate_platform(name, answer_key)
        platform_validations[name] = validation
        
        if validation:
            pass_count = sum(1 for v in validation.values() if v['all_match'])
            fail_count = sum(1 for v in validation.values() if not v['all_match'])
            platform_summaries[name] = {'pass': pass_count, 'fail': fail_count, 'status': 'passed' if fail_count == 0 else 'failed'}
        else:
            platform_summaries[name] = {'pass': 0, 'fail': 0, 'status': 'not_run'}
    
    # Group scales by system
    scales_by_system = {}
    for s in all_scales:
        sys_id = s['System']
        if sys_id not in scales_by_system:
            scales_by_system[sys_id] = []
        scales_by_system[sys_id].append(s)
    
    system_lookup = {s['SystemID']: s for s in systems}
    
    # Build chart data JSON
    chart_data = {}
    for sys_id, sys_scales in scales_by_system.items():
        sorted_scales = sorted(sys_scales, key=lambda x: x.get('Iteration', 0))
        system_info = system_lookup.get(sys_id, {})
        
        actual = []
        projected = []
        for s in sorted_scales:
            pt = {'x': s.get('LogScale', 0), 'y': s.get('LogMeasure', 0), 'iter': s.get('Iteration', 0)}
            if s.get('IsProjected', False):
                projected.append(pt)
            else:
                actual.append(pt)
        
        chart_data[sys_id] = {
            'actual': actual,
            'projected': projected,
            'slope': system_info.get('TheoreticalLogLogSlope', 0),
            'name': system_info.get('DisplayName', sys_id)
        }
    
    # Count total failures
    total_failures = sum(s['fail'] for s in platform_summaries.values())
    all_passed = total_failures == 0
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Power Laws & Fractals - Test Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --muted: #8b949e;
            --green: #3fb950;
            --red: #f85149;
            --purple: #a371f7;
            --blue: #58a6ff;
            --yellow: #d29922;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'JetBrains Mono', 'SF Mono', monospace;
            background: var(--bg);
            color: var(--text);
            padding: 2rem;
            line-height: 1.5;
        }}
        .container {{ max-width: 1800px; margin: 0 auto; }}
        
        header {{
            text-align: center;
            padding: 2rem;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, rgba(88,166,255,0.1), rgba(163,113,247,0.1));
            border-radius: 12px;
            border: 1px solid var(--border);
        }}
        h1 {{
            font-size: 2.5rem;
            background: linear-gradient(135deg, var(--blue), var(--purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .timestamp {{ color: var(--muted); font-size: 0.875rem; }}
        
        .status-banner {{
            padding: 1rem 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
            font-size: 1.25rem;
            font-weight: 600;
            text-align: center;
        }}
        .status-banner.passed {{
            background: rgba(63, 185, 80, 0.2);
            border: 2px solid var(--green);
            color: var(--green);
        }}
        .status-banner.failed {{
            background: rgba(248, 81, 73, 0.2);
            border: 2px solid var(--red);
            color: var(--red);
        }}
        
        .platform-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .platform-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1.5rem;
            text-align: center;
        }}
        .platform-card.passed {{ border-left: 4px solid var(--green); }}
        .platform-card.failed {{ border-left: 4px solid var(--red); }}
        .platform-card.not_run {{ border-left: 4px solid var(--muted); opacity: 0.6; }}
        .platform-name {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
        .platform-status {{ font-size: 0.875rem; font-weight: 600; }}
        .platform-status.passed {{ color: var(--green); }}
        .platform-status.failed {{ color: var(--red); }}
        .platform-counts {{ margin-top: 0.5rem; color: var(--muted); font-size: 0.8rem; }}
        
        .system {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }}
        .system-header {{
            display: flex;
            align-items: center;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .system-icon {{ font-size: 2rem; }}
        .system-name {{ font-size: 1.5rem; font-weight: 600; }}
        .system-badge {{
            background: var(--bg);
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.75rem;
            color: var(--muted);
        }}
        
        .system-content {{
            display: grid;
            grid-template-columns: 1fr 450px;
            gap: 2rem;
        }}
        @media (max-width: 1200px) {{
            .system-content {{ grid-template-columns: 1fr; }}
            .platform-grid {{ grid-template-columns: 1fr; }}
        }}
        
        .chart-container {{
            background: var(--bg);
            border-radius: 8px;
            padding: 1rem;
            height: 350px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.75rem;
        }}
        th, td {{
            padding: 0.4rem 0.5rem;
            text-align: right;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            color: var(--muted);
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.65rem;
            position: sticky;
            top: 0;
            background: var(--card);
        }}
        th:first-child, td:first-child {{ text-align: center; }}
        tr:hover {{ background: rgba(255,255,255,0.03); }}
        
        .row-actual {{ color: var(--green); }}
        .row-projected {{ color: var(--purple); }}
        .row-marker {{ font-size: 0.9rem; }}
        
        .val-match {{ color: var(--green); }}
        .val-fail {{ color: var(--red); font-weight: 700; background: rgba(248,81,73,0.15); }}
        .val-missing {{ color: var(--muted); font-style: italic; }}
        
        .validation-section {{
            margin-top: 1.5rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border);
        }}
        .validation-title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: var(--blue);
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            color: var(--muted);
            border-top: 1px solid var(--border);
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔺 Power Laws & Fractals</h1>
            <p>Cross-Platform Validation Report</p>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>
        
        <div class="status-banner {'passed' if all_passed else 'failed'}">
            {'✓ ALL PLATFORMS PASSED' if all_passed else f'✗ {total_failures} VALIDATION FAILURES'}
        </div>
        
        <div class="platform-grid">
'''
    
    platform_icons = {'python': '🐍', 'postgres': '🐘', 'golang': '🐹'}
    platform_display = {'python': 'Python', 'postgres': 'PostgreSQL', 'golang': 'Go'}
    
    for name in platform_names:
        summary = platform_summaries[name]
        status = summary['status']
        icon = platform_icons[name]
        display = platform_display[name]
        
        html += f'''            <div class="platform-card {status}">
                <div class="platform-name">{icon} {display}</div>
                <div class="platform-status {status}">{'✓ PASSED' if status == 'passed' else ('✗ FAILED' if status == 'failed' else '○ NOT RUN')}</div>
                <div class="platform-counts">{summary['pass']} passed, {summary['fail']} failed</div>
            </div>
'''
    
    html += '''        </div>
'''
    
    # Generate each system section with validation
    for sys_id in sorted(scales_by_system.keys()):
        sys_scales = sorted(scales_by_system[sys_id], key=lambda x: x.get('Iteration', 0))
        system = system_lookup.get(sys_id, {})
        
        icon = '🔺' if system.get('Class') == 'fractal' else '📈'
        type_label = 'Fractal' if system.get('Class') == 'fractal' else 'Power Law'
        slope = system.get('TheoreticalLogLogSlope', 0)
        
        # Check for any failures in this system
        system_has_failures = False
        for s in sys_scales:
            if s.get('IsProjected', False):
                for name in platform_names:
                    v = platform_validations.get(name, {})
                    if v and s['ScaleID'] in v and not v[s['ScaleID']]['all_match']:
                        system_has_failures = True
                        break
        
        html += f'''
        <div class="system" style="{'border-left: 4px solid var(--red);' if system_has_failures else ''}">
            <div class="system-header">
                <span class="system-icon">{icon}</span>
                <span class="system-name">{system.get('DisplayName', sys_id)}</span>
                <span class="system-badge">{type_label}</span>
                <span class="system-badge">Slope: {slope}</span>
                {'<span class="system-badge" style="background: var(--red); color: white;">⚠ HAS FAILURES</span>' if system_has_failures else ''}
            </div>
            
            <div class="system-content">
                <div>
                    <table>
                        <thead>
                            <tr>
                                <th></th>
                                <th>Iter</th>
                                <th>Measure</th>
                                <th>Scale</th>
                                <th>log(Scale)</th>
                                <th>log(Measure)</th>
                                <th>🐍 Py</th>
                                <th>🐘 PG</th>
                                <th>🐹 Go</th>
                            </tr>
                        </thead>
                        <tbody>
'''
        
        # Show ALL scales (actual + projected)
        for s in sys_scales:
            scale_id = s['ScaleID']
            iteration = s.get('Iteration', 0)
            is_projected = s.get('IsProjected', False)
            
            row_class = 'row-projected' if is_projected else 'row-actual'
            marker = '◌' if is_projected else '●'
            
            html += f'''                            <tr class="{row_class}">
                                <td class="row-marker">{marker}</td>
                                <td>{iteration}</td>
                                <td>{s.get('Measure', 0):.6f}</td>
                                <td>{s.get('Scale', 0):.6f}</td>
                                <td>{s.get('LogScale', 0):.6f}</td>
                                <td>{s.get('LogMeasure', 0):.6f}</td>
'''
            
            # Show platform validation only for projected scales
            if is_projected:
                for name in platform_names:
                    v = platform_validations.get(name, {})
                    if v and scale_id in v:
                        scale_v = v[scale_id]
                        if scale_v['missing']:
                            html += '                                <td class="val-missing">MISSING</td>\n'
                        else:
                            lm = scale_v['fields'].get('LogMeasure', {})
                            actual = lm.get('actual')
                            match = lm.get('match', False)
                            css_class = 'val-match' if match else 'val-fail'
                            val_str = f"{actual:.6f}" if actual is not None else "-"
                            html += f'                                <td class="{css_class}">{val_str}</td>\n'
                    else:
                        html += '                                <td class="val-missing">-</td>\n'
            else:
                # Actual scales (0-3) - no platform validation, just show dashes
                html += '                                <td class="val-missing">-</td>\n'
                html += '                                <td class="val-missing">-</td>\n'
                html += '                                <td class="val-missing">-</td>\n'
            
            html += '                            </tr>\n'
        
        html += f'''                        </tbody>
                    </table>
                </div>
                <div class="chart-container">
                    <canvas id="chart-{sys_id}"></canvas>
                </div>
            </div>
        </div>
'''
    
    # Add JavaScript for charts
    chart_json = json.dumps(chart_data)
    html += f'''
        <footer>
            <p>🔺 Power Laws & Fractals — ERB Testing Protocol</p>
            <p>Validating {len([s for s in all_scales if s.get('IsProjected')])} projected scales across {len(systems)} systems</p>
        </footer>
    </div>
    
    <script>
        const chartData = {chart_json};
        
        Object.keys(chartData).forEach(sysId => {{
            const data = chartData[sysId];
            const canvas = document.getElementById('chart-' + sysId);
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            const all = [...data.actual, ...data.projected];
            if (all.length === 0) return;
            
            const xMin = Math.min(...all.map(p => p.x));
            const xMax = Math.max(...all.map(p => p.x));
            const first = all[0];
            
            const theory = [];
            for (let i = 0; i <= 20; i++) {{
                const x = xMin + (xMax - xMin) * i / 20;
                const y = first.y + data.slope * (x - first.x);
                theory.push({{x, y}});
            }}
            
            new Chart(ctx, {{
                type: 'scatter',
                data: {{
                    datasets: [
                        {{
                            label: 'Actual (0-3)',
                            data: data.actual,
                            backgroundColor: '#3fb950',
                            borderColor: '#3fb950',
                            pointRadius: 8,
                            pointHoverRadius: 10
                        }},
                        {{
                            label: 'Projected (4-7)',
                            data: data.projected,
                            backgroundColor: '#a371f7',
                            borderColor: '#a371f7',
                            pointRadius: 8,
                            pointHoverRadius: 10
                        }},
                        {{
                            label: 'Theoretical (slope=' + data.slope.toFixed(3) + ')',
                            data: theory,
                            type: 'line',
                            borderColor: 'rgba(139, 148, 158, 0.6)',
                            borderDash: [5, 5],
                            borderWidth: 2,
                            pointRadius: 0,
                            fill: false
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{
                            position: 'bottom',
                            labels: {{ color: '#c9d1d9', font: {{ size: 10 }} }}
                        }},
                        title: {{
                            display: true,
                            text: data.name + ' - Log-Log Plot',
                            color: '#c9d1d9',
                            font: {{ size: 13 }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{ display: true, text: 'log(Scale)', color: '#8b949e' }},
                            ticks: {{ color: '#8b949e' }},
                            grid: {{ color: '#30363d' }}
                        }},
                        y: {{
                            title: {{ display: true, text: 'log(Measure)', color: '#8b949e' }},
                            ticks: {{ color: '#8b949e' }},
                            grid: {{ color: '#30363d' }}
                        }}
                    }}
                }}
            }});
        }});
    </script>
</body>
</html>
'''
    
    # Write report
    report_path = SCRIPT_DIR / 'report.html'
    with open(report_path, 'w') as f:
        f.write(html)
    
    # Print summary to console
    print(f"✓ Report generated: {report_path}")
    if not all_passed:
        print(f"\n⚠ VALIDATION FAILURES DETECTED:")
        for name in platform_names:
            v = platform_validations.get(name)
            if v:
                failures = [sid for sid, data in v.items() if not data['all_match']]
                if failures:
                    print(f"  {name}: {len(failures)} failures")
                    for sid in failures[:3]:
                        print(f"    • {sid}")
                    if len(failures) > 3:
                        print(f"    ... and {len(failures) - 3} more")
    
    return report_path


if __name__ == '__main__':
    generate_report()
