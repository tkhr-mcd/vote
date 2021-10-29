import pandas as pd
import numpy as np1
import datetime
import copy
import re
from pathlib import Path
from wordcloud import WordCloud
import MeCab

def make_wordcloud(tweets_csv_path, congress_csv_path):
    '''
    tweetのcsvファイルを渡すと各議員のワードクラウドのイメージファイルを出力する
    aws上ではなくローカルで実行するモジュールです

    parameters
    ----------
    tweets_csv_path: str
        抽出したtwitterのデータのcsvファイルパス
    congress_csv_path: str
        抽出し各文章ごとに整理されたcsvファイルパス
    
    Returns
    -------
    None
    '''    

    this_file_path = Path(__file__)
    wordcloud_filepath  = this_file_path.parent.parent / 'vote' / 'static' / 'vote' / 'wordcloud'
    def preprocess(x):
        # 不要な行, 列のフィルタなど、データサイズを削減する処理
        return x

    reader = pd.read_csv(tweets_csv_path, chunksize=50)
    # tweets_dfのカラムはname, text, created_at 
    tweets_df = pd.concat((preprocess(r) for r in reader), ignore_index=True) 
    # 欠損処理
    tweets_df = tweets_df.dropna(subset=['text'])
    reader = pd.read_csv(congress_csv_path, chunksize=50)
    # congress_dfのカラムはname, sentence, comment, comment_datetime
    congress_df = pd.concat((preprocess(r) for r in reader), ignore_index=True)  
    congress_df = congress_df.rename(columns={'sentence': 'text', 'comment_datetime': 'created_at'})
    congress_df = congress_df.dropna(subset=['text'])
    df = pd.concat([tweets_df, congress_df], join='inner')
    value_counts = df['name'].value_counts()
    value_counts.to_csv('candidate_unique.csv', encoding='utf_8_sig')
    for name, sdf in df.groupby('name'):
        sdf.reset_index(drop=True)
        texts = sdf['text']
        texts_merged = ''.join(texts)
        # macabの準備
        mecab = MeCab.Tagger(f'-d {this_file_path.parent.parent}/mecab-ipadic-neologd')
        mecab.parse('')
        node = mecab.parseToNode(texts_merged)
        # 名詞を取り出す
        word_list = []
        while node:
            word_type = node.feature.split(',')[0]
            if word_type == '名詞':
                word_list.append(node.surface)
            node = node.next
        # リストを文字列に変換
        word_chain = ' '.join(word_list)
        #wordCloudで表示する
        hiragana = ['こちら', 'これ', 'ありません', 'そこ', 'ところ', 'とき', 'それ', 'こと', 'もの', 'ため', 'の', 'よう', 'そう', 'さん', 'たび', 'たくさん', 'みなさん', 'さ', 'お互い', 'おはよう', 'お願い', 'こんばんは', 'かつ', 'ひと']
        english = ['https', 'http','co', '@', 'RT', 't']
        kanji = ['等', '十', '九', '八', '七', '六', '五', '四', '三', '二', '一', '皆さん', '皆様', '本日', '衆議院選挙', '議員', '時間', '衆議院議員', '街頭演説', '選挙戦', '私', '応援', '今日', 'お願い', '大変', '本日', '現在']
        party = ['立憲民主党', '民主党', '自民党', '自由民主党', '共産党', '維新' '党']
        stop_words = hiragana + kanji + english + party
        fpath = "NotoSerifCJKtc-Regular.otf"
        wordcloud = WordCloud(font_path=fpath,
                            background_color='white',
                            stopwords=set(stop_words),
                            collocations=False,
                            width=800,
                            height=600).generate(word_chain)
        #図をフォルダに保存
        wordcloud.to_file(wordcloud_filepath / f'{name}_wordCloud.png')


    
    return None

if __name__ == '__main__':
    this_file_path = Path(__file__)
    tweets_csv_path = this_file_path.parent.parent / 'data' / 'twitter' / '2021-10-29_tweets_mochida.csv'
    congress_csv_path = this_file_path.parent.parent / 'data' / 'congress' /  '2021-10-29_house_member_words.csv'
    make_wordcloud(tweets_csv_path, congress_csv_path)