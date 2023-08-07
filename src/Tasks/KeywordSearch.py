import pandas as pd
from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import Keyword



def KeywordSearch(query_values, k=10, db_name='vertica', main_index_table_name='gittables_main_tokenized'):
    plan = Plan(db_name, main_index_table_name)
    input_element = Input(pd.DataFrame(query_values))
    plan.add('input', input_element, [], {})
    element = Keyword(query_values, k)
    plan.add('query', element, ['input'], {})
    plan.add('terminal', Terminal(), ['query'], {})
    return plan
