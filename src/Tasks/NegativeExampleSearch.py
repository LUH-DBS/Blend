from src.Plan import Plan
from src.Operators import Combiners
from src.Operators.Seekers import MultiColumnOverlap

from typing import List
# typing imports
import pandas as pd


def NegativeExampleSearch(inclusive_df: pd.DataFrame, inclusive_column_name_1: str, inclusive_column_name_2: str, exclusive_df: pd.DataFrame, exclusive_column_name_1: str, exclusive_column_name_2: str, k: int = 10) -> Plan:
    plan = Plan()
    plan.add("query_exclusive", MultiColumnOverlap(exclusive_df[[exclusive_column_name_1, exclusive_column_name_2]], k*4))
    plan.add("query_inclusive", MultiColumnOverlap(inclusive_df[[inclusive_column_name_1, inclusive_column_name_2]], k*2))
    plan.add("difference", Combiners.Difference(k=k), inputs=["query_exclusive", "query_inclusive"])
    return plan
