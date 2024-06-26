from src.Operators.OperatorBase import Operator
from abc import ABC
from pathlib import Path
from src.DBHandler import DBHandler

class Seeker(Operator, ABC):
    def __init__(self, k: int) -> None:
        super().__init__(k)

        self._cached_predicted_runtime = None
        if self.DB.USE_ML_OPTIMIZER:
            from xgboost import XGBRegressor
            self.model = XGBRegressor()
            self.model.load_model(Path(__file__).parent / f"{self.__class__.__name__}_model.json")
        else:
            self.model = None
            self._cached_predicted_runtime = 1

    def _predict_runtime(self, columns: list, db: DBHandler) -> float:
        if self._cached_predicted_runtime is not None:
            return self._cached_predicted_runtime
        
        rows = [tuple(row) for row in zip(*columns)]
        
        freqs = db.get_token_frequencies(set().union(*columns))
        prod = 1
        for col in columns:
            prod *= sum(freqs[token] for token in set(db.clean_value_collection(col)) if token in freqs)
        
        features = [len(set(rows)), prod ** (1 / len(columns)), len(columns)]
        self._cached_predicted_runtime = self.model.predict([features])[0]
        
        return self._cached_predicted_runtime
