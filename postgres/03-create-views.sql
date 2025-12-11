-- ============================================================================
-- CREATE VIEWS - Combine raw data with calculated fields
-- ============================================================================
-- Each view exposes all columns: raw, lookup, and calculated
-- ============================================================================

-- systems View (all raw columns)
CREATE OR REPLACE VIEW vw_systems AS
SELECT
  t.system_id,
  t.display_name,
  t.class,
  t.base_scale,
  t.scale_factor,
  t.measure_name,
  t.fractal_dimension,
  t.theoretical_log_log_slope
FROM systems t;

-- scales View (raw + lookup + calculated)
CREATE OR REPLACE VIEW vw_scales AS
SELECT
  -- Raw columns
  t.scale_id,
  t.system_id,
  t.iteration,
  t.measure,
  -- Lookup columns (from parent: systems)
  calc_scales_base_scale(t.scale_id) AS base_scale,
  calc_scales_scale_factor(t.scale_id) AS scale_factor,
  -- Calculated columns (atomic single-operation each)
  calc_scales_scale_factor_power(t.scale_id) AS scale_factor_power,
  calc_scales_scale(t.scale_id) AS scale,
  calc_scales_log_scale(t.scale_id) AS log_scale,
  calc_scales_log_measure(t.scale_id) AS log_measure
FROM scales t;

-- system_stats View (raw + lookup + aggregation + calculated)
CREATE OR REPLACE VIEW vw_system_stats AS
SELECT
  -- Raw columns
  t.system_id,
  -- Lookup columns (from parent: systems)
  calc_system_stats_theoretical_log_log_slope(t.system_id) AS theoretical_log_log_slope,
  -- Aggregation columns (from children: scales)
  calc_system_stats_point_count(t.system_id) AS point_count,
  calc_system_stats_min_log_scale(t.system_id) AS min_log_scale,
  calc_system_stats_max_log_scale(t.system_id) AS max_log_scale,
  calc_system_stats_min_log_measure(t.system_id) AS min_log_measure,
  calc_system_stats_max_log_measure(t.system_id) AS max_log_measure,
  -- Calculated columns (atomic single-operation each)
  calc_system_stats_delta_log_measure(t.system_id) AS delta_log_measure,
  calc_system_stats_delta_log_scale(t.system_id) AS delta_log_scale,
  calc_system_stats_empirical_log_log_slope(t.system_id) AS empirical_log_log_slope
FROM system_stats t;
