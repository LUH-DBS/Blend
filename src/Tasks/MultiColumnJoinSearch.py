from src.Operators.Seekers import MultiColumnOverlap
from src.Plan import Plan

# typing imports
import pandas as pd


def MultiColumnJoinSearch(query_dataset: pd.DataFrame, k: int = 10) -> Plan:
    plan = Plan()
    plan.add("multi_column_overlap", MultiColumnOverlap(query_dataset, k))
    return plan
