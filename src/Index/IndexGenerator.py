from typing import List, Callable, Type

import vertica_python as vp
import pandas as pd
import multiprocessing
from functools import partial
from tqdm import tqdm
from chunk import Chunk
from src.utils import df_to_index
import pickle

process_unique_zipfile = None
def chunk2result(callback: Callable[[pd.DataFrame], pd.DataFrame], part: any) -> pd.DataFrame:
    global process_unique_chunk
    df = process_unique_chunk.get_part(part)
    if df is not None:
        try:
            return callback(df)
        except Exception as e:
            print(df.columns.name, e)
            return None
    return None


def init_worker(chunk_cls: Type[Chunk], chunk_label: any, start: int) -> None:
    global process_unique_chunk
    process_unique_chunk = chunk_cls(chunk_label)
    process_unique_chunk.set_start(start)


def process_chunk(con: vp.Connection, result_table_name: str, chunk_cls: Type[Chunk], chunk_label: any, callback: Callable[[pd.DataFrame], pd.DataFrame], cache_and_store_limit: int, num_of_tables: int):
    with chunk_cls(chunk_label) as chunk:
        parts = chunk.get_part_labels()

    with multiprocessing.Pool(
            processes=multiprocessing.cpu_count() // 4,
            initializer=init_worker,
            initargs=(chunk_cls, chunk_label, num_of_tables)
    ) as pool:
        cursor = con.cursor()
        def cache_and_store(item: pd.DataFrame,  limit: int, last: bool = False, item_cache: List[pd.DataFrame]=[]):
            if item is not None and not item.empty:
                item_cache.append(item)
            if sum(len(item) for item in item_cache) > limit or (last and sum(len(item) for item in item_cache) > 0):
                result_merged_df = pd.concat(item_cache, axis=0)
                if result_merged_df.empty:
                    return
                
                csv = result_merged_df.to_csv(index=False, header=False, escapechar='\\')
                
                cursor.copy(f"COPY {result_table_name} (CellValue, Tableid, ColumnId, RowId, SuperKey FORMAT 'hex', Quadrant) FROM STDIN DELIMITER ',' ENCLOSED BY '\"' ESCAPE AS '\\' NULL '' REJECTED DATA AS TABLE {result_table_name}_rejected", csv)
                item_cache.clear()

    
        for result_table_df in tqdm(pool.imap_unordered(partial(chunk2result, callback), parts, chunksize=16), total=len(parts), leave=False):
            if result_table_df is None:
                continue
            cache_and_store(result_table_df, limit=cache_and_store_limit)
        cache_and_store(None, limit=cache_and_store_limit, last=True)

    



def map_chunks(con: vp.Connection,
              result_table_name: str,
              chunk_cls: Type[Chunk],
              chunks: List[any],
              callback: Callable[[pd.DataFrame], pd.DataFrame],
              cache_and_store_limit: int = 300000,
              ):
    """
    :param con: Vertica connection that the result table will be inserted into
    :param result_table_name: Name of the result table
    :param chunk_cls: Chunk class that is used to load the data
    :param chunks: List of chunks to be loaded
    :param parts: List of parts to be loaded
    :param cache_and_store_limit: Limit for the cache_and_store item cache size
    :param callback: Callback function that takes a DataFrame and returns a DataFrame
    """

    # Create table for inverted index results
    cursor = con.cursor()
    cursor.execute(f"""
                   CREATE TABLE IF NOT EXISTS
                   {result_table_name}(
                        CellValue varchar(200),
                        TableId INT,
                        ColumnId INT,
                        RowId INT,
                        SuperKey BINARY(16),
                        Quadrant BOOLEAN
                   );
                   """)


    # For all chunks calculate the results in parallel (parallelization by table file)
    print('Calculating results...')
    
    chunk_to_id = {}
    num_of_tables = 0 # Number of tables processed so far
    for chunk_label in tqdm(chunks):
        num_of_parts = len(chunk_cls(chunk_label).get_part_labels())
        chunk_to_id[chunk_label] = num_of_tables
        process_chunk(con, result_table_name, chunk_cls, chunk_label, callback, cache_and_store_limit, num_of_tables)
        num_of_tables += num_of_parts
        with open(f'{result_table_name}_ids.pkl', 'wb') as f:
            pickle.dump(chunk_to_id, f)


from src.Index.Chunks import GitChunk, DresdenChunk
import configparser
def main():
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    conn_info = dict(
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
    vertica_con = vp.connect(**conn_info)
            

    # ------------------------ Blend ------------------------
    map_chunks(vertica_con, 'gittables_runtime_test', GitChunk, GitChunk.get_chunk_labels(), callback=df_to_index)
    


if __name__ == '__main__':
    main()
