from src.utils import Logger
import configparser
import pickle
from src.Tasks.SingleColumnJoinSearch import SingleColumnJoinSearch
from src.Tasks.KeywordSearch import KeywordSearch
from tqdm import tqdm
import time

def run(config_name):
    config = configparser.ConfigParser()
    config.read(f'data/benchmarks/SC/{config_name}.ini')

    logger = Logger()
    log_name_template = config["Benchmark"]["log_name"]
    
    ks = config["Benchmark"]["ks"].strip().split()
    sizes = config["Benchmark"]["sizes"].strip().split()
    paths = config["Benchmark"]["paths"].strip()

    for query_set_size in sizes:
        path = paths.format(query_set_size)
        with open(path, 'rb') as f:
            queries = pickle.load(f)
        for k in ks:
            print("Running for k = ", k, " and query set size = ", query_set_size, "...")
            log_name = log_name_template.format(query_set_size, k)
            for query_id, query in tqdm(list(enumerate(queries))):
                if config.has_option("Benchmark", "column_agnostic") and config["Benchmark"]["column_agnostic"].lower() == "true":
                    task = KeywordSearch(query, k)
                else:
                    task = SingleColumnJoinSearch(query, k)
                task.DB.load_config(config["Benchmark"]["database_config"])
                task.DB.index_table = config["Benchmark"]["index_table"]

                start = time.time()
                results = task.run()
                time_to_result = time.time() - start

                if results is None or results == []:
                    print("No results for query: ", query_id)
                
                
                logger.log(log_name, {
                    "query_id": query_id,
                    "k": k,
                    "time": time_to_result,
                    "results": len(results)
                })
            
                        

if __name__ == '__main__':
    run("SC_Opendata_Vertica")