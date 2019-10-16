# encoding: utf-8

"""
@author: Henry
@site: 
@software: PyCharm
@file: news_extractor.py
@time: 2019/10/7 15:35
"""
from wtforms import Form
from wtforms import StringField
from wtforms import validators


class NewsExtractorForm(Form):
    news = StringField(validators=[validators.DataRequired(message="请输入需检测信息...",),
                                   validators.InputRequired(message="请输入需检测信息..."),
                                   validators.Length(min=3, message="检测信息不能少于3个字符"),
                                   validators.Length(max=500, message="检测信息不能超过500个字符"),
                                   ],
                       render_kw={'class': 'form-control', 'placeholder': '请输入有效信息……'}
                       )
