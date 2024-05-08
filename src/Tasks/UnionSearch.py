from src.Operators import Combiners, Seekers

# typing imports
import pandas as pd
from src.Operators.OperatorBase import Operator


def UnionSearch(dataset: pd.DataFrame, k: int = 10) -> Operator:
    union_elements = []
    for clm_name in dataset.columns:
        element = Seekers.SC(dataset[clm_name], k * 10)
        union_elements.append(element)

    counter = Combiners.Counter(*union_elements, k=k)

    return counter
