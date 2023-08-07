from src.Operators.OperatorBase import Operator
import numpy as np

class Input(Operator):
    def __init__(self, DF):
        Operator.__init__(self)
        self.type = 'input'
        self.DF = DF.apply(lambda x: x.astype(str).str.strip().str.lower()).replace('nan', np.nan).dropna()
