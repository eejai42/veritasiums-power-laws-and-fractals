#!/usr/bin/env python3
"""
Comprehensive HTML Report Generator

Generates a full data report with:
- All 8 iterations per system (actual + projected)
- Full data tables with all computed values
- Large interactive log-log charts
- System aggregates and statistics
"""

import json
from pathlib import Path
from datetime import datetime, timezone

# Paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
TEST_DATA_DIR = PROJECT_ROOT / 'test-data'
TEST_RESULTS_DIR = PROJECT_ROOT / 'test-results'

def load_json(path: Path) -> dict:
    with open(path, 'r') as f:
        return json.load(f)

def generate_report():
    """Generate comprehensive HTML report"""
    
    # Load all data
    base_data = load_json(TEST_DATA_DIR / 'base-data.json')
    answer_key = load_json(TEST_DATA_DIR / 'answer-key.json')
    
    systems = base_data.get('systems', [])
    all_scales = answer_key.get('scales', [])
    
    # Load platform results
    platforms = {}
    for name in ['python', 'postgres', 'golang']:
        path = TEST_RESULTS_DIR / f'{name}-results.json'
        if path.exists():
            platforms[name] = load_json(path)
    
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
    
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Power Laws & Fractals - Complete Results</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg: #0d1117;
            --card: #161b22;
            --border: #30363d;
            --text: #c9d1d9;
            --muted: #8b949e;
            --green: #3fb950;
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
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
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
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .summary-card {{
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }}
        .summary-value {{ font-size: 2rem; font-weight: 700; color: var(--green); }}
        .summary-label {{ color: var(--muted); font-size: 0.75rem; text-transform: uppercase; }}
        
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
        .system-stats {{
            display: flex;
            gap: 2rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}
        .stat {{ text-align: center; }}
        .stat-value {{ font-size: 1.25rem; font-weight: 600; color: var(--blue); }}
        .stat-label {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; }}
        
        .system-content {{
            display: grid;
            grid-template-columns: 1fr 500px;
            gap: 2rem;
        }}
        @media (max-width: 1200px) {{
            .system-content {{ grid-template-columns: 1fr; }}
        }}
        
        .chart-container {{
            background: var(--bg);
            border-radius: 8px;
            padding: 1rem;
            height: 400px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.8rem;
        }}
        th, td {{
            padding: 0.5rem;
            text-align: right;
            border-bottom: 1px solid var(--border);
        }}
        th {{
            color: var(--muted);
            font-weight: 500;
            text-transform: uppercase;
            font-size: 0.7rem;
        }}
        th:first-child, td:first-child {{ text-align: center; }}
        tr:hover {{ background: rgba(255,255,255,0.03); }}
        
        .row-actual {{ color: var(--green); }}
        .row-projected {{ color: var(--purple); }}
        .row-marker {{ font-size: 1rem; }}
        
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
            <p>Complete Results Report - All Computed Values</p>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>
        
        <div class="summary">
            <div class="summary-card">
                <div class="summary-value">{len(systems)}</div>
                <div class="summary-label">Systems</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{len(all_scales)}</div>
                <div class="summary-label">Total Scales</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{len([s for s in all_scales if not s.get('IsProjected')])}</div>
                <div class="summary-label">Actual (0-3)</div>
            </div>
            <div class="summary-card">
                <div class="summary-value">{len([s for s in all_scales if s.get('IsProjected')])}</div>
                <div class="summary-label">Projected (4-7)</div>
            </div>
        </div>
'''
    
    # Generate each system section
    for sys_id in sorted(scales_by_system.keys()):
        sys_scales = sorted(scales_by_system[sys_id], key=lambda x: x.get('Iteration', 0))
        system = system_lookup.get(sys_id, {})
        
        icon = '🔺' if system.get('Class') == 'fractal' else '📈'
        type_label = 'Fractal' if system.get('Class') == 'fractal' else 'Power Law'
        slope = system.get('TheoreticalLogLogSlope', 0)
        
        # Calculate aggregates
        measures = [s.get('Measure', 0) for s in sys_scales]
        log_measures = [s.get('LogMeasure', 0) for s in sys_scales]
        log_scales = [s.get('LogScale', 0) for s in sys_scales]
        
        html += f'''
        <div class="system">
            <div class="system-header">
                <span class="system-icon">{icon}</span>
                <span class="system-name">{system.get('DisplayName', sys_id)}</span>
                <span class="system-badge">{type_label}</span>
                <span class="system-badge">Slope: {slope}</span>
                <span class="system-badge">Base: {system.get('BaseScale', 1)} × {system.get('ScaleFactor', 1)}^n</span>
            </div>
            
            <div class="system-stats">
                <div class="stat">
                    <div class="stat-value">{len(sys_scales)}</div>
                    <div class="stat-label">Iterations</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{min(measures):.4f}</div>
                    <div class="stat-label">Min Measure</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{max(measures):.4f}</div>
                    <div class="stat-label">Max Measure</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{min(log_scales):.2f}</div>
                    <div class="stat-label">Min log(Scale)</div>
                </div>
                <div class="stat">
                    <div class="stat-value">{max(log_scales):.2f}</div>
                    <div class="stat-label">Max log(Scale)</div>
                </div>
            </div>
            
            <div class="system-content">
                <table>
                    <thead>
                        <tr>
                            <th></th>
                            <th>Iter</th>
                            <th>Measure</th>
                            <th>Scale</th>
                            <th>ScaleFactorPower</th>
                            <th>log(Scale)</th>
                            <th>log(Measure)</th>
                        </tr>
                    </thead>
                    <tbody>
'''
        
        for s in sys_scales:
            is_proj = s.get('IsProjected', False)
            row_class = 'row-projected' if is_proj else 'row-actual'
            marker = '◌' if is_proj else '●'
            
            html += f'''                        <tr class="{row_class}">
                            <td class="row-marker">{marker}</td>
                            <td>{s.get('Iteration', 0)}</td>
                            <td>{s.get('Measure', 0):.6f}</td>
                            <td>{s.get('Scale', 0):.8f}</td>
                            <td>{s.get('ScaleFactorPower', 0):.8f}</td>
                            <td>{s.get('LogScale', 0):.6f}</td>
                            <td>{s.get('LogMeasure', 0):.6f}</td>
                        </tr>
'''
        
        html += f'''                    </tbody>
                </table>
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
            <p>● Actual Data (iterations 0-3) &nbsp;&nbsp; ◌ Projected Data (iterations 4-7)</p>
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
                            pointRadius: 10,
                            pointHoverRadius: 12
                        }},
                        {{
                            label: 'Projected (4-7)',
                            data: data.projected,
                            backgroundColor: '#a371f7',
                            borderColor: '#a371f7',
                            pointRadius: 10,
                            pointHoverRadius: 12
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
                            labels: {{ color: '#c9d1d9', font: {{ size: 11 }} }}
                        }},
                        title: {{
                            display: true,
                            text: data.name + ' - Log-Log Plot',
                            color: '#c9d1d9',
                            font: {{ size: 14 }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    const pt = ctx.raw;
                                    if (pt.iter !== undefined) {{
                                        return 'Iter ' + pt.iter + ': (' + pt.x.toFixed(3) + ', ' + pt.y.toFixed(3) + ')';
                                    }}
                                    return '(' + pt.x.toFixed(3) + ', ' + pt.y.toFixed(3) + ')';
                                }}
                            }}
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
    
    print(f"✓ Report generated: {report_path}")
    return report_path


if __name__ == '__main__':
    generate_report()

