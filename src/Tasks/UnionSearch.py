from src.Operators import Combiners, Seekers
from src.Plan import Plan

# typing imports
import pandas as pd


def UnionSearch(dataset: pd.DataFrame, k: int = 10) -> Plan:
    plan = Plan()
    for clm_name in dataset.columns:
        plan.add(clm_name, Seekers.SC(dataset[clm_name], k * 10))

    plan.add("union", Combiners.Union(k=k), inputs=dataset.columns)

    return plan
