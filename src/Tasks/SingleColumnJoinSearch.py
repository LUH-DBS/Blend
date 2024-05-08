import pandas as pd
from src.Operators.Seekers import SingleColumnOverlap

# typing imports
from typing import Iterable
from src.Operators.OperatorBase import Operator


def SingleColumnJoinSearch(query_values: Iterable[any], k: int = 10) -> Operator:
    return SingleColumnOverlap(query_values, k)

