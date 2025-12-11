#!/usr/bin/env python3
"""
Rulebook to Python Generator

Reads the canonical rulebook JSON and generates Python dataclasses
with calculation methods.

Usage:
    python rulebook-to-python.py

Input:  ssot/ERB_veritasium-power-laws-and-fractals.json
Output: python/rulebook/ package with generated code
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Add parent directory to path to import generators
sys.path.insert(0, str(Path(__file__).parent.parent))

from generators.parser import RulebookParser, Table, Field
from generators.translator import FormulaTranslator, Language


class PythonGenerator:
    """Generates Python code from rulebook"""

    def __init__(self, rulebook_path: str, output_dir: str):
        self.parser = RulebookParser(rulebook_path)
        self.translator = FormulaTranslator(Language.PYTHON)
        self.output_dir = Path(output_dir)
        self.timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

    def generate(self):
        """Generate all Python code"""
        print(f"Generating Python code from {self.parser.model_name}...")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Generate files
        self._generate_init()
        self._generate_models()
        self._generate_data()
        self._generate_utils()

        print(f"✓ Generated Python package at {self.output_dir}")

    def _generate_init(self):
        """Generate __init__.py"""
        code = f'''"""
{self.parser.model_name} - Python Implementation

Auto-generated from rulebook: {self.timestamp}

