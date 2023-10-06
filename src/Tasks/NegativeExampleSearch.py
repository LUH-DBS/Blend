from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners
from src.Operators.Seekers import MultiColumnOverlap

from typing import List
# typing imports
import pandas as pd


def NegativeExampleSearch(inclusive_df: pd.DataFrame, inclusive_column_name_1: str, inclusive_column_name_2: str, exclusive_df: pd.DataFrame, exclusive_column_name_1: str, exclusive_column_name_2: str, k: int = 10) -> Plan:
    plan = Plan()
    # df = pd.DataFrame({'inclusive_column_1': inclusive_column_1, 'inclusive_column_2': inclusive_column_2, 'exclusive_column_1': exclusive_column_1, 'exclusive_column_2': exclusive_column_2})
    input_element = Input(inclusive_df)
    plan.add('input', input_element, [])
    element_exclusive = MultiColumnOverlap(exclusive_df[[exclusive_column_name_1, exclusive_column_name_2]], k*100)
    element_inclusive = MultiColumnOverlap(inclusive_df[[inclusive_column_name_1, inclusive_column_name_2]], k*10)
    plan.add('query_exclusive', element_exclusive, ['input'])
    plan.add('query_inclusive', element_inclusive, ['input'])

    plan.add('difference', Combiners.Difference(k), ['query_inclusive', 'query_exclusive'])
    plan.add('terminal', Terminal(), ['difference'])
    return plan
