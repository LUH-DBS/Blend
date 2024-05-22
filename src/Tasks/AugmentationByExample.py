from src.Operators import Combiners, Seekers
from src.Plan import Plan

# Typing imports
import pandas as pd
from typing import Iterable


def AugmentationByExample(examples: pd.DataFrame, queries: Iterable[str], k: int = 10) -> Plan:
    plan = Plan()
    plan.add("mc_seeker", Seekers.MC(examples, k * 10))
    plan.add("query_seeker", Seekers.SC(queries, k * 30))
    plan.add("intersection", Combiners.Intersection(k=k), inputs=["mc_seeker", "query_seeker"])

    return plan
