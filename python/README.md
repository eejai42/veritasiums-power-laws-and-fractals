# Python SDK - Rulebook to Python

A Python implementation of the Power Laws and Fractals analysis engine.

## Status: Planned

## Overview

This module will provide a Pythonic API for working with fractal and power-law systems, built on the same rulebook data model as the PostgreSQL implementation.

## Planned Features

### Core Components

1. **System Class**: Object-oriented representation of fractal/power-law systems
2. **Scale Class**: Measurement points with automatic calculation support
3. **Stats Class**: Statistical analysis and validation
4. **Rulebook Parser**: Import/export systems from various formats

### Calculation Engine

- NumPy-based mathematical operations
- Automatic field dependency resolution
- Lazy evaluation for performance
- Vectorized operations for batch processing

### Data Manipulation

- Pandas DataFrames for tabular data
- Easy filtering, grouping, and aggregation
- Export to CSV, JSON, Excel formats
- Import from existing rulebook sources

### Visualization

- Matplotlib integration for static plots
- Plotly support for interactive visualizations
- Log-log plot generation
- Fractal rendering and animation
- Multi-system comparison charts

## Planned API

```python
from rulebook import System, Scale, analyze

# Define a system
sierpinski = System(
    system_id="Sierpinski",
    display_name="Sierpinski Triangle",
    class_type="fractal",
    base_scale=1.0,
    scale_factor=0.5,
    measure_name="black_triangle_count",
    fractal_dimension=1.585,
    theoretical_log_log_slope=-1.585
)

# Add measurement points
sierpinski.add_scale(iteration=0, measure=1.0)
sierpinski.add_scale(iteration=1, measure=3.0)
sierpinski.add_scale(iteration=2, measure=9.0)
sierpinski.add_scale(iteration=3, measure=27.0)

# Calculate derived fields
for scale in sierpinski.scales:
    print(f"Iteration {scale.iteration}: "
          f"Scale={scale.scale:.4f}, "
          f"LogScale={scale.log_scale:.4f}, "
          f"LogMeasure={scale.log_measure:.4f}")

# Perform statistical analysis
stats = sierpinski.analyze()
print(f"Empirical slope: {stats.empirical_log_log_slope:.4f}")
print(f"Theoretical slope: {stats.theoretical_log_log_slope:.4f}")
print(f"Slope error: {stats.slope_error:.6f}")

# Visualize
sierpinski.plot_log_log()

# Export to various formats
sierpinski.to_csv("sierpinski.csv")
sierpinski.to_json("sierpinski.json")
```

## Planned Dependencies

- Python 3.8+
- NumPy: Numerical operations
- Pandas: Data manipulation
- Matplotlib: Static visualization
- Plotly: Interactive visualization
- Pydantic: Data validation

## Planned Directory Structure

```
python/
├── README.md                    # This file
├── rulebook-to-python.py        # Placeholder/future converter
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
├── rulebook/                    # Main package
│   ├── __init__.py
│   ├── system.py               # System class
│   ├── scale.py                # Scale class
│   ├── stats.py                # Stats class
│   ├── calculations.py         # Field calculation engine
│   ├── parser.py               # Rulebook import/export
│   └── visualize.py            # Plotting utilities
├── examples/                    # Example scripts
│   ├── sierpinski.py
│   ├── koch.py
│   ├── zipf.py
│   └── scale_free_network.py
└── tests/                       # Unit tests
    ├── test_system.py
    ├── test_scale.py
    └── test_calculations.py
```

## Implementation Plan

1. Core data structures (System, Scale, Stats classes)
2. Field calculation engine
3. Statistical analysis functions
4. Data import/export
5. Visualization utilities
6. Documentation and examples
7. Unit tests
8. Package distribution

## Future Enhancements

- Integration with SciPy for advanced statistics
- 3D fractal support using Mayavi
- Real-time animation of fractal generation
- Machine learning for pattern detection
- REST API wrapper using FastAPI
