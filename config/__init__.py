import os


base_path = os.path.abspath(os.path.join(os.getcwd(), "../"))
LTP_MODEL_PATH = os.path.join(base_path, 'ltp/')
SYNONYMS_PATH = os.path.join(base_path, 'dataset/synonyms/synonyms.txt')
DEFAULT_STOPWORDS_PATH = os.path.join(base_path, 'dataset/stop_words/stopwords.txt')
DEFAULT_SYNONYMS_PATH = os.path.join(base_path, 'dataset/synonyms/synonyms.txt')
WORD2VEC_MODEL_PATH = os.path.join(base_path, 'dataset/word2vec.wv')
WIKI_DATA_PATH = os.path.join(base_path, 'dataset/wiki_data/wiki_00')
NEWS_DATA_PATH = os.path.join(base_path, 'dataset/news_data/news_chinese.csv')
PROCESSED_DATA_PATH = os.path.join(base_path, 'dataset/processed/')
