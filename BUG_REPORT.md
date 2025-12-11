# Bug Report: rulebook-to-postgres SQL Generator

**Date:** December 11, 2025  
**Affected Component:** SQL generation from CMCC rulebook schema  
**Source Rulebook:** `ssot/ERB_veritasium-power-laws-and-fractals.json`

---

## Summary of Issues

The SQL generator failed to correctly translate the CMCC rulebook schema into working PostgreSQL code. The following bugs were identified:

1. **BUG-001**: Lookup-type fields do not generate corresponding SQL functions
2. **BUG-002**: Composite primary keys not recognized or generated
3. **BUG-003**: Excel formula syntax not translated to PostgreSQL equivalents
4. **BUG-004**: Calculated functions missing required row-context parameters
5. **BUG-005**: Aggregation functions on calculated fields improperly resolved

---

## BUG-001: Lookup-type fields do not generate corresponding SQL functions

### Severity: **Critical** (Blocks execution)

### Description

The rulebook schema defines fields with `"type": "lookup"` that perform cross-table lookups via foreign key relationships. The SQL generator creates functions for `"type": "calculated"` and `"type": "aggregation"` fields, but completely ignores `"type": "lookup"` fields.

### Schema Definition (from rulebook)

```json
{
  "name": "BaseScale",
  "datatype": "number",
  "type": "lookup",
  "formula": "=_xlfn.INDEX(systems!BaseScale, _xlfn.MATCH({{SystemID}}, systems!SystemID, 0))",
  "Description": "Base scale pulled from systems."
}
```

### Expected SQL Output

```sql
CREATE OR REPLACE FUNCTION calc_scales_base_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (SELECT base_scale FROM systems WHERE system_id = p_system_id);
END;
$$ LANGUAGE plpgsql;
```

### Actual SQL Output

**No function was generated.** The view attempted to call `calc_scales_base_scale()` which did not exist.

### Error Message

```
ERROR:  function calc_scales_base_scale(text) does not exist
LINE 6:   calc_scales_base_scale(t.system_id) AS base_scale,
          ^
HINT:  No function matches the given name and argument types.
```

### Root Cause

The SQL generator only processes fields where `type === "calculated"` or `type === "aggregation"`. Fields with `type === "lookup"` are silently skipped during function generation, but the view generator still expects them to exist.

### Affected Fields

| Table        | Field                    | Lookup Target                       |
|--------------|--------------------------|-------------------------------------|
| scales       | BaseScale                | systems.BaseScale                   |
| scales       | ScaleFactor              | systems.ScaleFactor                 |
| system_stats | TheoreticalLogLogSlope   | systems.TheoreticalLogLogSlope      |

### Fix Applied

Added three missing lookup functions to `02-create-functions.sql` that perform simple `SELECT` queries against the referenced table.

---

## BUG-002: Composite primary keys not recognized or generated

### Severity: **Critical** (Data corruption / insert failures)

### Description

The `scales` table requires a composite primary key on `(SystemID, Iteration)` because multiple rows exist per system (one for each iteration). The SQL generator only created a primary key on `system_id`, causing duplicate key violations when inserting data.

### Schema Definition (from rulebook)

The rulebook had no explicit `primary_key` metadata (before fix). The generator should have inferred from the data structure that multiple rows share the same `SystemID`.

### Expected SQL Output

```sql
CREATE TABLE scales (
  system_id   TEXT     NOT NULL,
  iteration   INTEGER  NOT NULL,
  measure     NUMERIC,
  PRIMARY KEY (system_id, iteration)
);
```

### Actual SQL Output

```sql
CREATE TABLE scales (
  system_id   TEXT     PRIMARY KEY,
  iteration   INTEGER,
  measure     NUMERIC
);
```

### Error Message

```
ERROR:  duplicate key value violates unique constraint "scales_pkey"
DETAIL:  Key (system_id)=(Sierpinski) already exists.
```

### Root Cause

The generator naively applies `PRIMARY KEY` to the first column without analyzing:
1. The data to detect multiple rows with the same value
2. FK relationships that imply a child table pattern
3. Whether multiple columns together form the unique identifier

### Fix Applied

