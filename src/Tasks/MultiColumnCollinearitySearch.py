from src.Operators import Combiners
from src.Operators.Seekers import Correlation, MultiColumnOverlap


# typing imports
import pandas as pd
from typing import List
from src.Operators.OperatorBase import Operator


def MultiColumnCollinearitySearch(query_dataset: pd.DataFrame, source_column_name: str, target_column_name: str, numerical_feature_column_name: str, multi_column_column_names: List[str], k: int = 10) -> Operator:
    query_included = Correlation(query_dataset[source_column_name], query_dataset[target_column_name], k)
    query_excluded = Correlation(query_dataset[source_column_name], query_dataset[numerical_feature_column_name], k)
    difference = Combiners.Difference(query_included, query_excluded, k=k)
    query_mc = MultiColumnOverlap(query_dataset[[source_column_name, target_column_name]], k*2)
    intersection = Combiners.Intersection(query_mc, difference, k=k)
    return intersection
