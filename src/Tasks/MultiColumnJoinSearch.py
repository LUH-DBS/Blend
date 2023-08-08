from src.Plan import Plan
from src.Operators import Terminal, Input
from src.Operators.Seekers import MultiColumnOverlap

# typing imports
import pandas as pd


def MultiColumnJoinSearch(query_dataset: pd.DataFrame, k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(query_dataset)
    plan.add('input', input_element, [])
    element = MultiColumnOverlap(query_dataset, k)
    plan.add('query', element, ['input'])
    plan.add('terminal', Terminal(), ['query'])
    return plan
