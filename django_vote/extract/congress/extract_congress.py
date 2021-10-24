import urllib
import untangle
import urllib.parse
import os
import sys
import re
import time
import glob
import logging
import traceback
import pandas as pd
import numpy as np
from datetime import date
from pathlib import Path

def scrape_congress(filename, name):
    '''Summary line.

    指定した議員の本会議の過去の発言を抽出する

    parameters
    ----------
    filename: str
        抽出した後に発言を保存するテキストファイル名
     name: str
        抽出したい議員の名前
    
    Returns
    -------
    None

    '''

    # 抽出部分
    start = '1'
    i = 0
    Reco = ""
    day = ""
    # 議長リスト
    chairs = ["大島理森","赤松広隆","伊達忠一","郡司彰","山崎正昭","輿石東","川端達夫","金子原二郎","向大野新治","冨岡勉","石田昌宏","郷原悟"] 
    while True:
        name = name
        startdate = '2017-10-01'
        #enddate = '2019-12-31'
        # maxreco = '1000'
        meeting = '本会議'
        # search = '財務'
        url = 'http://kokkai.ndl.go.jp/api/1.0/speech?'+urllib.parse.quote('startRecord=' + start
                                                                           # + '&maximumRecords=' + maxreco
                                                                           + '&speaker=' + name
                                                                           # + '&any=' + search
                                                                           + '&nameOfMeeting=' + meeting
                                                                           + '&from=' + startdate)
                                                                           # + '&until=' + enddate)
        obj = untangle.parse(url)
        art = obj.data.numberOfRecords.cdata
        # 以下ロジックにtry句を入れてエラーハンドリングできるようにする
        # 期間中に発言がない議員の場合はエラーがでてしまうので
        # エラー議員名とエラー内容がlogに保存できるようにする
        for record in obj.data.records.record:
            name = record.recordData.speechRecord.speaker.cdata
            if name == '' or name in chairs:    #発言者なしor議長の場合はパス
                pass
            else:
                speechreco = record.recordData.speechRecord
                if not day == speechreco.date.cdata:
                    Reco += speechreco.date.cdata + "\n"            
                day = speechreco.date.cdata
                reco_line = speechreco.speech.cdata
                Reco += reco_line
        Reco += '\n'

        if not i%500:   #500件超えるならここでカキコ
            with open(filename, 'a') as f:
                f.write(Reco)
            Reco = ""
        try:
            start = obj.data.nextRecordPosition.cdata
        except AttributeError:
            print("おわり")
            break
        i += 100
        print("{0}件中{1}件目".format(art,i))
    return Reco


def read_congress_words(path):
    '''Summary line.

    テキストのパスを指定しstop_wordsをテキストから削除する

    parameters
    ----------
    path: str
        削除したいテキストデータのパス
    
    Returns
    -------
    text: str
        stop_wordsが削除されたテキストデータ
    '''
    
    #パスを指定してテキストデータを読み込んでいます
    f = open(path)
    text = f.read()
    f.close()
    
    # stop_wordsを指定
    stop_words = [ '　', '\n', '（拍手）', '―――――――――――――', '――――◇―――――', '、', '─', '—', '（内閣提出）', '・', '「', '」', '（', '）']

    path = str(path.resolve())

    # 議員名をパスから取り出しています
    name = path[11:]
    name = name[:-4]

    #stop_wordsをテキストから削除しています
    prime_minister = '○内閣総理大臣{}君'.format(name)
    minister = '○国務大臣{}君'.format(name)
    congressman = '○{}君'.format(name)
    vice_chair = '○副議長{}君'.format(name)
    stop_words.extend([prime_minister, minister, congressman, vice_chair])
    for word in stop_words:
        text = text.replace(word, '')

    # 正規表現に合致した文字を削除する
    stop_words = ['\d{4}-\d{2}-\d{2}', '〔[一-龥ぁ-んァ-ン]+〕']
    for word in stop_words:
        text = re.sub(word, '', text)
    return text, name


def extract_all_congress():
    '''Summary line.
    エクセルで指定した議員すべての発言を抽出する

    parameters
    ----------
    なし

    Returns
    -------
    なし

    '''
    this_file_path = Path(__file__)
    log_file_path = this_file_path.parent / 'extract_congress.log'

    # log関連
    logger = logging.getLogger(rf'{__name__}.{sys._getframe().f_code.co_name}')
    logger.setLevel(logging.DEBUG)
    ch = logging.FileHandler(filename=log_file_path, mode='a', encoding='utf-8')
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s %(asctime)s [%(name)s] %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info(rf'start : extract_congress()')
    try:
        house_member = pd.read_excel(this_file_path.parent / '議員一覧.xlsx', sheet_name='衆議院')

        member_files_path = []
        for name in house_member['氏名']:
            path =this_file_path.parent / f'congress_words/words_{name}.txt'
            member_files_path.append(path)
            f = open(path, 'w')
            f.close()
            try:
                r = scrape_congress(path, name)
            except:
                logger.error(traceback.format_exc())
                logger.exception(f'{name} do not have words')
                pass
            try:
                with open(path, 'a') as f: #残りをかきこ
                    f.write(r)
            except:
                logger.error(traceback.format_exc())
                pass
            time.sleep(60)
            print(f'{name}の発言を抽出しました。')

        # 議員の発言をラベルとして1文ずつ抽出しデータフレーム化
        parent_dir = this_file_path.parent.resolve()
        member_files = list(this_file_path.parent.glob('congress_words/*.txt'))

        # パスの順番に衆議院議員の名前をリスト化
        # member_names = []
        # for member_file in member_files:
        #     member_file = str(member_file).split(r'/')[-1]
        #     # 11と-4はファイル名の名前部分のみを抽出するために指定しています
        #     member_file = member_file[11:]
        #     member_file = member_file[:-4]
        #     member_names.append(member_file)

        # 衆議院議員の発言を抽出してstop_wordsを削除してデータフレームに追加しています。
        df = pd.DataFrame({'name':[],
                        'sentence':[]})

        for path in member_files:
            text, name = read_congress_words(path)
            sentence_list = text.split('。')
            for sentence in sentence_list:
                series = pd.Series([name, sentence], index=df.columns)
                df = df.append(series, ignore_index=True)
        # 欠損処理
        df['sentence'] = df['sentence'].replace('', np.nan)
        df = df.dropna(subset=['sentence'])

        # 重複処理
        df = df.drop_duplicates()

        df = df.reset_index(drop=True)
        today = date.today()
        # csvデータとして衆議院議員の発言を出力しています
        df.to_csv(this_file_path.parent / f'{today}_house_member_words.csv', index=False, encoding='utf_8_sig')
        logger.info(rf'normal end : extract_congress()の処理が正常終了しました。')
    except:
        traceback.print_exc()
        logger.error(rf'abnormal end : extract_congress()の処理が異常終了しました。')

if __name__ == '__main__':
    '''
    scrape_congressの正常テスト
    '''
    ''' 
    name = '青柳陽一郎'
    date = date.today()
    filename = f'{date}_{name}.txt'
    r = scrape_congress(filename, name)
    #残りをかきこ
    with open(filename, 'a') as f:
        f.write(r)
    '''
    '''
    extract_congressの通常テスト
    '''
    extract_all_congress()