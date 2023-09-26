from src.utils import Logger
import configparser
from src.Tasks.UnionSearch import UnionSearch
from tqdm import tqdm
import time
import pandas as pd
import os

def run(config_name):
    config = configparser.ConfigParser()
    config.read(f'data/benchmarks/Union/{config_name}.ini')

    logger = Logger(clear_logs=True)
    log_name_template = config["Benchmark"]["log_name"]
    
    ks = map(int, config["Benchmark"]["ks"].strip().split())
    path = config["Benchmark"]["path"].strip()
    query_paths = os.listdir(path)
    
    for k in ks:
        print("Running for k = ", k)
        log_name = log_name_template.format(k)
        for query_id, query_path in tqdm(list(enumerate(sorted(query_paths)))):
            query = pd.read_csv(path + "/" + query_path, sep=",").apply(lambda x: x.astype(str).str.lower())
            task = UnionSearch(query, k)
            task.DB.load_config(config["Benchmark"]["database_config"])
            task.DB.index_table = config["Benchmark"]["index_table"]

            start = time.time()
            results = task.run()
            time_to_result = time.time() - start

            if results is None or results == []:
                print("No results for query: ", query_path)
                print(query.head())
                exit()
            
            
            logger.log(log_name, {
                "query_id": query_id,
                "k": k,
                "time": time_to_result,
                "results": len(results)
            })
        
                    

if __name__ == '__main__':
    run("TUS_Small_Vertica")
