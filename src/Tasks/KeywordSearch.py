import pandas as pd
from src.Operators.Seekers import Keyword

# typing imports
from typing import List
from src.Operators.OperatorBase import Operator

def KeywordSearch(query_values: List[any], k: int = 10) -> Operator:
    return Keyword(query_values, k)
