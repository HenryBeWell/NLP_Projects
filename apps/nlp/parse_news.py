import os

from pyltp import SentenceSplitter, Segmentor, Postagger
from pyltp import NamedEntityRecognizer, Parser
from collections import defaultdict

from apps.utils.load_data import load_synonyms


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

    def __call__(self, sentence, *args, **kwargs):
        words = self.split_words(sentence)
        postags = self.pos(words)
        ner = self.ner(words, postags)
        arcs = self.parsing(words, postags)
        parse_result = {
            "sentence": sentence,
            "words": words,
            "postags": postags,
            "ner": ner,
            "arcs": [(arc.head, arc.relation) for arc in arcs],
        }
        return parse_result

    @staticmethod
    def split_sentence(sentence):
        """
        分句
        :param sentence:
        :return:
        """
        sen = SentenceSplitter.split(sentence)
        sentences = [s for s in sen if s]
        return sentences

    def split_words(self, words):
        """
        分词
        :param words:
        :return:
        """
        words = self.segmentor.segment(words)
        return [w for w in words]

    def pos(self, words):
        """
        词性标注
        :param words:
        :return:
        """
        postags = self.postagger.postag(words)
        return postags

    def ner(self, words, postags):
        """
        命名实体识别
        :param words:
        :param postags:
        :return:
        """
        netags = self.recongnizer.recognize(words, postags)
        return netags

    def parsing(self, words, postags):
        """
        依存句法分析
        :param words:
        :param postags:
        :return:
        """
        arcs = self.parser.parse(words, postags)
        return arcs

    def release(self):
        """
        释放模型
        """
        self.segmentor.release()
        self.recongnizer.release()
        self.parser.release()
        self.postagger.release()


class SpeechExtractor(object):
    # ltp_manager = LTPManager()

    def __init__(self, news, synonyms_path, ltp_manager):
        self.news = news
        self.synonyms = set(load_synonyms(synonyms_path))
        self.ltp_manager = ltp_manager

    def __call__(self):
        self.sentences = self.handle(self.news)
        self.sentences_goal, self.parse, self.expression_words = self.get_expression_sentences(self.sentences)
        self.ners = self.get_named_entity(self.parse, self.expression_words)
        # print(self.ners)
        self.contents = self.get_content(self.ners, self.parse, self.sentences)
        infos = [
            [
                self.ners[i]['sbv'][1],
                self.ners[i]['hed'][1],
                self.contents[i],
            ] for i in self.contents.keys()
        ]
        if infos:
            return infos
        else:
            return self.news

    @staticmethod
    def handle(news):
        """
        将新闻分句
        :param news:
        :return:
        """
        sentences = []
        for line in news.strip().split('\n'):
            sentences.extend(list(SentenceSplitter.split(line.strip())))
        return sentences

    def get_expression_sentences(self, sentences):
        """
        检测句子中是否含有与说相关的词
        :param sentences:
        :return:需要分析的句子，解析成分，说的词汇
        """
        parse = {}
        expression_words = defaultdict(list)
        sentences_goal = {}
        for i, sen in enumerate(sentences):
            for word in self.synonyms:
                word = word.strip()
                if word in sen:
                    sentences_goal[i] = sen
                    parse[i] = self.ltp_manager(sen)
                    expression_words[i].append(word)
                    # break
        return sentences_goal, parse, expression_words

    @staticmethod
    def get_named_entity(parse, expression_words):
        """
        获取命名主体
        :param parse:
        :param expression_words:
        :return:
        """
        ners = defaultdict(dict)
        for i in parse.keys():
            postags = parse[i]['postags']
            ner = parse[i]['ner']
            words = parse[i]['words']
            arcs = parse[i]['arcs']
            expression_words_list = expression_words[i]
            for expression_word in expression_words_list:
                if expression_word not in words: continue
                expression_word_idx = words.index(expression_word)

                if 0 not in arcs[expression_word_idx]: continue

                if 'v' not in list(postags[expression_word_idx]): continue

                for j, (k, v) in enumerate(arcs):
                    # 缩写，普通名词，人名，代词，机构名，地名，其它名词
                    postags_list = ['j', 'n', 'nh', 'r', 'ni', 'ns', 'nz']
                    if (v == 'SBV' and k == expression_word_idx + 1) \
                            and (set(list(ner[j])) & {"S", "B", "I", "E"}
                                 or postags[j] in postags_list):
                        sbv_start = j
                        for m in range(5):
                            if j - 1 - m >= 0:
                                if arcs[j - 1 - m][1] == 'ATT':
                                    sbv_start = j - 1 - m
                        if 'u' in postags[expression_word_idx + 1]:
                            expression_word_new_idx = expression_word_idx + 1
                            expression_word = expression_word + words[expression_word_new_idx]
                            ners[i] = {
                                'hed': (expression_word_new_idx, expression_word),
                                'sbv': ((sbv_start, j), ''.join(words[sbv_start:j + 1])),
                            }
                        else:
                            ners[i] = {
                                'hed': (expression_word_idx, expression_word),
                                'sbv': ((sbv_start, j), ''.join(words[sbv_start:j + 1])),
                            }
        return ners

    @staticmethod
    def get_content(ners, parse, sentence):
        """
        获取言论
        :param ners:
        :param parse:
        :param sentence:
        :return:
        """
        contents = defaultdict(str)
        for i in ners.keys():
            words = parse[i]['words']
            hed_idx = ners[i]['hed'][0]
            sbv_idx = ners[i]['sbv'][0]
            content_front_str = ''
            content_back_str = ''
            try:
                hed_idx_next = hed_idx + 1
                if set(words) & {'"', "'", "“", "‘"} and \
                        abs(words.index((set(words) & {'"', "'", "“", "‘"}).pop()) - hed_idx) <= 3:
                    contents[i] = words[words.index((set(words) & {'"', "'", "“", "‘"}).pop()):]
                    if not set(words) & {'"', "'", "’", "”"}:
                        for j in range(5):
                            content_back_str += sentence[i + 1 + j]
                            if set(sentence[i + 1 + j]) & {'"', "'", "’", "”"}: break

                elif words[hed_idx_next] in ['。', "！", "？", "!", "?", "…", ".", "……"]:
                    if set(sentence[i - 1]) & {'"', "'", "’", "”"}:
                        for j in range(5):
                            content_front_str = sentence[i - 1 - j] + content_front_str
                            if set(sentence[i - 1 - j]) & {'"', "'", "“", "‘"}:
                                break
                        # content_front_str += sentence[i - 1]
                    contents[i] = words[:sbv_idx[0]]

                    # 没有引号的，获取表示说的词后面的内容。
                elif words[hed_idx_next] in [":", "：", ',', '，']:
                    contents[i] = words[hed_idx_next + 1:]
                else:
                    contents[i] = words[hed_idx_next:]
            except IndexError:
                content_front_str += sentence[i - 1]
                contents[i] = words[:sbv_idx]
            contents[i] = content_front_str + "".join(contents[i]) + content_back_str
        return contents


