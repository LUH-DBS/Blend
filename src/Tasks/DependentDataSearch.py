from src.Operators import Combiners
from src.Plan import Plan
from src.Operators.Seekers import SingleColumnOverlap as SC

# typing imports
from typing import List
import pandas as pd


def DependentDataSearch(query_dataset: pd.DataFrame, dependent_column_names_1: List[str], dependent_column_names_2: List[str], k: int = 10) -> Plan:
    plan = Plan()
    
    plan.add("query_c1", SC(query_dataset[dependent_column_names_1][0], k))
    plan.add("query_c2", SC(query_dataset[dependent_column_names_1][1], k))
    plan.add("intersection_1", Combiners.Intersection(k=k), inputs=["query_c1", "query_c2"])

    plan.add("query_c3", SC(query_dataset[dependent_column_names_2][0], k))
    plan.add("query_c4", SC(query_dataset[dependent_column_names_2][1], k))
    plan.add("intersection_2", Combiners.Intersection(k=k), inputs=["query_c3", "query_c4"])


    plan.add("union", Combiners.Union(k=k), inputs=["intersection_1", "intersection_2"])

    return plan
