import pandas as pd
from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import Keyword

# typing imports
from typing import List


def KeywordSearch(query_values: List[any], k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(pd.DataFrame(query_values))
    plan.add('input', input_element, [])
    element = Keyword(query_values, k)
    plan.add('query', element, ['input'])
    plan.add('terminal', Terminal(), ['query'])
    return plan
