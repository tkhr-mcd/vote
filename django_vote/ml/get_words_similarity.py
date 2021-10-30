import re
import pandas as pd
import numpy as np
from glob import glob
from pathlib import Path
import scipy.spatial as sp
import MeCab
# from janome.tokenizer import Tokenizer
from sklearn.feature_extraction.text import TfidfVectorizer


def _get_cosine_similarity(x, y):
    # cosine類似度　= 1 - cosine距離
    # sp.distance.cosine(x, y)の返り値はcosine距離
    return 1- sp.distance.cosine(x, y)

def remove_URL(x):
    x = re.sub(r"http\S+", "", x)
    return x

def get_words_similarity(search_words, comment_df):
    '''
    検索クエリの文字列と選挙区指定によってDBから得られたcomment_tableデータフレームを渡すと
    検索クエリの文字列と候補者の発言と比較して候補者ランキングと発言ランキングを返します

    parameters
    ----------
    search_words: str
        検索クエリで検索された文字列
    comment_df: pd.DataFrame
         選挙区指定によってDBから得られたcomment_tableでdjango-pandasによってデータフレームに変換されています
    
    Returns
    -------
    candidate_rank: pd.DataFrame 
        search_result.htmlの候補者ランキングで表示させたい候補者ランキングのデータフレームです
    sentence_rank: pd.DataFrame
        search_result.htmlの発言ランキングで表示させたい発言ランキングのデータフレームです
    '''

    this_file_path = Path(__file__)
    parent_dir_path = str(this_file_path.parent.parent.resolve())

    # レコメンドワードに「・」があるため置き換えています
    search_words = search_words.replace('・', '')
    # 文書類似度の比較のためcomment_dfに検索ワードを追加しています
    comment_df = comment_df.append({'serial_id': '', 'name': '', 'sentence':search_words, 'comment': '', 'comment_datetime': ''}, ignore_index=True)
    # 重複削除
    comment_df = comment_df.drop_duplicates()
    # URLを削除
    comment_df['sentence'] = comment_df['sentence'].apply(remove_URL)
    # 形態素解析
    # Mecabで形態素解析
    mecab = MeCab.Tagger(f'-d {parent_dir_path}/mecab-ipadic-neologd')

    sentence_tokenized = []
    for sentence in comment_df['sentence']:
        sentence_tokenized.append(mecab.parse(sentence))

    comment_df['sentence_tokenized'] = sentence_tokenized
    # TF-IDFで特徴量化consider
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    sentence_transformed = vectorizer.fit_transform(comment_df["sentence_tokenized"])

    # numpy.ndarrayに変換しています
    sentence_transformed = sentence_transformed.toarray()

    # コサイン類似度を計算
    sentences_similarity = []
    target_idx = -1

    for i in range(len(sentence_transformed)):
        # cosine類似度　= 1 - cosine距離
        sim = _get_cosine_similarity(sentence_transformed[target_idx], sentence_transformed[i])    
        sentences_similarity.append(sim)
        
    sentences_similarity = np.array(sentences_similarity)
    sentences_similarity = pd.DataFrame(sentences_similarity, columns=['sentences_similarity'])
    comment_df = pd.concat([comment_df, sentences_similarity], axis=1)
    comment_df['sentence'] = comment_df['sentence'].replace('', np.nan)
    comment_df = comment_df.dropna(subset=['sentence'])
    #類似度でソート
    sorted_df = comment_df.sort_values('sentences_similarity', ascending=False)
    # 必要のない列を削除
    sorted_df = sorted_df.drop('sentence_tokenized', axis=1)
    sorted_df['sentences_similarity'] = sorted_df['sentences_similarity'] * 100
    sorted_df['sentences_similarity'] = sorted_df['sentences_similarity'].round(2)

    # 候補者ランキング作成
    # 候補者ごとの発言ランキングデータフレームを作成しています
    candidate_topN = 10 
    df_list = []
    score_list = []
    for _, sdf in sorted_df.groupby('name'):
        sdf = sdf.reset_index(drop=True)
        candidate_score = float(sdf['sentences_similarity'].mean())
        score_list.append(candidate_score)
        df_list.append(sdf)
    # 一番類似度が高い検索ワードがある行をスライスで削除しています
    df_list = df_list[1:]
    score_list = score_list[1:]
    tuple_list =[]
    for score_and_df in zip(score_list, df_list):
        tuple_list.append(score_and_df)
    # タプルの1つめ、類似度の平均値でリストをソートしています
    tuple_list.sort(key=lambda x: x[0], reverse=True)
    candidate_df_list = []
    for score_and_df in tuple_list:
        # 一番上の発言のみ取得します
        candidate_df = pd.DataFrame(score_and_df[1].iloc[0, :]).T 
        candidate_df_list.append(pd.DataFrame(score_and_df[1].iloc[0, :]).T)
    candidate_rank = pd.concat(candidate_df_list, axis=0)

    # 発言ランキング作成
    # トップ5の類似度が高い発言を抽出します
    sentences_topN = 5
    sentence_rank = sorted_df.iloc[1:sentences_topN+1, :]
    sentence_rank = sentence_rank.reset_index(drop=True)
    return candidate_rank, sentence_rank

if __name__ == '__main__':
    search_words = 'インボイス'
    comment_df = pd.read_csv('comment_df.csv')
    candidate_rank, sentence_rank = get_words_similarity(search_words, comment_df)
    print(candidate_rank)