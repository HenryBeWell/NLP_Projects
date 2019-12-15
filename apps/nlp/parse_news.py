import os
import re

from apps.utils.load_data import load_synonyms
from apps.config import SYNONYMS_PATH, LTP_MODEL_PATH
from string import punctuation

from pyltp import SentenceSplitter, Segmentor, Postagger, NamedEntityRecognizer, Parser
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


add_punc = '·，。、【 】 “”：；（）《》‘’{}？！⑦()、%^>℃：.”“^-——=&#@￥「」′° —『』'
all_punc = punctuation + add_punc


class LTPManager(object):
    """
    LTP model
    """

    def __init__(self, data_dir):
        self.LTP_DATA_DIR = data_dir
        # 分词模型
        cws_model = os.path.join(self.LTP_DATA_DIR, 'cws.model')
        self.segmentor = Segmentor()
        self.segmentor.load(cws_model)
        # self.segmentor.load_with_lexicon(cws_model, DEFAULT_SYNONYMS_PATH)

        # 词性标注模型
        pos_model = os.path.join(self.LTP_DATA_DIR, 'pos.model')
        self.postagger = Postagger()
        self.postagger.load(pos_model)

        # 命名实体识别模型
        ner_model = os.path.join(self.LTP_DATA_DIR, 'ner.model')
        self.recongnizer = NamedEntityRecognizer()
        self.recongnizer.load(ner_model)

        # 依存句法分析模型
        parse_model = os.path.join(self.LTP_DATA_DIR, 'parser.model')
        self.parser = Parser()
        self.parser.load(parse_model)

    @staticmethod
    def split_sentence(content):
        """
        分句
        :param sentence:
        :return:
        """
        sen = SentenceSplitter.split(content)
        sentences = [s for s in sen if s]
        return sentences

    def split_words(self, sentence):
        """
        分词
        :param words:
        :return:
        """
        words = self.segmentor.segment(sentence)
        return ' '.join(words)

    def pos(self, words):
        """
        词性标注
        :param words:
        :return:
        """
        words = words.split(' ')
        postags = self.postagger.postag(words)
        return list(postags)

    def ner(self, words, postags):
        """
        命名实体识别
        :param words:
        :param postags:
        :return:
        """
        netag = self.recongnizer.recognize(words.split(' '), postags)
        return list(netag)

    def parsing(self, words, postags):
        """
        依存句法分析
        :param words:
        :param postags:
        :return:
        """
        arcs = self.parser.parse(words, postags)
        return [(arc.head, arc.relation) for arc in arcs]

    def release(self):
        """
        释放模型
        """
        self.segmentor.release()
        self.recongnizer.release()
        self.parser.release()
        self.postagger.release()


