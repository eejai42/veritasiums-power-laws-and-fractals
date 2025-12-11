# Power Laws and Fractals Analysis Engine

A multi-platform analytical framework for modeling, analyzing, and visualizing fractal systems and power-law distributions.

## 🚀 Quick Start

```bash
./start.sh
```

That's it! Pick from Python, PostgreSQL, Jupyter, Go, or the HTML visualizer.

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Start here to continue development
- **[PROGRESS.md](PROGRESS.md)** - Current status and completed work
- **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Technical architecture

## 📊 Current Status

| Platform | Status | Location | Generator |
|----------|--------|----------|-----------|
| **PostgreSQL** | ✅ COMPLETE | [postgres/](postgres/) | External tool |
| **Python** | ✅ COMPLETE | [python/rulebook/](python/rulebook/) | [rulebook-to-python.py](python/rulebook-to-python.py) |
| **Golang** | 📋 Planned | [golang/](golang/) | To be built |
| **Visualizer** | 📋 Planned | [visualizer/](visualizer/) | To be built |
| **Jupyter** | 📋 Planned | [jupyter/](jupyter/) | To be built |

**Meta-Programming Approach**: One canonical rulebook → Multiple platform-specific implementations via code generators.

## Overview

This project implements a computational engine for analyzing systems that exhibit power-law behavior and fractal characteristics. Inspired by concepts from the Veritasium video on power laws and fractals, it provides tools to:

- Define fractal and power-law systems with consistent parameters
- Calculate scale relationships across multiple iterations
- Perform log-log analysis to validate theoretical predictions
- Visualize scaling behavior and self-similarity patterns
- Compare empirical measurements against theoretical models

## What is the Rulebook?

The **rulebook** is a standardized data model that defines how to represent and analyze self-similar systems. It consists of three core components:

### 1. Systems Table
Defines the fundamental properties of each fractal or power-law system:

- **SystemID**: Unique identifier (e.g., "Sierpinski", "Koch", "ZipfWords")
- **DisplayName**: Human-readable name
- **Class**: Type of system ("fractal" or "power_law")
- **BaseScale**: Starting scale/size at iteration 0
- **ScaleFactor**: Multiplicative factor between iterations
- **MeasureName**: What is being measured (e.g., "black_triangle_count", "edge_length_total")
- **FractalDimension**: For fractals, the Hausdorff dimension
- **TheoreticalLogLogSlope**: Expected slope on log-log plot

### 2. Scales Table
Records measurements at each iteration/scale of a system:

- **ScaleID**: Unique identifier for each measurement point
- **System**: Reference to parent system
- **Iteration**: Which iteration/generation (0, 1, 2, 3, ...)
- **Measure**: The actual measurement value
- **Calculated Fields**:
  - ScaleFactorPower: Scale factor raised to iteration power
  - Scale: Actual scale at this iteration
  - LogScale: Log₁₀ of the scale
  - LogMeasure: Log₁₀ of the measurement

### 3. System Stats Table
Aggregates statistical analysis for each system:

- **SystemStatsID**: Unique identifier
- **System**: Reference to parent system
- **AnalysisName**: Name of this analysis run
- **Status**: Validation status ("validated", "pending", etc.)
- **Calculated Aggregations**:
  - PointCount: Number of data points
  - MinLogScale, MaxLogScale: Range of log scales
  - MinLogMeasure, MaxLogMeasure: Range of log measurements
  - DeltaLogMeasure, DeltaLogScale: Differences for slope calculation
  - EmpiricalLogLogSlope: Measured slope from data
  - SlopeError: Difference between empirical and theoretical slopes

## Example Systems in the Rulebook

The current implementation includes four classic examples:

### 1. Sierpinski Triangle
- **Class**: Fractal
- **Measure**: Count of black triangles
- **Fractal Dimension**: 1.585
- **Behavior**: At each iteration, each triangle subdivides into 3 smaller triangles
- **Theoretical Slope**: -1.585

### 2. Koch Snowflake
- **Class**: Fractal
- **Measure**: Total edge length
- **Fractal Dimension**: 1.262
- **Behavior**: Each edge segment is replaced by 4 segments at 1/3 the length
- **Theoretical Slope**: -0.262

### 3. Zipf's Law (Word Frequencies)
- **Class**: Power Law
- **Measure**: Relative frequency
- **Behavior**: Word frequency inversely proportional to rank
- **Theoretical Slope**: -1.0

### 4. Scale-Free Networks
- **Class**: Power Law
- **Measure**: Node count at each degree
- **Behavior**: Degree distribution follows power law
- **Theoretical Slope**: -2.5

## Project Status

### Completed Modules

#### PostgreSQL Implementation (rulebook-to-postgres)
A fully functional, spreadsheet-like PostgreSQL database that implements the complete engine.

**Features:**
- Normalized schema with separate tables for raw data
- Calculation functions for all derived fields
- Views that present spreadsheet-like calculated columns
- Support for lookup, calculated, and aggregation field types
- Row-level security policies
- Automatic validation of theoretical vs. empirical slopes

**Files:**
- [postgres/01-drop-and-create-tables.sql](postgres/01-drop-and-create-tables.sql) - Schema definition
- [postgres/02-create-functions.sql](postgres/02-create-functions.sql) - Calculation functions
- [postgres/03-create-views.sql](postgres/03-create-views.sql) - Spreadsheet-like views
- [postgres/04-create-policies.sql](postgres/04-create-policies.sql) - Security policies
- [postgres/05-insert-data.sql](postgres/05-insert-data.sql) - Sample data

## Planned Modules

