from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners
from src.Operators.Seekers import Correlation


# typing imports
import pandas as pd


def FeatureForMLSearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(query_dataset)
    plan.add('input', input_element, [])
    element_included = Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k)
    plan.add('query_included', element_included, ['input'])
    element_excluded = Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k)
    plan.add('query_excluded', element_excluded, ['input'])
    plan.add('difference', Combiners.Difference(k), ['query_included', 'query_excluded'])
    plan.add('terminal', Terminal(), ['difference'])
    return plan
