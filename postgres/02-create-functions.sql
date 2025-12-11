-- ============================================================================
-- CREATE FUNCTIONS - Atomic calculation functions
-- ============================================================================
-- Each function performs exactly ONE operation:
--   - lookup: fetch a value from a parent table
--   - calculated: single arithmetic/function operation on same-row values
--   - aggregation: single aggregate function on child rows
-- ============================================================================

-- ============================================================================
-- SCALES TABLE - LOOKUP FUNCTIONS (from parent: systems)
-- ============================================================================

-- Lookup: BaseScale from systems
CREATE OR REPLACE FUNCTION calc_scales_base_scale(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT sys.base_scale
  FROM scales sc
  JOIN systems sys ON sys.system_id = sc.system_id
  WHERE sc.scale_id = p_scale_id;
$$ LANGUAGE sql STABLE;

-- Lookup: ScaleFactor from systems
CREATE OR REPLACE FUNCTION calc_scales_scale_factor(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT sys.scale_factor
  FROM scales sc
  JOIN systems sys ON sys.system_id = sc.system_id
  WHERE sc.scale_id = p_scale_id;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- SCALES TABLE - CALCULATED FUNCTIONS (single operation each)
-- ============================================================================

-- Calculated: ScaleFactorPower = POWER(ScaleFactor, Iteration)
CREATE OR REPLACE FUNCTION calc_scales_scale_factor_power(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT POWER(calc_scales_scale_factor(p_scale_id), sc.iteration)
  FROM scales sc
  WHERE sc.scale_id = p_scale_id;
$$ LANGUAGE sql STABLE;

-- Calculated: Scale = BaseScale * ScaleFactorPower
CREATE OR REPLACE FUNCTION calc_scales_scale(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT calc_scales_base_scale(p_scale_id) * calc_scales_scale_factor_power(p_scale_id);
$$ LANGUAGE sql STABLE;

-- Calculated: LogScale = LOG10(Scale)
CREATE OR REPLACE FUNCTION calc_scales_log_scale(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT LOG(10, calc_scales_scale(p_scale_id));
$$ LANGUAGE sql STABLE;

-- Calculated: LogMeasure = LOG10(Measure)
CREATE OR REPLACE FUNCTION calc_scales_log_measure(p_scale_id TEXT)
RETURNS NUMERIC AS $$
  SELECT LOG(10, sc.measure)
  FROM scales sc
  WHERE sc.scale_id = p_scale_id;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- SYSTEM_STATS TABLE - LOOKUP FUNCTIONS (from parent: systems)
-- ============================================================================

-- Lookup: TheoreticalLogLogSlope from systems
CREATE OR REPLACE FUNCTION calc_system_stats_theoretical_log_log_slope(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT sys.theoretical_log_log_slope
  FROM systems sys
  WHERE sys.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- SYSTEM_STATS TABLE - AGGREGATION FUNCTIONS (from children: scales)
-- ============================================================================

-- Aggregation: COUNT of scales rows
CREATE OR REPLACE FUNCTION calc_system_stats_point_count(p_system_id TEXT)
RETURNS INTEGER AS $$
  SELECT COUNT(*)::INTEGER
  FROM scales sc
  WHERE sc.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- Aggregation: MIN of LogScale
CREATE OR REPLACE FUNCTION calc_system_stats_min_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT MIN(calc_scales_log_scale(sc.scale_id))
  FROM scales sc
  WHERE sc.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- Aggregation: MAX of LogScale
CREATE OR REPLACE FUNCTION calc_system_stats_max_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT MAX(calc_scales_log_scale(sc.scale_id))
  FROM scales sc
  WHERE sc.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- Aggregation: MIN of LogMeasure
CREATE OR REPLACE FUNCTION calc_system_stats_min_log_measure(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT MIN(calc_scales_log_measure(sc.scale_id))
  FROM scales sc
  WHERE sc.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- Aggregation: MAX of LogMeasure
CREATE OR REPLACE FUNCTION calc_system_stats_max_log_measure(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT MAX(calc_scales_log_measure(sc.scale_id))
  FROM scales sc
  WHERE sc.system_id = p_system_id;
$$ LANGUAGE sql STABLE;

-- ============================================================================
-- SYSTEM_STATS TABLE - CALCULATED FUNCTIONS (single operation each)
-- ============================================================================

-- Calculated: DeltaLogMeasure = MinLogMeasure - MaxLogMeasure
CREATE OR REPLACE FUNCTION calc_system_stats_delta_log_measure(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT calc_system_stats_min_log_measure(p_system_id) 
       - calc_system_stats_max_log_measure(p_system_id);
$$ LANGUAGE sql STABLE;

-- Calculated: DeltaLogScale = MaxLogScale - MinLogScale
CREATE OR REPLACE FUNCTION calc_system_stats_delta_log_scale(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT calc_system_stats_max_log_scale(p_system_id) 
       - calc_system_stats_min_log_scale(p_system_id);
$$ LANGUAGE sql STABLE;

-- Calculated: EmpiricalLogLogSlope = DeltaLogMeasure / DeltaLogScale
CREATE OR REPLACE FUNCTION calc_system_stats_empirical_log_log_slope(p_system_id TEXT)
RETURNS NUMERIC AS $$
  SELECT calc_system_stats_delta_log_measure(p_system_id) 
       / NULLIF(calc_system_stats_delta_log_scale(p_system_id), 0);
$$ LANGUAGE sql STABLE;
