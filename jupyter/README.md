# Jupyter Notebooks - Interactive Learning and Analysis

Educational Jupyter notebooks for exploring power laws and fractals.

## Status: Planned

## Overview

This module will provide interactive Jupyter notebooks that combine executable code, visualizations, and explanatory text to teach and demonstrate fractal and power-law concepts.

## Planned Features

### Educational Content

1. **Introduction to Fractals**: Basic concepts and examples
2. **Power Laws in Nature**: Real-world applications
3. **Log-Log Analysis**: Understanding scaling relationships
4. **Interactive Exploration**: Parameter manipulation
5. **Advanced Topics**: Multifractals, critical phenomena

### Interactive Elements

- Live code cells with immediate feedback
- Interactive widgets (sliders, dropdowns)
- Real-time plot updates
- Step-by-step animations
- Guided exercises with solutions

### Data Analysis

- Load and analyze custom datasets
- Statistical validation
- Comparison with theoretical predictions
- Export results and figures

## Planned Notebooks

### 1. Introduction to Fractals

```markdown
# Introduction to Fractals

## What is a Fractal?

A fractal is a geometric shape that exhibits self-similarity at different scales.

## The Sierpinski Triangle

Let's build a Sierpinski triangle step by step...
```

```python
import numpy as np
import matplotlib.pyplot as plt
from rulebook import System

# Create Sierpinski system
sierpinski = System(
    system_id="Sierpinski",
    display_name="Sierpinski Triangle",
    base_scale=1.0,
    scale_factor=0.5,
    fractal_dimension=1.585
)

# Add data points
for i in range(8):
    measure = 3 ** i
    sierpinski.add_scale(iteration=i, measure=measure)

# Visualize
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot 1: Direct relationship
iterations = [s.iteration for s in sierpinski.scales]
measures = [s.measure for s in sierpinski.scales]
ax1.plot(iterations, measures, 'o-')
ax1.set_xlabel('Iteration')
ax1.set_ylabel('Number of Triangles')
ax1.set_title('Direct Plot')

# Plot 2: Log-log relationship
log_scales = [s.log_scale for s in sierpinski.scales]
log_measures = [s.log_measure for s in sierpinski.scales]
ax2.plot(log_scales, log_measures, 'o-')
ax2.set_xlabel('log₁₀(Scale)')
ax2.set_ylabel('log₁₀(Measure)')
ax2.set_title('Log-Log Plot')

plt.tight_layout()
plt.show()
```

### 2. Interactive Parameter Exploration

```python
from ipywidgets import interact, FloatSlider
import matplotlib.pyplot as plt

@interact(
    base_scale=FloatSlider(min=0.1, max=10, step=0.1, value=1.0),
    scale_factor=FloatSlider(min=0.1, max=0.9, step=0.05, value=0.5)
)
def explore_fractal(base_scale, scale_factor):
    """Interactive fractal parameter exploration"""
    system = System(
        system_id="Custom",
        base_scale=base_scale,
        scale_factor=scale_factor
    )

    # Generate scales
    for i in range(8):
        measure = (1/scale_factor) ** i
        system.add_scale(iteration=i, measure=measure)

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    x = [s.log_scale for s in system.scales]
    y = [s.log_measure for s in system.scales]
    ax.plot(x, y, 'o-')
    ax.set_xlabel('log₁₀(Scale)')
    ax.set_ylabel('log₁₀(Measure)')
    ax.set_title(f'Base={base_scale:.1f}, Factor={scale_factor:.2f}')
    ax.grid(True, alpha=0.3)
    plt.show()

    # Show statistics
    stats = system.analyze()
    print(f"Empirical slope: {stats.empirical_log_log_slope:.4f}")
```

### 3. Real-World Power Laws

```markdown
# Power Laws in the Real World

Power laws appear throughout nature and society:

1. **City Sizes**: Population follows Zipf's law
2. **Earthquake Magnitudes**: Gutenberg-Richter law
3. **Word Frequencies**: Zipf's law in language
4. **Network Connectivity**: Scale-free networks
5. **Wealth Distribution**: Pareto principle

Let's analyze real data...
```

```python
import pandas as pd

# Load real earthquake data
earthquakes = pd.read_csv('earthquakes.csv')

# Create power law system
earthquake_system = System(
    system_id="Earthquakes",
    display_name="Earthquake Magnitudes",
    class_type="power_law"
)

# Analyze magnitude distribution
magnitude_counts = earthquakes.groupby('magnitude').size()
for mag, count in magnitude_counts.items():
    earthquake_system.add_scale(iteration=int(mag), measure=count)

# Validate power law
stats = earthquake_system.analyze()
print(f"Power law exponent: {stats.empirical_log_log_slope:.2f}")

# Visualize
earthquake_system.plot_log_log(
    title="Earthquake Magnitude Distribution",
    xlabel="log₁₀(Magnitude)",
    ylabel="log₁₀(Frequency)"
)
```