### Python SDK (rulebook-to-python)
A Python implementation providing:
- Object-oriented API for defining and analyzing systems
- NumPy-based calculations for performance
- Pandas DataFrames for data manipulation
- Matplotlib/Plotly integration for visualization
- Export to various formats (CSV, JSON, Excel)

**Status**: Planned

**Directory**: [python/](python/)

### Golang SDK (rulebook-to-golang)
A Go implementation providing:
- Type-safe system definitions
- Concurrent calculation engine
- REST API for system queries
- gRPC support for inter-service communication
- High-performance batch processing

**Status**: Planned

**Directory**: TBD (to be created)

### Visualizer
An interactive visualization tool for exploring fractal and power-law systems:
- Log-log plot generation
- Interactive scaling controls
- Side-by-side system comparison
- Animation of fractal generation
- Export of publication-ready figures

**Status**: Planned

**Technologies**: D3.js, React, or Observable
**Directory**: TBD (to be created)

### Jupyter Notebook (rulebook-to-jupyter)
Educational Jupyter notebooks demonstrating:
- Step-by-step construction of fractal systems
- Interactive parameter exploration
- Real-time log-log plotting
- Integration with Python SDK
- Example analyses and tutorials

**Status**: Planned

**Directory**: TBD (to be created)

## Future Possibilities

- **Additional Systems**: Mandelbrot set, Cantor set, Pareto distributions, city size distributions
- **3D Fractals**: Extension to 3D systems (Menger sponge, etc.)
- **Real-world Data**: Integration with actual datasets (earthquake magnitudes, wealth distribution)
- **Machine Learning**: Pattern recognition in power-law systems
- **Web API**: RESTful service for system analysis
- **Mobile App**: iOS/Android visualization tools

## Core Concepts

### Log-Log Analysis
The engine performs log-log analysis to validate power-law and fractal behavior:

1. Measure values at different scales (iterations)
2. Take log₁₀ of both scale and measure
3. Plot LogMeasure vs. LogScale
4. Calculate slope using: `(MaxLogMeasure - MinLogMeasure) / (MaxLogScale - MinLogScale)`
5. Compare empirical slope to theoretical prediction

For a perfect power law or fractal, points on a log-log plot form a straight line. The slope reveals the scaling exponent.

### Field Type System
The rulebook supports three field types:

1. **Raw Fields**: Direct data storage (Iteration, Measure, SystemID)
2. **Lookup Fields**: Values from related tables (BaseScale from Systems)
3. **Calculated Fields**: Derived from other fields using formulas (LogScale = LOG10(Scale))
4. **Aggregation Fields**: Rollups across multiple rows (PointCount, MinLogScale)

## Getting Started

### PostgreSQL Implementation

1. Ensure PostgreSQL is installed and running
2. Create a new database
3. Run the SQL scripts in order:
```bash
psql -d your_database -f postgres/01-drop-and-create-tables.sql
psql -d your_database -f postgres/02-create-functions.sql
psql -d your_database -f postgres/03-create-views.sql
psql -d your_database -f postgres/04-create-policies.sql
psql -d your_database -f postgres/05-insert-data.sql
```

4. Query the views to see calculated results:
```sql
SELECT * FROM vw_scales;
SELECT * FROM vw_system_stats;
```

### Python SDK (Coming Soon)
```python
from rulebook import System, Scale

# Define a system
sierpinski = System(
    system_id="Sierpinski",
    display_name="Sierpinski Triangle",
    base_scale=1.0,
    scale_factor=0.5,
    fractal_dimension=1.585
)

# Add measurements
sierpinski.add_scale(iteration=0, measure=1.0)
sierpinski.add_scale(iteration=1, measure=3.0)
sierpinski.add_scale(iteration=2, measure=9.0)

# Analyze
stats = sierpinski.analyze()
print(f"Empirical slope: {stats.empirical_slope}")
print(f"Theoretical slope: {stats.theoretical_slope}")
print(f"Error: {stats.slope_error}")
```

## Architecture Principles

Each implementation follows these principles:

1. **Separation of Concerns**: Raw data storage separate from calculations
2. **Formula Preservation**: Original Excel-like formulas documented in code
3. **Type Safety**: Proper typing for all fields and calculations
4. **Validation**: Automatic comparison of empirical vs. theoretical results
5. **Extensibility**: Easy to add new systems and measurement types

## Contributing

This is an educational and research project. Contributions are welcome for:

- New system implementations
- Additional calculation methods
- Visualization improvements
- Documentation and tutorials
- Bug fixes and optimizations

## References

- [Veritasium - The Surprising Reason Why Power Laws Are Everywhere](https://www.youtube.com/watch?v=3PdBZiHHHoQ)
- Mandelbrot, B. (1982). The Fractal Geometry of Nature
- Barabási, A-L. (2016). Network Science
- Newman, M. (2005). Power laws, Pareto distributions and Zipf's law

## License

MIT License - See LICENSE file for details

## Project Structure

```
ERB_veritasium-power-laws-and-fractals/
├── README.md                    # This file
├── postgres/                    # PostgreSQL implementation (COMPLETE)
│   ├── README.md               # Generation report
│   ├── 01-drop-and-create-tables.sql
│   ├── 02-create-functions.sql
│   ├── 03-create-views.sql
│   ├── 04-create-policies.sql
│   └── 05-insert-data.sql
├── python/                      # Python SDK (PLANNED)
│   └── rulebook-to-python.py   # Placeholder
├── golang/                      # Golang SDK (PLANNED)
├── visualizer/                  # Interactive visualizer (PLANNED)
└── jupyter/                     # Jupyter notebooks (PLANNED)
```
