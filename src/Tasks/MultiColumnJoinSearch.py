from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import MultiColumnOverlap



def MultiColumnJoinSearch(query_dataset, k=10, db_name='vertica', main_index_table_name='main_tokenized_quadrants'):
    plan = Plan(db_name, main_index_table_name)
    input_element = Input(query_dataset)
    plan.add('input', input_element, [], {})
    element = MultiColumnOverlap(query_dataset, k)
    plan.add('query', element, ['input'], {})
    plan.add('terminal', Terminal(), ['query'], {})
    return plan
