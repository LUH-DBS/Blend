from tqdm import tqdm
import pandas as pd
import numpy as np
from glob import glob
import vertica_python
import math
from collections import Counter, defaultdict
from io import StringIO
from src.utils import calculate_xash


def create_table_and_projections(dbcon, table_name):
    print('Preparing index creation by creating tables in DB.')
    with dbcon.cursor() as cur:
        cur.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')

        cur.execute(f"""CREATE TABLE {table_name} (
            tokenized varchar(200), 
            tableid INT,
            colid INT,
            rowid INT, 
            superkey BINARY(16),
            quadrant BOOLEAN
            );""")
        
        cur.execute(f"""
            CREATE PROJECTION {table_name}_to_tokenized(tokenized, tableid, colid, rowid, super_key, quadrant)
            AS SELECT *
            FROM {table_name}
            ORDER BY tokenized, tableid, colid, rowid
            SEGMENTED BY hash(tokenized) ALL NODES;
        """);

        cur.execute(f"""
            CREATE PROJECTION {table_name}_to_tableid(tokenized, tableid, colid, rowid, super_key, quadrant)
            AS SELECT *
            FROM {table_name}
            ORDER BY tableid, colid, rowid
            SEGMENTED BY hash(tableid) ALL NODES;
        """);

    print(f'Preparation of index creation is finished!')


def save_data_to_vertica(dbcon, data, table_name):
    df = pd.DataFrame(data, columns=['tokenized', 'tableid', 'colid', 'rowid', 'superkey', 'quadrant'])
    # Copy to temporary csv file
    with StringIO() as temp:
        df.to_csv(temp, index=False, header=False)
        temp.seek(0)
        # Copy to vertica
        with dbcon.cursor() as cur:
            cur.copy(f"COPY {table_name} (tokenized, tableid, colid, rowid, superkey FORMAT 'bitstring', quadrant) FROM STDIN DELIMITER ',' ENCLOSED BY '\"' ESCAPE AS '\\' NULL '' REJECTED DATA AS TABLE {table_name}_rejected", temp)
    


def create_index(dbcon, lake_path, table_name, sep=','):
    create_table_and_projections(dbcon, table_name)
    print('Inserting data into index.')
    data = []
    for table_counter, file_path in tqdm(list(enumerate(sorted(glob(f'{lake_path}'))))):
        file_content_df = pd.read_csv(file_path, sep=sep, low_memory=False)
        numeric_cols = file_content_df.select_dtypes(include='number').columns
        numeric_cols = [file_content_df.columns.get_loc(col) for col in numeric_cols]
        
        file_content = file_content_df.values
        number_of_rows = file_content.shape[0]
        number_of_cols = file_content.shape[1]
        
        pbar = None
        if number_of_cols * number_of_rows > 1000000:
            pbar =  tqdm(total=number_of_cols * number_of_rows, leave=False)

        superkeys = defaultdict(int)
        new_data = []
        for col_counter in range(number_of_cols):
            is_numeric_col = col_counter in numeric_cols
            if is_numeric_col:
                mean = np.nanmean(file_content[:, col_counter])
            for row_counter in range(number_of_rows):
                tokenized = str(file_content[row_counter][col_counter]).lower().replace('\\', '').replace('\'', '').replace('\"', '').replace('\t', '').replace('\n', '').replace('\r', '')[0:200]
                if tokenized == 'nan' or tokenized == 'none':
                    tokenized = ''
                quadrant = file_content[row_counter][col_counter] >= mean if is_numeric_col else None
                new_data.append((tokenized, table_counter, col_counter, row_counter, quadrant))
                superkeys[row_counter] = superkeys[row_counter] | calculate_xash(str(tokenized))
                if pbar: pbar.update(1)
        

        superkeys_as_binary = {key: f"{superkey:0128b}" for key, superkey in superkeys.items()}
        data.extend([(x[0], x[1], x[2], x[3], superkeys_as_binary[x[3]], x[4]) for x in new_data])
        if len(data) >= 3500000:
            save_data_to_vertica(dbcon, data, table_name)
            data = []
        
        if pbar: pbar.close()
                
    if len(data) > 0:
        save_data_to_vertica(dbcon, data, table_name)
    
    print(f'Insertion of the index is Finished!')
    



PATH = 'data/*.csv'
INDEX_NAME = 'blend_index'

dbcon = vertica_python.connect(
        port=5433,
        host='db.example.com',
        user='username',
        password='password',
        database='vdb',
        session_label='some_label',
        read_timeout=60000,
        unicode_error='strict',
        ssl=False,
        use_prepared_statements=False
)


create_index(dbcon, PATH, INDEX_NAME)


dbcon.close()
