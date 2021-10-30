import pandas as pd
from pathlib import Path

def concat_data():
    this_file_path = Path(__file__)
    tweets_csv_dir  = this_file_path.parent
    csv_filepath1 = tweets_csv_dir / '2021-10-29_tweets_mochida.csv'
    csv_filepath2 = tweets_csv_dir / '2021-10-29_tweets_sato.csv'
    csv_filepath3 = tweets_csv_dir / '2021-10-30_tweets.csv'

    def preprocess(x):
        # 不要な行, 列のフィルタなど、データサイズを削減する処理
        return x
    # tweets_dfのカラムはname, text, created_at
    reader = pd.read_csv(csv_filepath1, chunksize=50)
    tweets_df1 = pd.concat((preprocess(r) for r in reader), ignore_index=True)
    reader = pd.read_csv(csv_filepath2, chunksize=50)
    tweets_df2 = pd.concat((preprocess(r) for r in reader), ignore_index=True)
    reader = pd.read_csv(csv_filepath3, chunksize=50)
    tweets_df3 = pd.concat((preprocess(r) for r in reader), ignore_index=True)
    df = pd.concat([tweets_df1, tweets_df2, tweets_df3], join='inner')
    df = df.dropna(subset=['text'])

    df.to_csv(tweets_csv_dir / 'all_tweets.csv', index=False)

    return None

if __name__ == '__main__':
    concat_data()