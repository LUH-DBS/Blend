from src.Plan import Plan

import random
from pathlib import Path
from collections import Counter
from tqdm import tqdm


def main():
    plan = Plan()
    plan.DB.index_table = "santos_small_blend"
    NUMBER_OF_TABLES = 549 + 1

    ouput_folder = Path("santos_small_blend")
    ouput_folder.mkdir(parents=True, exist_ok=True)

    for i in tqdm(range(NUMBER_OF_TABLES)):
        df = plan.DB.get_table_from_index(str(i))
        df.to_csv(ouput_folder / (str(i) + ".csv"), index=False)



if __name__ == "__main__":
    main()
