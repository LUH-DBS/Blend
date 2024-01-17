from src.Operators.Combiners.CombinerBase import Combiner

from functools import cmp_to_key

# Typing imports
from src.DBHandler import DBHandler


class Intersection(Combiner):
    def __init__(self, k: int = 10):
        super().__init__(k)

    def cost(self) -> int:
        # Assuming most calculations are pruned by the first input
        return min(input_.cost() for input_ in self.inputs)
    
    def ml_cost(self, db: DBHandler) -> float:
        # Assuming most calculations are pruned by the first input
        return min(input_.ml_cost(db) for input_ in self.inputs)
    
    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        def lazy_comparator(operator1, operator2):
            if operator1.cost() != operator2.cost():
                return operator1.cost() - operator2.cost()
            else:
                return operator1.ml_cost(db) - operator2.ml_cost(db)
        
        sorted_inputs = list(sorted(self.inputs, key=cmp_to_key(lazy_comparator)))

        for input_ in sorted_inputs[:-1]:
            result = input_.run(db, additionals=additionals)
            if len(result) == 0:
                return "SELECT TableId FROM AllTables WHERE 1=0"
            additionals += f" AND TableId IN ({db.create_sql_list_numeric(result)}) "
        
        sorted_inputs[-1].k = self.k
        return sorted_inputs[-1].create_sql_query(db, additionals=additionals)
