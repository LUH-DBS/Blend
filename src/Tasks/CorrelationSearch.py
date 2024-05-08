from src.Operators.Seekers import Correlation
import pandas as pd

# typing imports
from typing import List
from numbers import Number
from src.Operators.OperatorBase import Operator


def CorrelationSearch(source_column: List[str], target_column: List[Number], k: int = 10) -> Operator:
    element = Correlation(source_column, target_column, k)
    return element




