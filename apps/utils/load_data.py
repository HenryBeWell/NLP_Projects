"""
加载数据
"""

from apps.config import DEFAULT_STOPWORDS_PATH


def load_synonyms(file_name=None) -> list:
    if file_name is None:
        file_name = DEFAULT_STOPWORDS_PATH
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            synonyms = f.readlines()
        return synonyms
    except Exception as e:
        print(e)


def load_stopwords(file_name=None) -> set:
    """

    :param file_name: stop_words path
    :return:
    """
    if file_name is None:
        file_name = DEFAULT_STOPWORDS_PATH
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            stopwords = set(line[:-1] for line in f)
        return stopwords
    except Exception as e:
        print(e)
