from collections import Counter


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


from  pathlib import Path
import pandas as pd
import numpy as np


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


