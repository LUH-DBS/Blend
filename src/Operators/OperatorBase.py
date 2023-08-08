from abc import ABC, abstractmethod

# Typing imports
from src.DBHandler import DBHandler
from typing import List


class Operator(ABC):
    def __init__(self, k):
        self.k = k

    def run(self, DB: DBHandler, additionals: str="") -> List[int]:
        sql = self.create_sql_query(DB, additionals=additionals)
        result = DB.execute_and_fetchall(sql)
        self.result = [r[0] for r in result]
        return self.result
        
    @abstractmethod
    def cost(self) -> int:
        raise NotImplementedError
    
    @abstractmethod
    def create_sql_query(self, DB: DBHandler, additionals: str="") -> str:
        raise NotImplementedError
    