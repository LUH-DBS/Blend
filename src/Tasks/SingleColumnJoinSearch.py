from src.Plan import Plan
from src.Operators.Seekers import SingleColumnOverlap

# typing imports
from typing import Iterable


def SingleColumnJoinSearch(query_values: Iterable[any], k: int = 10) -> Plan:
    plan = Plan()
    plan.add("single_column_overlap", SingleColumnOverlap(query_values, k))
    return plan

