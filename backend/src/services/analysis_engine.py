import itertools
import math
from datetime import datetime, timedelta, timezone

import numpy as np
from scipy import stats
from sklearn.cluster import DBSCAN, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, roc_auc_score, roc_curve, silhouette_score
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer


def _metric(label, value, unit="", tone="neutral"):
    if isinstance(value, (np.floating, np.integer)):
        value = value.item()
    return {"label": label, "value": value, "unit": unit, "tone": tone}


def _series(label, value):
    return {"label": str(label), "value": float(value)}


def _envelope(headline, narrative, metrics, series, table, method, caveat):
    return {
        "headline": headline,
        "narrative": narrative,
        "metrics": metrics,
        "series": series,
        "table": table,
        "method": method,
        "caveat": caveat,
    }


def run_primary(rows: list[dict], config: dict) -> dict:
    feature_keys = ["age", "seniority", "alerts", "days_since_service", "usage"]
    matrix = np.asarray([[float(row.get(key, 0)) for key in feature_keys] for row in rows])
    target = np.asarray([int(row.get("late", 0)) for row in rows])
    if len(set(target.tolist())) < 2:
        raise ValueError("需要超时与非超时样本")
    tree = DecisionTreeClassifier(max_depth=4, min_samples_leaf=max(8, len(rows) // 40), random_state=42)
    tree.fit(matrix, target)
    paths = []

    def walk(node: int, conditions: list[str]) -> None:
        if tree.tree_.children_left[node] == tree.tree_.children_right[node]:
            paths.append({"label": " 且 ".join(conditions) if conditions else "全部工单",
                          "rate": float(tree.tree_.value[node][0][1] / max(tree.tree_.value[node][0].sum(), 1)),
                          "samples": int(tree.tree_.n_node_samples[node])})
            return
        feature = feature_keys[tree.tree_.feature[node]]
        threshold = tree.tree_.threshold[node]
        walk(tree.tree_.children_left[node], conditions + [f"{feature} <= {threshold:.1f}"])
        walk(tree.tree_.children_right[node], conditions + [f"{feature} > {threshold:.1f}"])

    walk(0, [])
    paths.sort(key=lambda item: item["rate"], reverse=True)
    top = paths[0]
    predicted = tree.predict(matrix)
    accuracy = float((predicted == target).mean())
    return _envelope(
        f"最高风险规则命中率 {top['rate']:.1%}，样本 {top['samples']} 单",
        f"CART 树最大深度 4，训练集准确率 {accuracy:.1%}；叶节点规则可复核。",
        [
            _metric("训练准确率", accuracy * 100, "%", "neutral"),
            _metric("规则数量", len(paths), "条", "neutral"),
            _metric("最高风险叶", top["rate"] * 100, "%", "negative"),
            _metric("叶样本", top["samples"], "单", "neutral"),
        ],
        [_series(f"规则 {i + 1}", round(item["rate"] * 100, 2)) for i, item in enumerate(paths[:10])],
        [{"label": item["label"], "late_rate": round(item["rate"], 4),
          "samples": item["samples"]} for item in paths],
        "cart_decision_tree + rule_path_export",
        "规则来自训练集，需在后续工单上做时间外验证；叶节点过小时不应直接上线。",
    )



def run_algorithm(rows: list[dict], config: dict) -> dict:
    return run_primary(rows or [], config or {})
