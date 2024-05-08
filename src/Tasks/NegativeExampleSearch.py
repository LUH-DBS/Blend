from src.Operators import Combiners
from src.Operators.Seekers import MultiColumnOverlap

from typing import List
# typing imports
import pandas as pd
from src.Operators.OperatorBase import Operator


def NegativeExampleSearch(inclusive_df: pd.DataFrame, inclusive_column_name_1: str, inclusive_column_name_2: str, exclusive_df: pd.DataFrame, exclusive_column_name_1: str, exclusive_column_name_2: str, k: int = 10) -> Operator:
    query_exclusive = MultiColumnOverlap(exclusive_df[[exclusive_column_name_1, exclusive_column_name_2]], k*4)
    query_inclusive = MultiColumnOverlap(inclusive_df[[inclusive_column_name_1, inclusive_column_name_2]], k*2)
    difference = Combiners.Difference(query_exclusive, query_inclusive, k=k)
    return difference
