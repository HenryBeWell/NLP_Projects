# coding = utf-8
"""
文本预处理
"""
import os
import pandas as pd
import re
import jieba
from hanziconv import HanziConv
from apps.utils.load_data import load_stopwords
from apps.utils import clock
from apps.config import DEFAULT_STOPWORDS_PATH, WIKI_DATA_PATH, NEWS_DATA_PATH, PROCESSED_DATA_PATH

STOPWORDS = load_stopwords(DEFAULT_STOPWORDS_PATH)


def cut(string) -> str:
    """
    分词
    :param string:
    :return:
    """
    return ' '.join(jieba.cut(string))


def token(string) -> str:
    """
    去除句子中的标点符号
    :param string:
    :return:
    """
    return ''.join(re.findall(r'\w+', string))


def cut4wiki(string) -> list:
    line = string.strip()
    if len(line) < 1 or line.startswith('doc'):  # empty line
        pass
    else:
        return jieba.cut(line)


@clock
def train_data_from_wiki(wiki_path, out_file):
    """
    预处理wiki数据
    :param wiki_path: wiki数据路径
    :param out_file: clean_file_path
    :return:
    """
    if os.path.exists(wiki_path):
        with open(wiki_path, 'r', encoding='utf-8') as f:
            corpus = f.readlines()
            print('Now processing:' + wiki_path)
            with open(out_file, 'w', encoding='utf-8') as f:
                for sentence in corpus:
                    sentence = token(str(sentence))
                    if sentence == '': continue
                    words = cut4wiki(HanziConv.toSimplified(sentence))
                    if words:
                        sentences_by_word = ' '.join(word for word in words if word not in STOPWORDS)
                        f.write(sentences_by_word + '\n')
    else:
        print('Not Found {}'.format(wiki_path))


@clock
def train_data_from_news(data_path, out_file):
    """
    从新闻语料库下载的csv文档里拿数据
    """
    # sentences_by_word = ''
    if os.path.exists(data_path):
        print('Read data from ', data_path)
        news = pd.read_csv(data_path, error_bad_lines=False)
        news.columns = ['index', 'author', 'pulisher', 'content', 'code', 'title', 'url']
        content = news.iloc[:, 3]  # 获取content
        with open(out_file, 'w', encoding='utf-8') as f:
            for sentence in content:
                sentence = token(str(sentence))
                if sentence == '': continue
                words = jieba.cut(HanziConv.toSimplified(sentence))
                sentences_by_word = ' '.join(word for word in words if word not in STOPWORDS)

                f.write(sentences_by_word + '\n')
    else:
        print(data_path, ' does not exit')


if __name__ == '__main__':
    train_data_from_news(data_path=NEWS_DATA_PATH,
                         out_file=PROCESSED_DATA_PATH + 'processed_news.txt')
    print('finish extracting train data from news')
    train_data_from_wiki(wiki_path=WIKI_DATA_PATH,
                         out_file=PROCESSED_DATA_PATH + 'processed_wiki.txt')
    print('finish extracting train data from wiki dump')
