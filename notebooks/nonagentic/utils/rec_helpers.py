"""Level 5 recommendation row-building helpers."""
from collections import Counter, defaultdict
import math


def build_seg_rows(top_seg, segment, PROD_MAP):
    return [{
        "Product ID":    pid,
        "Name":          PROD_MAP.get(pid, {}).get("name", "?"),
        "Category":      PROD_MAP.get(pid, {}).get("category", "?"),
        "Segment Score": round(score, 3),
        "Explanation":   f"Popular in '{segment}' segment",
    } for pid, score in top_seg]


def build_sim_rows(similar_users, target_vec, MATRIX, CUST_MAP, cosine_fn):
    return [{
        "Customer ID":  uid,
        "Segment":      CUST_MAP.get(uid, {}).get("segment", "?"),
        "Similarity":   round(cosine_fn(target_vec, MATRIX.get(uid, {})), 3),
        "Interactions": len(MATRIX.get(uid, {})),
        "Categories":   ", ".join(CUST_MAP.get(uid, {}).get("purchase_categories", [])[:3]),
    } for uid in similar_users]


def build_collab_rows(top_collab, PROD_MAP):
    return [{
        "Product ID": pid,
        "Name":       PROD_MAP.get(pid, {}).get("name", "?"),
        "Category":   PROD_MAP.get(pid, {}).get("category", "?"),
        "CF Score":   round(score, 3),
    } for pid, score in top_collab]


def build_behav_rows(behav_scores, content_scores, PROD_MAP, top_k=10):
    all_pids = set(behav_scores) | set(content_scores)
    rows = [{
        "Product ID":      pid,
        "Name":            PROD_MAP.get(pid, {}).get("name", "?"),
        "Category":        PROD_MAP.get(pid, {}).get("category", "?"),
        "Behaviour Score": round(behav_scores.get(pid, 0.0), 3),
        "Content Score":   round(content_scores.get(pid, 0.0), 3),
        "Combined":        round(behav_scores.get(pid, 0.0) * 0.6 + content_scores.get(pid, 0.0) * 0.4, 3),
    } for pid in all_pids]
    return sorted(rows, key=lambda r: -r["Combined"])[:top_k]


def build_hybrid_rows(recs, PROD_MAP):
    return [{
        "Rank":        i + 1,
        "Product ID":  r["product_id"],
        "Name":        PROD_MAP.get(r["product_id"], {}).get("name", "?"),
        "Category":    PROD_MAP.get(r["product_id"], {}).get("category", "?"),
        "Score":       round(r["score"], 3),
        "Confidence":  round(r["confidence"], 3),
        "Explanation": r["explanation"],
    } for i, r in enumerate(recs)]


def build_cold_rows(top_cold, segment, PROD_MAP):
    return [{
        "Product ID":  pid,
        "Name":        PROD_MAP.get(pid, {}).get("name", "?"),
        "Category":    PROD_MAP.get(pid, {}).get("category", "?"),
        "Score":       score,
        "Source":      "segment_fallback",
        "Explanation": f"Popular in '{segment}' segment",
    } for pid, score in top_cold]


def build_seg_batch_rows(top_seg_recs, PROD_MAP):
    return [{
        "Product ID": pid,
        "Name":       PROD_MAP.get(pid, {}).get("name", "?"),
        "Category":   PROD_MAP.get(pid, {}).get("category", "?"),
        "Avg Score":  score,
    } for pid, score in top_seg_recs]


def build_precision_buckets(eval_users, eligible, recommend_fn, k=10):
    buckets = Counter()
    for uid in eval_users:
        recs  = eligible[uid]
        split = max(1, len(recs) * 4 // 5)
        gt    = {r["product_id"] for r in recs[split:]}
        if not gt:
            continue
        result = recommend_fn(uid, exclude_purchased=False)
        pids   = [r["product_id"] for r in result.get("recommendations", [])][:k]
        hits   = sum(1 for p in pids if p in gt)
        prec   = hits / k
        bucket = f"{int(prec * 10) * 10}–{int(prec * 10) * 10 + 10}%"
        buckets[bucket] += 1
    return dict(buckets)
