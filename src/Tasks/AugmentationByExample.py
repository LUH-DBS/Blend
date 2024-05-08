from src.Operators import Combiners, Seekers

# Typing imports
import pandas as pd
from typing import Iterable
from src.Operators.OperatorBase import Operator


def AugmentationByExample(examples: pd.DataFrame, queries: Iterable[str], k: int = 10) -> Operator:
    mc_seeker = Seekers.MC(examples, k * 10)
    query_seeker = Seekers.SC(queries, k * 30)
    intersection = Combiners.Intersection(mc_seeker, query_seeker, k=k)
    return intersection
