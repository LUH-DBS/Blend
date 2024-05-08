from src.Operators import Combiners
from src.Operators.Seekers import Correlation


# typing imports
import pandas as pd
from src.Operators.OperatorBase import Operator


def FeatureForMLSearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, k: int = 10) -> Operator:
    query_included = Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k*10)
    query_excluded = Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k*10)
    difference = Combiners.Difference(query_included, query_excluded, k=k)
    return difference
