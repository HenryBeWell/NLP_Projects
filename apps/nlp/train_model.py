from gensim.models import Word2Vec
from gensim.models.word2vec import PathLineSentences
import os
import multiprocessing
from apps.config import PROCESSED_DATA_PATH, WORD2VEC_MODEL_PATH, DEFAULT_SYNONYMS_PATH
from apps.utils import clock


@clock
def train_word2vec_model(path):
    """
    训练词向量
    """
    if os.path.exists(path):
        print('Train Word2Vec model using all files under ', path)
        model = Word2Vec(
            PathLineSentences(path),  # 训练该文件夹下所有文件
            min_count=10,  # 忽略词频小于此值的单词
            sg=0,  # sg=0: CBOW
            size=128,  # 一个句子中当前单词和被预测单词的最大距离
            window=20,  # 一个句子中当前单词和被预测单词的最大距离
            workers=multiprocessing.cpu_count()  # 训练模型时使用的线程数
        )
        related_words = model.most_similar('说', topn=100)
        print(related_words)
        words = sorted(related_words.items(), key=lambda x: x[1], reverse=True)
        words = list(zip(*words))[0]
        with open(DEFAULT_SYNONYMS_PATH, 'w', encoding='utf-8') as f:
            for word in words:
                f.write(word + '\n')
        return model
    else:
        print(path, ' does not exit')


if __name__ == '__main__':
    word2vec_model = train_word2vec_model(PROCESSED_DATA_PATH)
    word_vector = word2vec_model.wv
    # del word2vec_model
    word_vector.save(WORD2VEC_MODEL_PATH)
