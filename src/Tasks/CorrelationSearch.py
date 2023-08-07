from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import Correlation

import pandas as pd


def CorrelationSearch(source_column, target_column, k=10, db_name='vertica', main_index_table_name='main_tokenized_quadrants'):
    plan = Plan(db_name, main_index_table_name)
    input_element = Input(pd.DataFrame({'source_column': source_column, 'target_column': target_column}))
    plan.add('input', input_element, [], {})
    element = Correlation(source_column, target_column, k)
    plan.add('query', element, ['input'], {})
    plan.add('terminal', Terminal(), ['query'], {})
    return plan




