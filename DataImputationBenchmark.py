from glob import glob
import pandas as pd
import time
from tqdm import tqdm
import re

from src.Tasks.DataImputation import DataImputation
from src.utils import Logger


def get_cleaned_text(text):
    if text is None:
        return ''
    stopwords = ['a','the','of','on','in','an','and','is','at','are','as','be','but','by','for','it','no','not','or'
        ,'such','that','their','there','these','to','was','with','they','will',  'v', 've', 'd']

    cleaned = re.sub('[\W_]+', ' ', text.encode('ascii', 'ignore').decode('ascii'))
    feature_one = re.sub(' +', ' ', cleaned).strip()

    for x in stopwords:
        feature_one = feature_one.replace(' {} '.format(x), ' ')
        if feature_one.startswith('{} '.format(x)):
            feature_one = feature_one[len('{} '.format(x)):]
        if feature_one.endswith(' {}'.format(x)):
            feature_one = feature_one[:-len(' {}'.format(x))]
    return feature_one


def main():
    k = 10
    logger = Logger(clear_logs=True)
    query_path = 'data/benchmarks/DataImputation/gittables_benchmark/*.csv'


    counter = 0
    for file_path in tqdm(list(sorted(glob(query_path)))):
        counter += 1
        df = pd.read_csv(file_path, header=None).astype(str)
        if len(df) > 5:
            example_df = df.head(5).iloc[:, : 2]
            query_values = df.iloc[5:, :][df.columns.values[0]]
        elif len(df) < 5 and len(df) > 2:
            example_df = df.head(2).iloc[:, : 2]
            query_values = df.iloc[2:, :][df.columns.values[0]]
        elif len(df) == 2:
            example_df = df.head(1).iloc[:, : 2]
            query_values = df.iloc[1:, :][df.columns.values[0]]
        elif len(df) < 2:
            continue
        size = len(query_values)
        if size == 0:
            continue


        task = DataImputation(example_df, query_values, k=k)
        task.DB.index_table = 'gittables_quadrants'
        start = time.time()
        result_ids = task.run()
        end = time.time()
        task.DB.close()

        logger.log(
            "DataImputation",
            dict(
                runtime=end - start,
                result_ids=str(result_ids),
                result_size=len(result_ids),
                query_path=file_path,
            )
        )




if __name__ == '__main__':
    main()