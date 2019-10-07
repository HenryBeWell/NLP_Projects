# encoding: utf-8

"""
@author: Henry
@site: 
@software: PyCharm
@file: news_auto_extract.py
@time: 2019/10/7 19:19
"""
from flask import Flask
from flask import g
from flask import request
from flask import render_template
from flask import jsonify

from forms.news_extractor import NewsExtractorForm

from views import app
from nlp.parse_news import SpeechExtractor, LTPManager
from config import SYNONYMS_PATH, LTP_MODEL_PATH


@app.route('/')
def nlp_projects():
    return render_template('index.html')


@app.route('/extract/', endpoint='extract', methods=['GET'])
def auto_extractor():
    return render_template('news_extractor.html')


# 解析新闻
@app.route('/extract/', methods=['POST'])
def add_address():
    LTPM = LTPManager(LTP_MODEL_PATH)

    news_form = NewsExtractorForm(request.form)
    message = "添加成功"
    if news_form.validate():
        npa = SpeechExtractor(news_form, SYNONYMS_PATH, LTPM)
        result = npa()
        return render_template('extract.html', form=result)
    return jsonify({"status": "false", "message": "格式错误"})


if __name__ == '__main__':
    app.run()
