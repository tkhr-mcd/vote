import tweepy
import time
from datetime import timedelta
from datetime import date
import pandas as pd
from pathlib import Path
import logging
import traceback
import sys

def merge_candidate_list():
    '''Summary line.
    入力した都道府県リストを結合しexcelファイルを吐き出す関数

    parameters
    ----------
    なし 

    Returns
    -------
    output_filepath: str(filepath)
        議員情報をまとめたcsvファイルのパス

    '''
    this_file_path = Path(__file__)
    parent_dir = this_file_path.parent.parent.parent.resolve()
    candidate_dir = parent_dir / 'candidate_list' 
    candidate_lists = list(candidate_dir.glob('候補者リスト_*.xlsx'))
    output_dir = parent_dir / 'data' / 'twitter' 
    print(this_file_path)
    print(parent_dir)
    print(candidate_dir)
    print(candidate_lists)
    print(output_dir)

    excel_df_list = []
    for candidate_form_path in candidate_lists:
        # エクセルの各シート名を取得
        bk = pd.ExcelFile(candidate_form_path)
        prefecture_list = bk.sheet_names
        prefecture_df_list = []
        for pre in prefecture_list:
            df = pd.read_excel(candidate_form_path, sheet_name=pre, index_col=0)
            prefecture_df_list.append(df)
        all_pre_df = pd.concat(prefecture_df_list)
        excel_df_list.append(all_pre_df)
    excel_df = pd.concat(excel_df_list)
    today = date.today()
    output_filepath = output_dir / f'{today}_all_congress_info.csv' 
    excel_df.to_csv(output_filepath, encoding='utf_8_sig')
    return output_filepath

def get_user_tweets(csv_filepath):
    '''Summary line.

    都道府県の議員情報のcsvファイルパスを渡すと
    各議員の過去3000ツイートを抽出しcsvファイルを出力します

    parameters
    ----------
    csv_filepath: str(filepath)
        選挙候補者のcsvルファイルのパス
 
    Returns
    -------
    None
        csvを出力するだけなので特に戻り値はない
    '''

    this_file_path = Path(__file__)
    log_file_path = this_file_path.parent / 'get_user_tweets.log'
    parent_dir = this_file_path.parent.parent.parent 
    twitter_dir = parent_dir / 'data' / 'twitter' 

    # log関連
    logger = logging.getLogger(rf'{__name__}.{sys._getframe().f_code.co_name}')
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler(filename=log_file_path, mode='a', encoding='utf-8')
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s %(asctime)s [%(name)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info(rf'start : get_user_tweets(csv_filepath)')
    try:
        all_congress_df = pd.read_csv(csv_filepath)
        # twitterアカウントがないユーザー行を削除
        all_congress_df = all_congress_df[all_congress_df['twitterユーザー名'] != 'なし']


        # 以下、ツイッターのユーザーのタイムライン抽出
        Consumer_key = 'PvgVMOlay7ysZVLnVlDa1MfPu'
        Consumer_secret = 'oKq5Ky7ijm0HDWTukhm1eFDMd4x4R93Cql1FmZLuMqU9pVrojA'
        Access_token = '1188317618618294272-8RVbEMVfEIeBxNAUNnFz3MFKhYLkiz'
        Access_secret = 'g99Fns4WgK8TsGDi76NGVNfAgF6n9NmV5wWYCSx0mlUBa'

        # OAuth認証
        auth = tweepy.OAuthHandler(Consumer_key, Consumer_secret)
        auth.set_access_token(Access_token, Access_secret)
        api = tweepy.API(auth)

        # 抽出する議員名のリスト
        congress_name_list = all_congress_df['議員名'].values.tolist()
        # 抽出する議員のtwitterアカウントのリスト
        account_list = all_congress_df['twitterユーザー名'].values.tolist()

        # ツイート取得
        text_list = []
        created_at_list = []
        name_list = []
        
        # 最大3000件のツイートを取得するためのページ
        pages = list(range(1, 16))
        for account, name in zip(account_list, congress_name_list):
            for page in pages:
                try:
                    results = api.user_timeline(screen_name=account, count=200, page=page)
                    for r in results:
                        #r.textで、投稿の本文のみ取得する
                        text_list.append(r.text)
                        created_at_list.append(r.created_at + timedelta(hours=+9))
                        name_list.append(name)
                except:
                    # アカウント名が間違っていた際にfor文が止めさせたくないため
                    # exceptで例外キャッチしpassで無視して次のforに行くようにしている
                    logger.error(traceback.format_exc())
                    logger.exception(f'{account} does not exist')
                    pass
            time.sleep(60)


        df = pd.DataFrame({'name':name_list, 'text':text_list, 'created_at':created_at_list})
        today = date.today()
        df.to_csv(twitter_dir / f'{today}_tweets.csv', encoding='utf_8_sig')
        logger.info(rf'normal end : get_user_tweets({csv_filepath})の処理が正常終了しました。')
    except:
        traceback.print_exc()
        logger.error(rf'abnormal end : get_user_tweeets({csv_filepath})の処理が異常終了しました。')

if __name__ == '__main__':
    # merge_candidate_list()
    csv_filepath = merge_candidate_list()
    get_user_tweets(csv_filepath)
