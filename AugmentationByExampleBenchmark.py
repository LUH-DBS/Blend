from src.utils import Logger
from src.Tasks.AugmentationByExample import AugmentationByExample

import configparser
from tqdm import tqdm
import time
import pandas as pd
import os
from pathlib import Path
from collections import Counter

# Typing imports
from typing import List, Tuple



def count_intersection(df1: pd.DataFrame, df2: pd.DataFrame) -> int:
    # Counts the number of rows that are in both dataframes
    assert len(df1.columns) == len(df2.columns)

    df1 = df1.drop_duplicates().reset_index(drop=True)
    df1.columns = [0, 1]
    df2 = df2.drop_duplicates().reset_index(drop=True)
    df2.columns = [0, 1]

    concatenated = pd.concat([df1, df2], ignore_index=True)
    concatenated = concatenated.drop_duplicates()

    return len(df1) + len(df2) - len(concatenated)


def find_mapping(result: pd.DataFrame, examples: pd.DataFrame, inputs: List[str]) -> pd.DataFrame:
    # Find input column
    number_of_inputs = Counter()
    for column in result.columns:
        number_of_inputs[column] = result[column].isin(inputs).sum()
    input_column = number_of_inputs.most_common(1)[0][0]

    # Find output column that aligns with examples
    number_of_examples = Counter()
    for column in result.columns:
        if column == input_column:
            continue
        mapping = result[[input_column, column]].dropna().drop_duplicates()
        number_of_examples[column] = count_intersection(mapping, examples)

    output_column = number_of_examples.most_common(1)[0][0]

    mapping = result[[input_column, output_column]].dropna().drop_duplicates()
    mapping = mapping[mapping.iloc[:, 0].isin(inputs)].reset_index(drop=True)

    mapping.columns = [0, 1]
    return mapping



def get_precision_and_recall(discovered_mapping: pd.DataFrame, ground_truth: pd.DataFrame) -> Tuple[float, float]:
    

    # Find precision and recall
    correct = count_intersection(discovered_mapping, ground_truth)
    found_inputs = discovered_mapping.iloc[:, 0].unique().size
    precision = correct / found_inputs
    recall = correct / len(ground_truth)

    if correct == 0:
        raise ValueError("No correct results found but there should at least be one!")

    return precision, recall






def run(config_name: str) -> None:
    config = configparser.ConfigParser()
    config.read(f'data/benchmarks/AugmentationByExample/{config_name}.ini')

    logger = Logger(clear_logs=True)
    log_name = config["Benchmark"]["log_name"]
    
    k = int(config["Benchmark"]["k"].strip())
    query_folder = Path(config["Benchmark"]["queries"].strip())
    ground_truth_folder = Path(config["Benchmark"]["ground_truth"].strip())
    
    print("Running for k = ", k)
    for query_id, query_path in tqdm(list(enumerate(sorted(query_folder.glob('*'))))):
        skip = True
        for whiteitem in ['PoundsToKg', 'AthletesHoldingWorldRecordsPerCountry', 'CountryToAreaSqKM', 'ZipToCity', 'CountryToThreeLettersISOCode', 'CountryToLanguage', 'EnglishToGerman', 'City2TallBuildings', 'SoccerPlayer2NationalTeam', 'CityToZIp', 'TeamToManager', 'WorldRecordToAthlete', 'CompanyToCeo', 'shoesizeUSEUR', 'StateToAbbrv', 'fahrenheitToCelcius', 'CUSIPToCompanyName', 'airportToCountry', 'CountryToTwoLettersISOCode', 'USStandardToMetric', 'CityToCountry', 'SymbolToCompanyName', 'Country2UnescoSites', 'RegionToAreaCode_Single', 'USDQAR', 'MountainsOver7k2Range', 'Author2Novels', 'MountainsOver7k2meters', 'Driver2Champioships', 'CompanyToIndustry', 'TeamToCoach', 'BankToSwiftCode', 'RGBToColor', 'ZipToState']:
            if whiteitem in query_path.stem:
                skip = False
        if skip:
            continue

        # if 'CompanyToCeo' not in query_path.stem:
        #     continue

        query = pd.read_csv(query_path)
        ground_truth = pd.read_csv(ground_truth_folder / query_path.name).apply(lambda x: x.astype(str).str.lower()).reset_index(drop=True)
        examples = query[query.iloc[:, 1].notnull()].apply(lambda x: x.astype(str).str.lower()).reset_index(drop=True)
        inputs = query.iloc[:, 0].apply(lambda x: str(x).lower()).values.tolist()
        task = AugmentationByExample(examples, inputs, k)
        task.DB.load_config(config["Benchmark"]["database_config"])
        task.DB.index_table = config["Benchmark"]["index_table"]

        start = time.time()
        try:
            results = task.run()
        except Exception as e:
            print(e)
            continue
        time_to_result = time.time() - start

        partial_mappings = []
        for result_id in results:
            result = task.DB.get_table_from_index(result_id)
            partial_mapping = find_mapping(result, examples, inputs)
            partial_mappings.append(partial_mapping)

        if results:
            found_mapping = pd.concat(partial_mappings, ignore_index=True).drop_duplicates()
            precision, recall = get_precision_and_recall(found_mapping, ground_truth)
        else:
            precision, recall = 0, 0

        # print('-------------------------------------------------')
        # print('-------------------------------------------------')
        # print(query_path)
        # print(results)
        # print(recall)
        # print('-------------------------------------------------')
        
        task.DB.close()
        
        logger.log(log_name, {
            "query_id": query_id,
            "query_name": query_path.stem,
            "precision": precision,
            "recall": recall,
            "f1": 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0,
            "k": k,
            "time": time_to_result,
            "results": str(results),
            "number_of_results": len(results),
        })
        
                    

if __name__ == '__main__':
    run("EX5_Vertica")
