import duckdb
import vertica_python
import psycopg as pg
import time


class DBHandler:
    def __init__(self, preferred_db, main_table):
        self.preferred_db = preferred_db  # vertica / duckdb / postgres
        if preferred_db == 'vertica':
            conn_info = {'port': 5433,
                         'host': 'db.example.com',
                         'user': 'username',
                         'password': 'password',
                         'database': 'vdb',
                         'session_label': 'some_label',
                         'read_timeout': 60000,
                         'unicode_error': 'strict',
                         'ssl': False,
                         'use_prepared_statements': False,
                         }
            self.connection = vertica_python.connect(**conn_info)
        if preferred_db == 'postgres':
            CONN_INFO_postgres = {
                'host': 'db.example.com',
                'dbname': 'pdb',
                'user': 'username',
                'password': 'password',
            }
            self.connection = pg.connect(**CONN_INFO_postgres)
        if preferred_db == 'duckdb':
            self.connection = duckdb.connect(database='tequila_db.duckdb',read_only=True)
        
        self.main_table = main_table
        self.cursor = self.connection.cursor()


    def close(self):
        self.cursor.close()
        self.connection.close()

    def create_sql_where_condition_from_value_list(self, values):
        values = [str(x).replace('\'', '') for x in values]
        return "'{}'".format("' , '".join(set(values)))

    def clean_query(self, query):
        return query.replace('AllTables_quadrants', f'{self.main_table}_quadrants').replace('AllTables', f'{self.main_table}')\
            .replace('TableId', 'tableid').replace('ColumnId', 'colid').replace('RowId', 'rowid')\
            .replace('CellValue', 'tokenized').replace('Quadrants', 'quadrants_webtables').replace('QDR', 'quadrant')\
            .replace('COCOA', 'order_index').replace('MATE', 'MATE_index')

    def execute_and_fetchall(self, query):
        """Returns results, execution time, and fetch time"""
        query = self.clean_query(query)

        start_time = time.time()
        self.cursor.execute(query)
        execution_time = time.time() - start_time
        start_time = time.time()
        results = self.cursor.fetchall()
        fetch_time = time.time() - start_time
        return results, execution_time, fetch_time

    