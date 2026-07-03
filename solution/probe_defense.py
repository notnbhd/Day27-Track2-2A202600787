"""Calibration probe: calls each documented tool once per event and logs
payload + tool output to solution/probe_log.jsonl for offline analysis against
the provided practice answer key. Not a submission artifact."""
import json
from api import Verdict

LOG = "/home/nacho/Vin_20KAI/Day27-Track2-2A202600787/solution/probe_log.jsonl"


def _log(rec):
    with open(LOG, "a") as f:
        f.write(json.dumps(rec) + "\n")


def register(ctx):
    ctx.on("data_batch", h_batch)
    ctx.on("contract_checkpoint", h_contract)
    ctx.on("lineage_run", h_lineage)
    ctx.on("feature_materialization", h_feature)
    ctx.on("embedding_batch", h_embed)


def h_batch(payload, ctx):
    r = ctx.tools.batch_profile(payload["batch_id"])
    _log({"type": "data_batch", "payload": payload, "tool": r})
    return Verdict(alert=False)


def h_contract(payload, ctx):
    r = ctx.tools.contract_diff(payload["contract_id"], payload["checkpoint_batch_id"])
    _log({"type": "contract_checkpoint", "payload": payload, "tool": r})
    return Verdict(alert=False)


def h_lineage(payload, ctx):
    r = ctx.tools.lineage_graph_slice(payload["run_id"])
    _log({"type": "lineage_run", "payload": payload, "tool": r})
    return Verdict(alert=False)


def h_feature(payload, ctx):
    r = ctx.tools.feature_drift(payload["feature_view"], payload["batch_id"])
    _log({"type": "feature_materialization", "payload": payload, "tool": r})
    return Verdict(alert=False)


def h_embed(payload, ctx):
    r = ctx.tools.embedding_drift(payload["corpus"], payload["chunk_batch_id"])
    _log({"type": "embedding_batch", "payload": payload, "tool": r})
    return Verdict(alert=False)
