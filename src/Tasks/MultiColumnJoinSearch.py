from src.Operators.Seekers import MultiColumnOverlap

# typing imports
import pandas as pd
from src.Operators.OperatorBase import Operator


def MultiColumnJoinSearch(query_dataset: pd.DataFrame, k: int = 10) -> Operator:
    return MultiColumnOverlap(query_dataset, k)