## Planned Notebooks List

1. **01-introduction-to-fractals.ipynb**: Basic concepts and Sierpinski triangle
2. **02-koch-snowflake.ipynb**: Koch snowflake construction and analysis
3. **03-log-log-analysis.ipynb**: Understanding log-log plots
4. **04-interactive-exploration.ipynb**: Parameter exploration with widgets
5. **05-zipf-law.ipynb**: Word frequency and Zipf's law
6. **06-scale-free-networks.ipynb**: Network degree distributions
7. **07-custom-systems.ipynb**: Creating your own fractal systems
8. **08-3d-fractals.ipynb**: Menger sponge and 3D fractals
9. **09-real-world-data.ipynb**: Analyzing actual power-law datasets
10. **10-advanced-topics.ipynb**: Multifractals and critical phenomena

## Planned Directory Structure

```
jupyter/
├── README.md                           # This file
├── power-laws-and-fractals.ipynb      # Main notebook (placeholder)
├── notebooks/                          # Individual notebooks
│   ├── 01-introduction-to-fractals.ipynb
│   ├── 02-koch-snowflake.ipynb
│   ├── 03-log-log-analysis.ipynb
│   ├── 04-interactive-exploration.ipynb
│   ├── 05-zipf-law.ipynb
│   ├── 06-scale-free-networks.ipynb
│   ├── 07-custom-systems.ipynb
│   ├── 08-3d-fractals.ipynb
│   ├── 09-real-world-data.ipynb
│   └── 10-advanced-topics.ipynb
├── data/                               # Sample datasets
│   ├── word_frequencies.csv
│   ├── earthquakes.csv
│   ├── city_populations.csv
│   └── network_degrees.csv
├── images/                             # Figures and diagrams
│   ├── sierpinski_steps.png
│   └── koch_construction.png
└── solutions/                          # Exercise solutions
    └── exercises.ipynb
```

## Required Dependencies

```python
# requirements.txt
numpy>=1.20.0
pandas>=1.3.0
matplotlib>=3.4.0
scipy>=1.7.0
ipywidgets>=7.6.0
plotly>=5.0.0
jupyterlab>=3.0.0
```

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install rulebook SDK
pip install -e ../python

# Launch Jupyter Lab
jupyter lab
```

## Planned Interactive Features

### 1. Widget-Based Controls

```python
from ipywidgets import interact, IntSlider

@interact(iteration=IntSlider(min=0, max=7, value=3))
def show_sierpinski(iteration):
    """Show Sierpinski triangle at specific iteration"""
    draw_sierpinski_triangle(iteration)
```

### 2. Animation

```python
from IPython.display import HTML
from matplotlib.animation import FuncAnimation

def animate_fractal():
    """Animate fractal generation"""
    fig, ax = plt.subplots()

    def update(frame):
        ax.clear()
        draw_fractal(iteration=frame)
        ax.set_title(f'Iteration {frame}')

    anim = FuncAnimation(fig, update, frames=8, interval=500)
    return HTML(anim.to_jshtml())

animate_fractal()
```

### 3. Interactive Plots

```python
import plotly.graph_objects as go

def interactive_loglog_plot(system):
    """Create interactive log-log plot"""
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[s.log_scale for s in system.scales],
        y=[s.log_measure for s in system.scales],
        mode='markers+lines',
        name='Data points',
        marker=dict(size=10)
    ))

    # Add trend line
    stats = system.analyze()
    # ... add line

    fig.update_layout(
        title='Interactive Log-Log Plot',
        xaxis_title='log₁₀(Scale)',
        yaxis_title='log₁₀(Measure)',
        hovermode='closest'
    )

    fig.show()
```

## Learning Outcomes

After completing these notebooks, users will be able to:

1. Understand what fractals are and how they exhibit self-similarity
2. Recognize power-law distributions in real-world data
3. Perform log-log analysis to validate scaling relationships
4. Calculate fractal dimensions
5. Create and analyze custom fractal systems
6. Apply these concepts to real datasets
7. Visualize and communicate findings effectively

## Future Enhancements

- Video tutorials embedded in notebooks
- Auto-graded exercises
- Integration with online courses
- Live coding sessions
- Collaborative notebooks via JupyterHub
- Export to interactive HTML
- Integration with Binder for cloud execution
