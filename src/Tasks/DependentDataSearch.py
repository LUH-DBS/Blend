from src.Operators import Combiners
from src.Operators.Seekers import SingleColumnOverlap

# typing imports
from typing import List
import pandas as pd
from src.Operators.OperatorBase import Operator


def FeatureForMLSearch(query_dataset: pd.DataFrame, dependent_column_names_1: List[str], dependent_column_names_2: List[str], k: int = 10) -> Operator:
    query_c1 = SingleColumnOverlap(query_dataset[dependent_column_names_1][0], k)
    query_c2 = SingleColumnOverlap(query_dataset[dependent_column_names_1][1], k)
    query_c3 = SingleColumnOverlap(query_dataset[dependent_column_names_2][0], k)
    query_c4 = SingleColumnOverlap(query_dataset[dependent_column_names_2][1], k)

    intersection_1 = Combiners.Intersection(query_c1, query_c2, k=k)
    intersection_2 = Combiners.Intersection(query_c3, query_c4, k=k)
    union = Combiners.Union(intersection_1, intersection_2, k=k)

    return union
