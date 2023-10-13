from collections import Counter
from  pathlib import Path
import pandas as pd
from collections import defaultdict
import numpy as np

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
            tokenized = str(file_content[row_counter][col_counter]).lower().replace('\\', '').replace('\'', '').replace('\"', '').replace('\t', '').replace('\n', '').replace('\r', '')[:200]
            if tokenized == 'nan' or tokenized == 'none':
                tokenized = ''
            quadrant = file_content[row_counter][col_counter] >= mean if is_numeric_col else None
            new_data.append((tokenized, tableid, col_counter, row_counter, quadrant))
            superkeys[row_counter] = superkeys[row_counter] | calculate_xash(str(tokenized))
    

    superkeys_as_binary = {key: f"0x{superkey:032x}" for key, superkey in superkeys.items()}
    new_data = [(x[0], x[1], x[2], x[3], superkeys_as_binary[x[3]], x[4]) for x in new_data]

    return pd.DataFrame(new_data, columns=['CellValue', 'TableId', 'ColumnId', 'RowId', 'SuperKey', 'Quadrant'])


class Logger(object):
    def __init__(self, logging_path='logs/', clear_logs=False):
        self.logging_path = Path(logging_path)
        self.logging_path.mkdir(parents=True, exist_ok=True)

        print("Logger using path: ", self.logging_path.absolute(), end='\n\n')
        self.used_logs = dict()
        self.clear_logs = clear_logs

    def _open_log(self, logname):
        if logname in self.used_logs:
            return
        
        fp = self.logging_path / f"{logname}.csv"
        if not fp.exists():
            self.used_logs[logname] = pd.DataFrame()
        else:
            self.used_logs[logname] = pd.read_csv(fp, sep=',')

    def log(self, logname, data):
        if logname not in self.used_logs:
            if self.clear_logs:
                self.used_logs[logname] = pd.DataFrame(columns=data.keys())
            else:
                self._open_log(logname)
            
        self.used_logs[logname] = pd.concat([self.used_logs[logname], pd.DataFrame(data, index=[0])], ignore_index=True)
        self.used_logs[logname].to_csv(self.logging_path / f"{logname}.csv", sep=',', index=False)

    def read_average_log(self, logname, metric_to_read, k):
        self._open_log(logname)
        df = self.used_logs[logname]
        df = df[df['k'] == k]
        vals = df[metric_to_read]

        print(vals.describe())

    def describe_log(self, logname):
        self._open_log(logname)
        df = self.used_logs[logname]

        print(df.describe())


