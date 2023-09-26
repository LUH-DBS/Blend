import random
import configparser
from pathlib import Path

# Typing imports
from typing import List, Union, Tuple, Iterable
from numbers import Number


class DBHandler(object):
    def __init__(self) -> None:
        self.connection = None
        self.cursor = None
        self.index_table = None

        config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
        self.load_config(config_path)

    def load_config(self, config_path: Path) -> None:
        self.close()

        config = configparser.ConfigParser()
        config.read(config_path)

        dbms = config['Database']['dbms'].lower()
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
        # Temporary fix
        query = query.replace('CellValue', 'tokenized').replace("superkey", "super_key").replace("ColumnId", "colid")

        self.cursor.execute(query)
        results = self.cursor.fetchall()

        return results
    
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
