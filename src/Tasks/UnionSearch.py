from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners, Seekers

# typing imports
import pandas as pd


def UnionSearch(dataset: pd.DataFrame, k: int = 10) -> Plan:
    plan = Plan()
    input_element = Input(dataset)
    plan.add('input', input_element)
    for clm_name in dataset.columns:
        element = Seekers.SC(dataset[clm_name], k)
        plan.add(clm_name, element, ['input'])
    plan.add('counter', Combiners.Counter(k), dataset.columns)
    plan.add('terminal', Terminal(), ['counter'])

    return plan
