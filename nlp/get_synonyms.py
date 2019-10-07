from gensim.models import KeyedVectors
from collections import defaultdict
from config import WORD2VEC_MODEL_PATH

word_vec = KeyedVectors.load(WORD2VEC_MODEL_PATH)


def get_related_word(initial_words, model, size=500, topn=10):
    """
    获取 相近词
    :param initial_words list
    :param model is the word2vec model.
    :return
    """
    unseen = initial_words
    seen = defaultdict(int)
    while unseen and len(seen) < size:
        if len(seen) % 50 == 0:
            print('seen length : {}'.format(len(seen)))
        node = unseen.pop(0)
        new_expanding = [w for w, s in model.most_similar(node, topn=topn)]
        unseen += new_expanding
        seen[node] += 1
    return seen


if __name__ == '__main__':
    seed = ['说', '否认', '坚称', '回应', '告诉', '反驳', '承认', '时说', '批评', '驳斥', '质疑', '议论', '宣称', '诋毁', '答道', '回答', '嘲讽',
            '写道', '争辩', '指出', '指证', '承认']

    level_seen = get_related_word(seed, word_vec)

    sort_v = sorted([(k, v) for k, v in level_seen.items()], reverse=True, key=lambda x: x[1])

    print([k for k, v in sort_v[:200]])
