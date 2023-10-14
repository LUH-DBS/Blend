from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler


class Intersection(Combiner):
    def __init__(self, k: int = 10):
        super().__init__(k)

    def cost(self) -> int:
        # Assuming most calculations are pruned by the first input
        return min(input_.cost() for input_ in self.inputs)
    
    def create_sql_query(self, db: DBHandler, additionals: str = "") -> str:
        sorted_inputs = list(sorted(self.inputs, key=lambda operator: operator.cost()))

        for input_ in sorted_inputs[:-1]:
            result = input_.run(db, additionals=additionals)
            if len(result) == 0:
                return "SELECT TableId FROM AllTables WHERE 1=0"
            additionals += f" AND TableId IN ({db.create_sql_list_numeric(result)}) "
        
        sorted_inputs[-1].k = self.k
        return sorted_inputs[-1].create_sql_query(db, additionals=additionals)
