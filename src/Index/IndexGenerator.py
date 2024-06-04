def calculate_xash(token: str, hash_size: int = 128) -> int:
    """Calculates the XASH hash of a token."""

    number_of_ones = 5
    char = [
        " ", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f", "g", "h", "i",
        "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
    ]

    segment_size_dict = {64: 1, 128: 3, 256: 6, 512: 13}
    segment_size = segment_size_dict[hash_size]

    n_bits_for_chars = 37 * segment_size
    length_bit_start = n_bits_for_chars
    n_bits_for_length = hash_size - length_bit_start
    token_size = len(token)

    # - Character position encoding
    result = 0
    # Pick the 5 most infrequent characters
    counts = Counter(token).items()
    sorted_counts = sorted(counts, key=lambda char_occurances: char_occurances[::-1])
    selected_chars = [char for char, _ in sorted_counts[:number_of_ones]]
    # Encode the position of the 5 most infrequent characters
    for c in selected_chars:
        if c not in char:
            continue
        # Calculate the mean position of the character and set the one bit in the corresponding segment
        indices = [i for i, ltr in enumerate(token) if ltr == c]
        mean_index = sum(indices) / len(indices)
        normalized_mean_index = mean_index / token_size
        segment = max(int(normalized_mean_index * segment_size - 1e-6), 0)  # Legacy fix
        location = char.index(c) * segment_size + segment
        result = result | 2**location

    # Rotate position encoding
    shift_distance = (
        length_bit_start
        * (token_size % (hash_size - length_bit_start))
        // (hash_size - length_bit_start)
    )
    left_bits = result << shift_distance
    wrapped_bits = result >> (n_bits_for_chars - shift_distance)
    cut_overlapping_bits = 2**n_bits_for_chars

    result = (left_bits | wrapped_bits) % cut_overlapping_bits

    # - Add length bit
    length_bit = 1 << (length_bit_start + token_size % n_bits_for_length)
    result = result | length_bit

    return result
from typing import List, Callable, Type

import vertica_python as vp
import psycopg as pg
import pandas as pd
import multiprocessing
from functools import partial
from tqdm import tqdm
from chunk import Chunk
import pickle
from collections import defaultdict, Counter

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
                
                with cursor.copy("COPY " + result_table_name + "(tokenized, tableid, colid, rowid, super_key, quadrant) FROM STDIN WITH CSV ESCAPE '\\'") as copy_cursor:
                    copy_cursor.write(csv)
                con.commit()

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
    # cursor.execute(f"""
    #                CREATE TABLE IF NOT EXISTS
    #                {result_table_name}(
    #                     CellValue varchar(200),
    #                     TableId INT,
    #                     ColumnId INT,
    #                     RowId INT,
    #                     SuperKey BINARY(16),
    #                     Quadrant BOOLEAN
    #                );
    #                """)


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


from Chunks import GitChunk, DresdenChunk
import configparser
def main():
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    vertica_con = pg.connect(
                host=config['Database']['host'],
                port=5432,
                user="postgres",
                password=config['Database']['password'],
                dbname="pdb",
            )

    
            

    # ------------------------ Blend ------------------------
    map_chunks(vertica_con, 'gittables_1m_main_tokenized', GitChunk, GitChunk.get_chunk_labels(), callback=df_to_index)
    
def df_to_index(df: pd.DataFrame) -> pd.DataFrame:
    tableid = int(df.columns.name)

    numeric_cols = df.select_dtypes(include='number').columns
    numeric_cols = [df.columns.get_loc(col) for col in numeric_cols]
    
    file_content = df.values
    number_of_rows = file_content.shape[0]
    number_of_cols = file_content.shape[1]
    

    superkeys = defaultdict(int)
    new_data = []
    for col_counter in range(number_of_cols):
        is_numeric_col = col_counter in numeric_cols
        if is_numeric_col:
            mean = df.iloc[:, col_counter].mean()
        for row_counter in range(number_of_rows):
            tokenized = str(file_content[row_counter][col_counter]).lower().replace('\\', '').replace('\'', '').replace('\"', '').replace('\t', '').replace('\n', '').replace('\r', '').strip()[:200]
            if tokenized == 'nan' or tokenized == 'none':
                tokenized = ''
            quadrant = file_content[row_counter][col_counter] >= mean if is_numeric_col else None
            new_data.append((tokenized, tableid, col_counter, row_counter, quadrant))
            superkeys[row_counter] = superkeys[row_counter] | calculate_xash(str(tokenized))
    

    superkeys_as_binary = {key: f"{superkey:0128b}" for key, superkey in superkeys.items()}
    new_data = [(x[0], x[1], x[2], x[3], superkeys_as_binary[x[3]], x[4]) for x in new_data]

    return pd.DataFrame(new_data, columns=['CellValue', 'TableId', 'ColumnId', 'RowId', 'SuperKey', 'Quadrant'])

if __name__ == '__main__':
    main()





