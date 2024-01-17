import random
import configparser
from pathlib import Path
import pandas as pd

# Typing imports
from typing import List, Union, Tuple, Iterable
from numbers import Number
import pickle


class DBHandler(object):
    frequency_dict = None

    def __init__(self) -> None:
        self.connection = None
        self.cursor = None
        self.index_table = None
        self.dbms = None

        config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
        self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        self.close()

        config = configparser.ConfigParser()
        config.read(config_path)

        dbms = config['Database']['dbms'].lower()
        self.dbms = dbms
        if dbms == 'vertica':
            import vertica_python
            self.connection = vertica_python.connect(
                host=config['Database']['host'],
                port=config['Database']['port'],
                user=config['Database']['user'],
                password=config['Database']['password'],
                database=config['Database']['dbname'],
                session_label='some_label',
                read_timeout=60000,
                unicode_error='strict',
                ssl=False,
                use_prepared_statements=False
            )
        elif dbms == 'postgres':
            import psycopg as pg
            self.connection = pg.connect(
                host=config['Database']['host'],
                port=config['Database']['port'],
                user=config['Database']['user'],
                password=config['Database']['password'],
                dbname=config['Database']['dbname'],
            )
        elif dbms == 'duckdb':
            import duckdb
            self.connection = duckdb.connect(database=config['Database']['path'], read_only=True)

        self.cursor = self.connection.cursor()
        self.index_table = config['Database']['index_table']
        if DBHandler.frequency_dict is None:
            try:
                print("Loading frequency dict...")
                DBHandler.frequency_dict = pickle.load(open("freqs_dict.pkl", 'rb'))
            except FileNotFoundError as e:
                print("Could not load frequency dict")
                raise e

    def close(self) -> None:
        if self.cursor is not None:
            self.cursor.close()
        if self.connection is not None:
            self.connection.close()

        self.cursor = None
        self.connection = None

    def clean_query(self, query: str) -> str:
        return query.replace('AllTables', f'{self.index_table}')

    def execute_and_fetchall(self, query: str) -> List[Union[Tuple, List]]:
        """Returns results"""
        query = self.clean_query(query)
        if self.dbms == 'postgres':
            query = query.replace('TO_BITSTRING(superkey)', f'superkey')
        query.replace('TO_BITSTRING(superkey)', f'superkey')
        query = query.replace('CellValue', 'tokenized').replace("superkey", "super_key").replace("ColumnId", "colid")

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results
    
    def get_table_from_index(self, table_id: int) -> pd.DataFrame:
        sql = f"""
        SELECT CellValue, ColumnId, RowId
        FROM AllTables
        WHERE TableId = {table_id}
        """

        results = self.execute_and_fetchall(sql)

        df = pd.DataFrame(results, columns=['CellValue', 'ColumnId', 'RowId'], dtype=str)
        df = df.pivot(index='RowId', columns='ColumnId', values='CellValue')
        df.index.name = None
        df.columns.name = None

        return df
    
    def table_ids_to_sql(self, table_ids: Iterable[int]) -> str:
        if len(table_ids) == 0:
            return "SELECT 0 AS TableId WHERE 1 = 0"

        if self.dbms == 'postgres':
            return f"""
            SELECT * FROM (
                VALUES {' ,'.join([f"({table_id})" for table_id in table_ids])}
            ) AS {DBHandler.random_subquery_name()}(TableId)
            """
        elif self.dbms == 'vertica':
            return f"""
            SELECT TableId
            FROM (
                SELECT Explode(Array[{', '.join(f"{table_id}" for table_id in table_ids)}])
                OVER (Partition Best) AS (Index_In_Array, TableId)
            ) {DBHandler.random_subquery_name()}
            """
        
        return f"""
            SELECT TableId FROM (
            {' UNION ALL '.join([f'SELECT {table_id} AS TableId' for table_id in table_ids])}
            ) AS {DBHandler.random_subquery_name()}
        """
    
    def get_token_frequencies(self, tokens: Iterable[str]) -> dict[str, int]:
        tokens = DBHandler.clean_value_collection(set(tokens))
        
        return {token: DBHandler.frequency_dict.get(token, 1) for token in tokens}

    
    @staticmethod
    def clean_value_collection(values: Iterable[any]) -> List[str]:
        return [str(v).replace("'", "''").strip() for v in values if str(v).lower() != 'nan']

    @staticmethod
    def create_sql_list_str(values: Iterable[any]) -> str:
        values = [str(x).replace('\'', '') for x in values]
        return "'{}'".format("' , '".join(set(values)))

    @staticmethod
    def create_sql_list_numeric(values: Iterable[Number]) -> str:
        values = [str(x) for x in values]
        return "{}".format(" , ".join(values))

    @staticmethod
    def random_subquery_name() -> str:
        return f"subquery{random.random()*1000000:.0f}"
