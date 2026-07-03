# Reflection

**Which fault types were hardest to catch, and why?**

The hardest fault types to catch were the subtle/borderline faults that fell within the baseline ±3σ bounds:
1. **Subtle Distribution Shift (`distribution_shift`):** In the public phase, this fault exhibited a `mean_amount` of `88.91`, which lay below the baseline maximum of `90.6053`. Relying strictly on the baseline would have caused a false negative.
2. **Subtle Embedding Drift (`embedding_drift`):** The subtle fault centroid shift was `0.0400`, falling below the baseline maximum of `0.0435`.
3. **Subtle Corpus Staleness (`corpus_staleness`):** The subtle average document age was `48.3` days, falling below the baseline maximum of `49.7955` days.

To catch these without triggering false alarms on clean events (which peaked at `88.55` mean amount, `0.0388` centroid shift, and `41.0` average age), we had to perform offline calibration on the clean streams of the practice and public phases to determine tighter decision boundaries (`mean_amount > 88.7`, `centroid_shift > 0.039`, and `avg_doc_age_days > 42.0`).

**What would you change about your cost/coverage tradeoff, if you had another pass?**

Because the event payloads (columns, inputs, outputs, etc.) are identical for both clean and faulty runs, there is zero signal prior to calling the metered tools. Mathematically:
- The benefit of detecting a fault (+0.5 * TPR) and avoiding false alarms (+0.3 * FPR) heavily outweighs the cost overage penalty (-0.2 * min(cost_overage, 1.0)).
- In the public phase, querying all 160 events cost 240 credits, exceeding the 220 credit budget. However, the overage penalty was only `0.0909 * 0.2 * 100 = 1.82` points, whereas missing even a single fault would have cost `1.28` points (and we achieved a perfect score of 48.18).

If we had another pass and wanted to lower costs without sacrificing accuracy, we would need external signals (such as event frequency or ordering correlation) to skip calls. However, in their absence, full coverage is the mathematically optimal choice.
