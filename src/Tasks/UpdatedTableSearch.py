from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners
from src.Operators.Seekers import MultiColumnOverlap

from typing import List
# typing imports
import pandas as pd


def UpdatedTableSearch(old_column_1: List[str], old_column_2: List[str], new_column_1: List[str], new_column_2: List[str], k: int = 10) -> Plan:
    plan = Plan()
    df = pd.DataFrame({'old_column_1': old_column_1, 'old_column_2': old_column_2, 'new_column_1': new_column_1, 'new_column_2': new_column_2})
    input_element = Input(df)
    plan.add('input', input_element, [])
    element_new = MultiColumnOverlap(df[['new_column_1', 'new_column_2']], k)
    element_old = MultiColumnOverlap(df[['old_column_1', 'old_column_2']], k)
    plan.add('query_new', element_new, ['input'])
    plan.add('query_old', element_old, ['input'])

    plan.add('difference', Combiners.Difference(k), ['query_new', 'query_old'])
    plan.add('terminal', Terminal(), ['difference'])
    return plan