This package provides Python dataclasses for analyzing fractal
and power-law systems.
"""

from .models import System, Scale, SystemStats
from .data import load_sample_data

__all__ = ['System', 'Scale', 'SystemStats', 'load_sample_data']
'''
        self._write_file('__init__.py', code)

    def _generate_models(self):
        """Generate models.py with all table classes"""
        imports = [
            "from dataclasses import dataclass, field",
            "from typing import Optional, Dict, List",
            "import math",
            ""
        ]

        code_parts = [
            self._file_header("Data Models"),
            "\n".join(imports)
        ]

        # Generate class for each table
        for table_name in self.parser.get_table_names():
            table = self.parser.get_table(table_name)
            code_parts.append(self._generate_table_class(table))

        self._write_file('models.py', '\n\n'.join(code_parts))

    def _generate_table_class(self, table: Table) -> str:
        """Generate a dataclass for a table"""
        class_name = self._to_class_name(table.name)
        raw_fields = table.get_raw_fields()
        calc_fields = table.get_calculated_fields()

        # Build class definition
        parts = []

        # Class docstring
        parts.append(f'@dataclass')
        parts.append(f'class {class_name}:')
        parts.append(f'    """')
        parts.append(f'    {table.description}')
        parts.append(f'    """')

        # Raw fields
        for f in raw_fields:
            py_type = self._get_python_type(f)
            field_name = self._to_snake_case(f.name)
            parts.append(f'    {field_name}: {py_type}')

        # Cached calculated fields (private)
        for f in calc_fields:
            py_type = self._get_python_type(f)
            field_name = self._to_snake_case(f.name)
            parts.append(f'    _{field_name}: Optional[{py_type}] = field(default=None, repr=False)')

        parts.append('')

        # Calculation methods
        calc_order = table.get_calculation_order()
        for f in calc_order:
            method = self._generate_calculation_method(f, table)
            parts.append(method)
            parts.append('')

        return '\n'.join(parts)

    def _generate_calculation_method(self, f: Field, table: Table) -> str:
        """Generate a calculation method for a field"""
        method_name = f'calculate_{self._to_snake_case(f.name)}'
        field_name = self._to_snake_case(f.name)
        return_type = self._get_python_type(f)

        # Determine required parameters based on field type
        params = ['self']
        if f.field_type == 'lookup':
            # Lookups need access to related table
            related_table = self._find_related_table(f, table)
            if related_table:
                params.append(f'{related_table}_dict: Dict[str, {self._to_class_name(related_table)}]')
        elif f.field_type == 'aggregation':
            # Aggregations need access to child table
            child_table = self._find_child_table(f)
            if child_table:
                params.append(f'{child_table}: List[{self._to_class_name(child_table)}]')

        param_str = ', '.join(params)

        # Generate method body
        body_lines = [
            f'    def {method_name}({param_str}) -> {return_type}:',
            f'        """',
            f'        {f.description}',
            f'        Formula: {f.formula}',
            f'        """',
        ]

        # Add caching logic
        body_lines.append(f'        if self._{field_name} is None:')

        # Translate formula
        context = {
            'table_name': table.name,
            'is_calculated_field': f.field_type in ['calculated', 'aggregation']
        }

        try:
            translated = self.translator.translate(f.formula, context)
            # Handle special cases for better Python code
            if f.field_type == 'aggregation':
                # Aggregation already returns the value
                body_lines.append(f'            self._{field_name} = {translated}')
            elif f.field_type == 'lookup':
                # Lookup might return None
                body_lines.append(f'            result = {translated}')
                body_lines.append(f'            self._{field_name} = result if result is not None else 0.0')
            else:
                # Regular calculation
                body_lines.append(f'            self._{field_name} = {translated}')

        except Exception as e:
            body_lines.append(f'            # Error translating formula: {e}')
            body_lines.append(f'            self._{field_name} = 0.0')

        body_lines.append(f'        return self._{field_name}')

        return '\n'.join(body_lines)

    def _generate_data(self):
        """Generate data.py with sample data loader"""
        code_parts = [
            self._file_header("Sample Data"),
            "from typing import Dict, List",
            "from .models import System, Scale, SystemStats",
            "",
            "",
            "def load_sample_data() -> Dict[str, List]:",
            "    \"\"\"Load sample data from rulebook\"\"\"",
            "    data = {}"
        ]

        # Generate data for each table
        for table_name in self.parser.get_table_names():
            table = self.parser.get_table(table_name)
            class_name = self._to_class_name(table.name)

            code_parts.append(f"")
            code_parts.append(f"    # {table.description}")
            code_parts.append(f"    data['{table_name}'] = [")

            for row in table.data:
                # Only include raw fields in constructor
                raw_fields = {f.name: row.get(f.name) for f in table.get_raw_fields() if f.name in row}

                # Convert to Python code
                field_strs = []
                for key, value in raw_fields.items():
                    snake_key = self._to_snake_case(key)
                    if value is None:
                        field_strs.append(f'{snake_key}=None')
                    elif isinstance(value, str):
                        field_strs.append(f'{snake_key}="{value}"')
                    else:
                        field_strs.append(f'{snake_key}={value}')

                code_parts.append(f"        {class_name}({', '.join(field_strs)}),")

            code_parts.append("    ]")

        code_parts.append("")
        code_parts.append("    return data")

        self._write_file('data.py', '\n'.join(code_parts))

    def _generate_utils(self):
        """Generate utils.py with helper functions"""
        code = f'''{self._file_header("Utility Functions")}
from typing import Dict, List
from .models import System, Scale, SystemStats


def build_systems_dict(systems: List[System]) -> Dict[str, System]:
    """Build a dictionary of systems keyed by system_id"""
    return {{s.system_id: s for s in systems}}


def calculate_all_scales(scales: List[Scale], systems_dict: Dict[str, System]):
    """Calculate all derived fields for all scales"""
    for scale in scales:
        # Calculate in dependency order
        scale.calculate_base_scale(systems_dict)
        scale.calculate_scale_factor(systems_dict)
        scale.calculate_scale_factor_power()
        scale.calculate_scale(systems_dict)
        scale.calculate_log_scale(systems_dict)
        scale.calculate_log_measure()


def calculate_all_stats(stats_list: List[SystemStats], systems_dict: Dict[str, System], scales: List[Scale]):
    """Calculate all derived fields for all system stats"""
    for stats in stats_list:
        # Calculate in dependency order
        stats.calculate_system_display_name(systems_dict)
        stats.calculate_theoretical_log_log_slope(systems_dict)
        stats.calculate_point_count(scales)
        stats.calculate_min_log_scale(scales)
        stats.calculate_max_log_scale(scales)
        stats.calculate_min_log_measure(scales)
        stats.calculate_max_log_measure(scales)
        stats.calculate_delta_log_measure()
        stats.calculate_delta_log_scale()
        stats.calculate_empirical_log_log_slope()
        stats.calculate_slope_error()


def validate_system(stats: SystemStats, tolerance: float = 0.001) -> bool:
    """Check if empirical slope matches theoretical slope within tolerance"""
    return abs(stats._slope_error or 0) < tolerance
'''
        self._write_file('utils.py', code)

    def _file_header(self, title: str) -> str:
        """Generate file header comment"""
        return f'''"""
{title}

Auto-generated from rulebook
Model: {self.parser.model_name}
Generated: {self.timestamp}

DO NOT EDIT THIS FILE MANUALLY
Regenerate by running: python rulebook-to-python.py
"""'''

    def _to_class_name(self, table_name: str) -> str:
        """Convert table name to Python class name"""
        # Remove trailing 's' and convert to PascalCase
        if table_name == 'systems':
            return 'System'
        elif table_name == 'scales':
            return 'Scale'
        elif table_name == 'system_stats':
            return 'SystemStats'
        return table_name.title()

    def _to_snake_case(self, name: str) -> str:
        """Convert to snake_case"""
        return self.translator._to_snake_case(name)

    def _get_python_type(self, field: Field) -> str:
        """Get Python type annotation for a field"""
        base_type = {
            'string': 'str',
            'number': 'float',
            'decimal': 'float',
            'integer': 'int',
        }.get(field.datatype, 'str')

        # Make nullable if not primary key
        if not field.is_primary_key and field.datatype in ['number', 'decimal', 'integer']:
            return f'Optional[{base_type}]'

        return base_type

    def _find_related_table(self, field: Field, table: Table) -> Optional[str]:
        """Find which table this lookup field relates to"""
        # Look for relationship field in same table
        for f in table.fields:
            if f.field_type == 'relationship' and f.name in field.get_dependencies():
                return f.related_to
        return None

    def _find_child_table(self, field: Field) -> Optional[str]:
        """Find which table this aggregation operates on"""
        if not field.formula:
            return None

        # Extract table name from formula like COUNTIF(scales!{{System}}, ...)
        import re
        match = re.search(r'(COUNTIF|MINIFS|MAXIFS)\((\w+)!', field.formula, re.IGNORECASE)
        if match:
            return match.group(2)
        return None

    def _write_file(self, filename: str, content: str):
        """Write content to a file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  Generated {filepath}")


def main():
    """Main entry point"""
    # Paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    rulebook_path = project_root / 'ssot' / 'ERB_veritasium-power-laws-and-fractals.json'
    output_dir = script_dir / 'rulebook'

    # Check if rulebook exists
    if not rulebook_path.exists():
        print(f"Error: Rulebook not found at {rulebook_path}")
        sys.exit(1)

    # Generate
    generator = PythonGenerator(str(rulebook_path), str(output_dir))
    generator.generate()

    print("\n✓ Python code generation complete!")
    print(f"\nUsage:")
    print(f"  from rulebook import System, Scale, SystemStats, load_sample_data")
    print(f"  data = load_sample_data()")


if __name__ == '__main__':
    main()