1. Changed table definition to use composite `PRIMARY KEY (system_id, iteration)`
2. Added `primary_key` array metadata to the rulebook for explicit declaration

---

## BUG-003: Excel formula syntax not translated to PostgreSQL equivalents

### Severity: **Critical** (Syntax errors at runtime)

### Description

The rulebook uses Excel-style formula syntax (as it's designed for Excel compatibility). The SQL generator must translate these to PostgreSQL equivalents, but it left Excel-specific function prefixes and names in the generated SQL.

### Examples of Untranslated Syntax

| Excel Formula                | Should Become (PostgreSQL)              |
|------------------------------|-----------------------------------------|
| `_xlfn.LOG10(x)`             | `LOG(10, x)` or `LOG10(x)`              |
| `_xlfn.COUNTIFS(col, val)`   | `SELECT COUNT(*) ... WHERE col = val`   |
| `_xlfn.MINIFS(col, fcol, v)` | `SELECT MIN(col) ... WHERE fcol = v`    |
| `_xlfn.MAXIFS(col, fcol, v)` | `SELECT MAX(col) ... WHERE fcol = v`    |

### Actual SQL Output (broken)

```sql
CREATE OR REPLACE FUNCTION calc_scales_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (_xlfn.LOG10(calc_scales_scale(p_system_id)))::numeric;
END;
$$ LANGUAGE plpgsql;
```

### Error Behavior

PostgreSQL has no function named `_xlfn.LOG10` or `_xlfn.COUNTIFS`. These would fail at runtime when the functions are called.

### Root Cause

The formula parser is performing naive string substitution (replacing `{{FieldName}}` with function calls) without a translation layer for platform-specific function names.

### Fix Applied

Rewrote all functions to use proper PostgreSQL syntax:
- `LOG(10, value)` for logarithms
- `SELECT COUNT(*)/MIN()/MAX() ... WHERE` for conditional aggregations

---

## BUG-004: Calculated functions missing required row-context parameters

### Severity: **Critical** (Wrong calculations or runtime errors)

### Description

Some calculated fields depend on row-level data (not just lookup values). The generator created functions that only accept the foreign key parameter, missing other row-context parameters needed for the calculation.

### Schema Definition (from rulebook)

```json
{
  "name": "Scale",
  "datatype": "number",
  "type": "calculated",
  "formula": "={{BaseScale}}*({{ScaleFactor}}^{{Iteration}})",
  "Description": "X-axis variable"
}
```

Note: `{{Iteration}}` is a **raw field on the same row**, not a lookup.

### Expected SQL Output

```sql
CREATE OR REPLACE FUNCTION calc_scales_scale(p_system_id TEXT, p_iteration INTEGER)
RETURNS NUMERIC AS $$
DECLARE
  v_base_scale NUMERIC;
  v_scale_factor NUMERIC;
BEGIN
  v_base_scale := calc_scales_base_scale(p_system_id);
  v_scale_factor := calc_scales_scale_factor(p_system_id);
  RETURN v_base_scale * POWER(v_scale_factor, p_iteration);
END;
$$ LANGUAGE plpgsql;
```

### Actual SQL Output (broken)

```sql
CREATE OR REPLACE FUNCTION calc_scales_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (... calc_scales_base_scale(p_system_id) ... 
          (SELECT iteration FROM scales WHERE system_id = p_system_id) ...);
END;
$$ LANGUAGE plpgsql;
```

### Problem

The generated function tried to `SELECT iteration FROM scales WHERE system_id = p_system_id` which:
1. Returns multiple rows (one per iteration) causing an error
2. Cannot determine which iteration value to use

### Root Cause

The generator treats all `{{FieldName}}` references the same way:
- Lookups → call a lookup function
- Raw fields on same row → try to SELECT from table (wrong!)

It doesn't distinguish between:
- Fields that come from related tables (lookups)
- Fields that exist on the current row (need to be passed as parameters)

### Fix Applied

1. Modified function signatures to include row-level parameters (`p_iteration`)
2. Updated view to pass both `system_id` and `iteration` to calculated functions

---

## BUG-005: Aggregation functions on calculated fields improperly resolved

### Severity: **High** (Wrong results or runtime errors)

### Description

When an aggregation field references a calculated field from another table, the generator must compute the calculated value for each row before aggregating. The original generator tried to reference calculated fields as if they were columns.

### Schema Definition (from rulebook)

```json
{
  "name": "MinLogScale",
  "type": "aggregation",
  "formula": "=_xlfn.MINIFS(scales!LogScale, scales!SystemID, {{SystemID}})"
}
```

Note: `LogScale` is itself a **calculated field** on the `scales` table, not a raw column.

### Expected SQL Output

```sql
CREATE OR REPLACE FUNCTION calc_system_stats_min_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (
    SELECT MIN(calc_scales_log_scale(s.system_id, s.iteration))
    FROM scales s
    WHERE s.system_id = p_system_id
  );
END;
$$ LANGUAGE plpgsql;
```

### Actual SQL Output (broken)

```sql
CREATE OR REPLACE FUNCTION calc_system_stats_min_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (_xlfn.MINIFS(LogScale, SystemID, 
    (SELECT NULLIF(system_id, '') FROM system_stats WHERE system_id = p_system_id)))::numeric;
END;
$$ LANGUAGE plpgsql;
```

### Problems

1. `_xlfn.MINIFS` is not valid PostgreSQL
2. `LogScale` is not a column in the `scales` table—it's a calculated field
3. The reference to `LogScale` must invoke `calc_scales_log_scale()` for each row

### Root Cause

The generator doesn't track which fields are calculated vs. raw. When generating aggregation SQL, it treats all referenced fields as if they were physical columns.

### Resolution Chain

For `MIN(scales.LogScale)` to work, the generator must:
1. Recognize `LogScale` is calculated (not a column)
2. Find the function `calc_scales_log_scale(system_id, iteration)`
3. Call that function for each row in the aggregation
4. Apply `MIN()` to the results

### Fix Applied

Rewrote aggregation functions to call the appropriate calculation functions for each row before aggregating.

---

## Conclusion

The SQL generator has fundamental architectural issues in understanding the CMCC rulebook schema:

### Core Misunderstandings

1. **Field types are not equivalent.** The generator must handle `raw`, `lookup`, `calculated`, and `aggregation` types differently. Each has distinct semantics:
   - `raw` → physical column, no function needed
   - `lookup` → requires a function to query related table
   - `calculated` → requires a function with proper parameters
   - `aggregation` → requires a function that iterates and aggregates

2. **Row context matters.** Calculated fields that reference other fields on the same row need those values passed as parameters, not looked up via SELECT (which may return multiple rows).

3. **Formula translation is required.** Excel-style formulas must be parsed and translated to the target platform's syntax. A simple regex substitution is insufficient.

4. **Dependency chains must be resolved.** When aggregating on calculated fields, the calculation must happen per-row before aggregation. This requires understanding the full dependency graph.

5. **Primary keys require analysis.** The generator must either:
   - Require explicit `primary_key` metadata in the schema
   - Analyze the data to detect composite key patterns
   - Infer from FK relationships (child tables typically have composite keys)

### Recommendations

1. **Add a field type dispatcher** that generates appropriate SQL based on `type`
2. **Build a dependency graph** before generating functions to understand field relationships
3. **Create a formula parser** that translates Excel functions to PostgreSQL equivalents
4. **Add parameter analysis** to detect which fields need to be passed as function arguments
5. **Require explicit primary key metadata** in the rulebook schema (now added)

### Rulebook Improvements Made

To prevent future issues, the following metadata was added to the rulebook:

```json
{
  "primary_key": ["SystemID", "Iteration"],
  "foreign_keys": [{ "column": "SystemID", "references": "systems.SystemID" }],
  "schema": [
    {
      "name": "BaseScale",
      "type": "lookup",
      "lookup_table": "systems",
      "lookup_column": "BaseScale", 
      "lookup_key": "SystemID"
    },
    {
      "name": "Scale",
      "type": "calculated",
      "depends_on": ["BaseScale", "ScaleFactor", "Iteration"]
    }
  ]
}
```

These additions make the schema more explicit and reduce the need for the generator to infer relationships.

---

*Report generated after manual debugging and fixes to the PostgreSQL output.*

