from src.Operators import Combiners
from src.Plan import Plan
from src.Operators.Seekers import Correlation


# typing imports
import pandas as pd


def FeatureForMLSearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, k: int = 10) -> Plan:
    plan = Plan()
    plan.add("query_included", Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k*10))
    plan.add("query_excluded", Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k*10))
    plan.add("difference", Combiners.Difference(k=k), inputs=["query_included", "query_excluded"])
    return plan