if __name__ == '__main__':
    test_doc = """
    新华社香港8月11日电 香港升旗队总会11日在新界元朗一家中学举行“家在中华”升旗礼，吸引多名市民参与。

    习近平先生也说过这是一件重要的事情。

    正午时分，艳阳高照。由香港多家中学组成的升旗队伍，护送国旗到学校操场的旗杆下。五星红旗伴随着国歌冉冉升起，气氛庄严。
    香港升旗队总会主席周世耀在国旗下致辞时表示，最近香港发生很多不愉快的事件，包括部分人侮辱国旗国徽、挑战“一国两制”原则底线，也分化了香港和内地的同胞。希望通过当天举行升旗活动弘扬正能量，并传递一个重要讯息：香港属于中华民族大家庭。

    香港升旗队总会总监许振隆勉励年轻人说，要关心社会，关心国家，希望年轻人以国为荣，为国争光。
    活动接近尾声，参与者在中国地图上贴上中国国旗，象征大家共同努力建设国家。最后，全体人员合唱《明天会更好》，为香港送上美好祝愿。

    今年15岁的郭紫晴在香港土生土长。她表示，这次升旗礼是特别为香港加油而举行的，希望大家都懂得尊重自己的国家。“看着国旗升起，想到自己在中国这片土地上成长，感到十分自豪。”
    “升旗仪式(与以往)一样，但意义却不同。”作为当天升旗队成员之一的高中生赵颖贤说，国旗和国徽代表了一个国家的尊严，不容践踏，很期望当天的活动能向广大市民传达这一信息。

    即将升读初三的蒋靖轩认为，近日香港发生连串暴力事件，当天的升旗仪式更显意义，希望香港快快恢复平静，港人都团结起来。

    """
    from apps.config import SYNONYMS_PATH, LTP_MODEL_PATH

    LTPM = LTPManager(LTP_MODEL_PATH)
    npa = SpeechExtractor('习近平先生也说过这是一件重要的事情。', SYNONYMS_PATH, LTPM)
    # npa = SpeechExtractor(test_doc, SYNONYMS_PATH, LTPM)

    print(npa())
