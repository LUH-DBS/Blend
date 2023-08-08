from src.Operators.Combiners.CombinerBase import Combiner

# Typing imports
from src.DBHandler import DBHandler

class Intersection(Combiner):
    def __init__(self, k: int=10):
        super().__init__(k)

    def cost(self) -> int:
        # Assuming most calculations are pruned by the first input
        return min(input.cost() for input in self.inputs)
    
    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        sorted_inputs = list(sorted(self.inputs, key=lambda input: input.cost()))

        for input in sorted_inputs[:-1]:
            result = input.run(DB, additionals=additionals)
            if len(result) == 0:
                return "SELECT TableId FROM AllTables WHERE 1=0"
            additionals += f" AND TableId IN ({DB.create_sql_where_condition_from_numerical_value_list(result)}) "
        return sorted_inputs[-1].create_sql_query(DB, additionals=additionals)
