# encoding: utf-8

"""
@author: Henry
@site: 
@software: PyCharm
@file: __init__.py
@time: 2019/10/11 21:26
"""
from flask import Flask
from flask_bootstrap import Bootstrap


# 注册各个蓝图对象
def register_bp(app):
    from apps.views import nlp_bp
    app.register_blueprint(nlp_bp)  # 商家后台的蓝图注册

    return None


# 数据库db对象初始化
def register_db(app):
    pass


# 产生主app对象
def create_app():
    app = Flask(__name__)

    # 数据库对象注册
    register_db(app)

    # Bootstrap对象的注册
    Bootstrap(app)

    # 注册各个蓝图
    register_bp(app)

    return app
