from src.Plan import Plan
from src.Operators import Terminal, Input, Combiners, Seekers

# Typing imports
import pandas as pd
from typing import Iterable


def DataImputation(examples: pd.DataFrame, queries: Iterable[str], k: int = 10) -> Plan:
    plan = Plan()
    inputs = Input([examples, queries])
    plan.add('input', inputs)
    examples_seeker = Seekers.MC(examples, k)
    plan.add('example', examples_seeker, ['input'])
    query_seeker = Seekers.SC(queries, k)
    plan.add('query', query_seeker, ['input'])
    plan.add('combiner', Combiners.Intersection(k), ['example', 'query'])
    plan.add('terminal', Terminal(), ['combiner'])
    return plan