class SpeechExtractor(object):
    def __init__(self, news, synonyms_path, ltp_manager):
        self.news = news
        self.synonyms = set(load_synonyms(synonyms_path))
        self.ltp_manager = ltp_manager

    def del_punc(self, sent):
        """
        分词，去标点，分词
        :param sent:
        :return:
        """
        sent = self.ltp_manager.split_words(sent)
        item_list = [item.strip() for item in sent if item.strip() not in all_punc]
        sent_seg = self.ltp_manager.split_words(''.join(item_list))
        return sent_seg

    @classmethod
    def get_named_entity(cls, sentence_tag):
        """
        获取命名主体
        :param parse:
        :param expression_words:
        :return:
        """
        ners = defaultdict(int)
        ner_set = ['S-Ni', 'S-Ns', 'S-Nh', 'B-Ni', 'B-Ns', 'B-Nh', 'I-Ni', 'I-Ns', 'I-Nh', 'E-Ni', 'E-Ns', 'E-Nh']
        i = 0
        while i < len(sentence_tag):
            for j in range(i, len(sentence_tag)):
                if sentence_tag[j] not in ner_set: break
            if j == i:
                i += 1
            else:
                ners[i] = j
                i = j
        return ners

    @classmethod
    def calc_tf_idf(cls, text_list):
        """
        计算tf-idf
        :param text_list:
        :return:
        """
        tf_idf = TfidfVectorizer()
        return tf_idf.fit_transform(text_list)

    @classmethod
    def cosine_sim(cls, x1, x2):
        """
        获取文本相似性
        :param x1:
        :param x2:
        :return:
        """
        return cosine_similarity(x1, x2)

    def has_next_sentence(self, x1, x2, threshold):
        """
        判断是否有下一句话
        :param x1:
        :param x2:
        :param threshold: 阈值
        :return:
        """
        sim = self.cosine_sim(x1, x2)[0][0]
        if sim > threshold:
            # print(sim)
            return True
        return False

    def process(self):

        # 分句
        sents = self.ltp_manager.split_sentence(self.news)
        # 分词
        sents_ = [self.del_punc(s) for s in sents]
        # 词性标注
        postags = [self.ltp_manager.pos(s) for s in sents_]
        # 命名实体识别
        ners = [self.ltp_manager.ner(s, p) for s, p in zip(sents_, postags)]
        # 依存句法分析
        arcs = [self.ltp_manager.parsing(w.split(' '), n) for w, n in zip(sents_, postags)]
        # 计算句子间的tf-idf值
        tf_idf_vec = self.calc_tf_idf(sents_)

        result = []
        for idx, ner in enumerate(ners):
            ner_dict = self.get_named_entity(ner)
            if not ner_dict:
                continue
            words = sents_[idx].split(' ')
            # print(words)
            sub_v = defaultdict(int)
            for i, arc in enumerate(arcs[idx]):
                if arc[1] == 'SBV':
                    if (arc[0] - 1) not in sub_v.keys():
                        sub_v[arc[0] - 1] = i
                    else:
                        if i > sub_v[arc[0] - 1]:
                            sub_v[arc[0] - 1] = i

            for v, s in sub_v.items():
                if words[v] in self.synonyms:
                    if s in ner_dict.keys():
                        sub = ''.join(words[s:ner_dict[s]])
                    else:
                        l = [(n[0], n[1], s - n[0]) for n in list(ner_dict.items()) if n[0] < v and n[0] < s]
                        if l:
                            start, end, _ = min(l, key=lambda x: x[2])
                            sub = ''.join(words[start:end])
                        else:
                            sub = words[s]
                    said = words[v]
                    speech = sents[idx].split(words[v])[1]

                    # print('1: ', speech)

                    if idx < len(ners) - 1 and self.has_next_sentence(tf_idf_vec[idx], tf_idf_vec[idx + 1], 0.05):
                        speech += sents[idx + 1]
                        # print('2:', speech)
                    if speech[-1] != "。":
                        speech = re.findall("(?:[^.。]*?)" + "(?:，|:|：|,)([\s\S]*?)$", speech)
                        # print('3:', speech)

                    else:
                        speech = re.findall("(?:[^.。]*?)" + "(?:，|:|：|,)([\s\S]*?)。$", speech)

                    result.append((sub, said, speech[0])) if speech != [] else result.append((sub, said, sents[idx].split(words[v])[1]))

        return result


if __name__ == '__main__':
    test_doc = """
    新华社香港8月11日电 香港升旗队总会11日在新界元朗一家中学举行“家在中华”升旗礼，吸引多名市民参与。

    习近平先生也说这是一件重要的事情。

    正午时分，艳阳高照。由香港多家中学组成的升旗队伍，护送国旗到学校操场的旗杆下。五星红旗伴随着国歌冉冉升起，气氛庄严。
    香港升旗队总会主席周世耀在国旗下致辞时表示，最近香港发生很多不愉快的事件，包括部分人侮辱国旗国徽、挑战“一国两制”原则底线，也分化了香港和内地的同胞。希望通过当天举行升旗活动弘扬正能量，并传递一个重要讯息：香港属于中华民族大家庭。

    香港升旗队总会总监许振隆勉励年轻人说，要关心社会，关心国家，希望年轻人以国为荣，为国争光。
    活动接近尾声，参与者在中国地图上贴上中国国旗，象征大家共同努力建设国家。最后，全体人员合唱《明天会更好》，为香港送上美好祝愿。

    今年15岁的郭紫晴在香港土生土长。她表示，这次升旗礼是特别为香港加油而举行的，希望大家都懂得尊重自己的国家。“看着国旗升起，想到自己在中国这片土地上成长，感到十分自豪。”
    “升旗仪式(与以往)一样，但意义却不同。”作为当天升旗队成员之一的高中生赵颖贤说，国旗和国徽代表了一个国家的尊严，不容践踏，很期望当天的活动能向广大市民传达这一信息。

    即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。

    """
    # sentences = '习近平先生也说过这是一件重要的事情。即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。'
    sentence = '作为当天升旗队成员之一的高中生赵颖贤说，“国旗和国徽代表了一个国家的尊严，不容践踏，很期望当天的活动能向广大市民传达这一信息。”'
    sentence1 = '即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。'
    sentence2 = '习近平先生也说这是一件重要的事情。'

    manager = LTPManager(LTP_MODEL_PATH)
    # extractor = SpeechExtractor(sentence2, SYNONYMS_PATH, manager)
    extractor = SpeechExtractor(test_doc,SYNONYMS_PATH, manager)
    res = extractor.process()
    print(res)
    manager.release()
