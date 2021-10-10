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

def _remove_stop_words(text, stop_words):
    '''
    ■概要：テキスト内の正規表現に合致する文字を削除する
    '''
    for word in stop_words:
        text = re.sub(word, '', text)
    return text

def _remove_stop_words2(text, stop_words):
    '''
    ■概要：テキスト内のストップワードを削除する
    '''
    for word in stop_words:
        text = text.replace(word, '')
    return text

def _get_surfaces(text):
    '''
    ■概要：janomeを使用する際に単語をとりだす関数
    '''
    # janomeで形態素解析
    t = Tokenizer(wakati=False)
    result = []
    for token in t.tokenize(text):
        partOfSpeech = token.part_of_speech.split(',')[0]
        #part_of_speechの一番最初が品詞になっているため[0]を指定している
        if partOfSpeech in ['名詞']:
        #名詞だけを使う、前回はnot inで助詞、助動詞を削除した
            result.append(token.surface)
    return " ".join(result)


def get_words_similarity(search_words):
    '''
    ◯概要
     - 検索ワードと議員の発言にどれだけ関連性があるのかを判断する
    ◯引数
     - words(str): 検索値 
    ◯戻り値
        - similarity_scores(DataFrame): 議題と類似度の高い発言と議員名と類似度のpandas.DataFrameデータ
    }
    '''
    # テキストデータの読み込み
    this_filepath = Path(__file__)
    congress_words_dir = this_filepath.resolve().parent.parent / 'data' / 'all_congress_words'
    text_path_list = list(congress_words_dir.glob('*.txt'))

    # 議員名のリストを作成
    name_list = []
    # 発言のリストを作成
    word_list = []
    for path_list in text_path_list:
        # 議員名を取得
        path_list = str(path_list)
        text_filename = path_list.split('_')[-1]
        name_list.append(text_filename[:-4])
        # 発言を取得
        f = open(path_list)
        text = f.read()
        f.close()
        word_list.append(text)
    # 正規表現に合致した文字を削除する
    # パターンとしては順に「日付」、議事最後の登壇などの状況説明文書、大臣の発言の議事最初のラベル、通常議員の発言の議事最初のラベル
    stop_words = ['\d{4}-\d{2}-\d{2}', '〔[一-龥ぁ-んァ-ン]+〕', '○([ぁ-んァ-ン一-龥]+)（([ぁ-んァ-ン一-龥]+)君）', '○([ぁ-んァ-ン一-龥]+)君']

    # 適当な文字を設定、ストップワードで消す
    stop_words2 = ['　', r'\n', r'\u3000','（拍手）', '―――――――――――――', '――――◇―――――', '、', '─', '—', '（内閣提出）', '・', '「', '」', '（', '）', '\n', '\u3000']

    # ストップワードで余分な文字を削除
    for idx, _ in enumerate(word_list):
        word_list[idx] = _remove_stop_words(text=word_list[idx], stop_words=stop_words)
        word_list[idx] = _remove_stop_words2(text=word_list[idx], stop_words=stop_words2)

    # データフレーム化
    df = pd.DataFrame(columns=['name', 'text'])
    for name, words in zip (name_list, word_list):
        words = words.split('。')
        # 最後の発言は空白のなるため[-1]とスライスし空白行を削除がデータフレーム化しないようにしています
        words = words[:-1]
        word_df = pd.DataFrame({'name': name, 'text': words})
        df = df.append(word_df)
    # 重複処理
    df = df.drop_duplicates()

    # インデックスを振り直し
    df = df.reset_index(drop=True)
    # 最後の行に引数である議題を加える
    target_text = pd.Series(['target', search_words], index=['name', 'text'])
    df = df.append(target_text, ignore_index=True)
    # テスト関数用にデータフレームを少なくしています
    # df = df.iloc[:1000, :]

    # 形態素解析
    # Mecabで形態素解析
    mecab = MeCab.Tagger('-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')

    text_tokenized = []
    for text in df['text']:
        text_tokenized.append(mecab.parse(text))

    df['text_tokenized'] = text_tokenized
    # TF-IDFで特徴量化consider
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    text_transformed = vectorizer.fit_transform(df["text_tokenized"])

    # numpy.ndarrayに変換しています
    # メモリが足りないためカーネルが止まる
    text_transformed = text_transformed.toarray()

    # コサイン類似度を計算
    words_similarity = []
    target_idx = -1

    for i in range(len(text_transformed)):
        # cosine類似度　= 1 - cosine距離
        sim = _get_cosine_similarity(text_transformed[target_idx], text_transformed[i])    
        words_similarity.append(sim)
        
    words_similarity = np.array(words_similarity)
    words_similarity = pd.DataFrame(words_similarity, columns=['words_similarity'])
    df = pd.concat([df, words_similarity], axis=1)
    df['text'] = df['text'].replace('', np.nan)
    df = df.dropna(subset=['text'])
    # 比較対象発言で類似度が高い発言を抽出
    # トップ20の類似度が高い発言を抽出しています
    topN = 20
    #類似度でソート
    sorted_df = df.sort_values('words_similarity', ascending=False)
    # 必要のない列を削除
    sorted_df = sorted_df.drop('text_tokenized', axis=1)
    # トップ20を抽出
    similarited_text = sorted_df.iloc[1:topN+1, :]
    similarited_text = similarited_text.reset_index(drop=True)
    similarited_text['words_similarity'] = similarited_text['words_similarity'] * 100
    similarited_text['words_similarity'] = similarited_text['words_similarity'].round(2) 
    # 以下のコメントアウトはjsonでの処理の記述となっている
    # translated_similarited_text = similarited_text.T
    # pandas.DataFrameデータをjson化
    # similarity_scores = translated_similarited_text.to_json(force_ascii=False)
    return similarited_text

if __name__ == '__main__':
    search_words = 'デジタル庁のプロダクト内製について'
    similarity_scores = get_words_similarity(search_words)
    print(similarity_scores)