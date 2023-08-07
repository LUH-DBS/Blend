import pandas as pd
from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import SingleColumnOverlap



def SingleColumnJoinSearch(query_values, k=10):
    plan = Plan()
    input_element = Input(pd.DataFrame(query_values))
    plan.add('input', input_element, [], {})
    element = SingleColumnOverlap(query_values, k)
    plan.add('query', element, ['input'], {})
    plan.add('terminal', Terminal(), ['query'], {})
    return plan
