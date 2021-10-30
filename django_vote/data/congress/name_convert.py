import pandas as pd
import numpy as np
from pathlib import Path


def name_convert():
    this_file_path = Path(__file__)
    congress_csv_dir  = this_file_path.parent
    csv_filepath1 = congress_csv_dir / '2021-10-28_house_member_words.csv'
    csv_filepath2 = congress_csv_dir / '2021-10-29_house_member_words.csv'

    def preprocess(x):
        # 不要な行, 列のフィルタなど、データサイズを削減する処理
        return x

    reader = pd.read_csv(csv_filepath1, chunksize=50)
    # congress_dfのカラムはname, sentence, comment, comment_datetime
    congress_df1 = pd.concat((preprocess(r) for r in reader), ignore_index=True)
    
    reader = pd.read_csv(csv_filepath2, chunksize=50)
    # congress_dfのカラムはname, sentence, comment, comment_datetime
    congress_df2 = pd.concat((preprocess(r) for r in reader), ignore_index=True)
    
    df = pd.concat([congress_df1, congress_df2], join='inner')
    df = df.replace({'sentence': {'2020/1/24': np.nan,
                                '2020/4/27':np.nan,
                                '2020/1/23':np.nan}})
    df = df.dropna(subset=['sentence'])
    df = df.dropna(subset=['name'])
    df = df.replace({'name': {'あべ俊子':'阿部俊子',
                    'あかま二郎':'赤間二郎', 
                    '\u3000':'', 
                     'うえの賢一郎':'上野賢一郎',
                     'とかしきなおみ':'渡嘉敷奈緒美',
                     '岡本あき子':'岡本章子', 
                     '山本ともひろ':'山本朋広',
                      }})

    df.to_csv(congress_csv_dir / 'all_member_words.csv', index=False)




    
    return None

if __name__ == '__main__':
    name_convert()