from src.Operators import Combiners
from src.Plan import Plan
from src.Operators.Seekers import Correlation, MultiColumnOverlap


# typing imports
import pandas as pd
from typing import List


def MultiColumnCollinearitySearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, multi_column_column_names: List[str], k: int = 10) -> Plan:
    plan = Plan()
    plan.add("query_included", Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k))
    plan.add("query_excluded", Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k))

    plan.add("difference", Combiners.Difference(k=k), inputs=["query_included", "query_excluded"])

    plan.add("query_mc", MultiColumnOverlap(query_dataset[multi_column_column_names], k*2))
    plan.add("intersection", Combiners.Intersection(k=k), inputs=["query_mc", "difference"])

    return plan
