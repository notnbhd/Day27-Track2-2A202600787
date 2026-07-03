from api import Verdict

def register(ctx):
    ctx.on("data_batch", check_data_batch)
    ctx.on("contract_checkpoint", check_contract_checkpoint)
    ctx.on("lineage_run", check_lineage_run)
    ctx.on("feature_materialization", check_feature_materialization)
    ctx.on("embedding_batch", check_embedding_batch)

def check_data_batch(payload, ctx):
    batch_id = payload["batch_id"]
    profile = ctx.tools.batch_profile(batch_id)
    if not profile or "error" in profile:
        return Verdict(alert=False, pillar="checks")
    
    # Extract metrics
    row_count = profile.get("row_count", 0)
    null_rate = profile.get("null_rate", {}).get("customer_id", 0)
    mean_amount = profile.get("mean_amount", 0)
    staleness = profile.get("staleness_min", 0)
    
    # Get baseline limits
    row_count_max = ctx.baseline.get("row_count_max", 561.2948)
    null_rate_max = ctx.baseline.get("null_rate_max", 0.0109)
    staleness_min_max = ctx.baseline.get("staleness_min_max", 8.418)
    
    # Proposed thresholds
    if row_count > row_count_max:
        return Verdict(alert=True, pillar="checks", reason="volume_spike")
    if null_rate > null_rate_max:
        return Verdict(alert=True, pillar="checks", reason="null_spike")
    if staleness > staleness_min_max:
        return Verdict(alert=True, pillar="checks", reason="freshness_lag")
    if mean_amount > 88.7 or mean_amount < 74.5:
        return Verdict(alert=True, pillar="checks", reason="distribution_shift")
        
    return Verdict(alert=False, pillar="checks")

def check_contract_checkpoint(payload, ctx):
    contract_id = payload["contract_id"]
    checkpoint_batch_id = payload["checkpoint_batch_id"]
    diff = ctx.tools.contract_diff(contract_id, checkpoint_batch_id)
    if not diff or "error" in diff:
        return Verdict(alert=False, pillar="contracts")
        
    violations = diff.get("violations", [])
    freshness_delay = diff.get("freshness_delay_min", 0)
    
    freshness_delay_max_min = ctx.baseline.get("freshness_delay_max_min", 11.1141)
    
    if "type_violation" in violations:
        return Verdict(alert=True, pillar="contracts", reason="type_violation")
    if "schema_hash_mismatch" in violations or "schema_break" in violations:
        return Verdict(alert=True, pillar="contracts", reason="schema_break")
    if freshness_delay > freshness_delay_max_min:
        return Verdict(alert=True, pillar="contracts", reason="sla_violation")
        
    return Verdict(alert=False, pillar="contracts")

def check_lineage_run(payload, ctx):
    run_id = payload["run_id"]
    slice_data = ctx.tools.lineage_graph_slice(run_id)
    if not slice_data or "error" in slice_data:
        return Verdict(alert=False, pillar="lineage")
        
    duration = slice_data.get("duration_ms", 0)
    actual_upstream = slice_data.get("actual_upstream", [])
    actual_downstream_count = slice_data.get("actual_downstream_count", 0)
    
    lineage_duration_ms_max = ctx.baseline.get("lineage_duration_ms_max", 5134.9804)
    
    if duration > lineage_duration_ms_max:
        return Verdict(alert=True, pillar="lineage", reason="runtime_anomaly")
    if actual_downstream_count < 1:
        return Verdict(alert=True, pillar="lineage", reason="orphan_output")
        
    # Check upstream
    expected_upstream = {"raw.orders", "raw.customers"}
    if set(actual_upstream) != expected_upstream:
        return Verdict(alert=True, pillar="lineage", reason="missing_upstream")
        
    return Verdict(alert=False, pillar="lineage")

def check_feature_materialization(payload, ctx):
    feature_view = payload["feature_view"]
    batch_id = payload["batch_id"]
    drift = ctx.tools.feature_drift(feature_view, batch_id)
    if not drift or "error" in drift:
        return Verdict(alert=False, pillar="ai_infra")
        
    mean_shift_sigma = drift.get("mean_shift_sigma", 0)
    
    if mean_shift_sigma > 0.8:
        return Verdict(alert=True, pillar="ai_infra", reason="feature_skew")
        
    return Verdict(alert=False, pillar="ai_infra")

def check_embedding_batch(payload, ctx):
    corpus = payload["corpus"]
    chunk_batch_id = payload["chunk_batch_id"]
    drift = ctx.tools.embedding_drift(corpus, chunk_batch_id)
    if not drift or "error" in drift:
        return Verdict(alert=False, pillar="ai_infra")
        
    centroid_shift = drift.get("centroid_shift", 0)
    avg_doc_age_days = drift.get("avg_doc_age_days", 0)
    
    if centroid_shift > 0.039:
        return Verdict(alert=True, pillar="ai_infra", reason="embedding_drift")
    if avg_doc_age_days > 42.0:
        return Verdict(alert=True, pillar="ai_infra", reason="corpus_staleness")
        
    return Verdict(alert=False, pillar="ai_infra")
