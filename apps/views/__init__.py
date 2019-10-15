from flask import Blueprint

# 实例化cms_bp的蓝图对象
nlp_bp = Blueprint('nlp', __name__)

# 导入蓝图管理的视图函数，目的是执行各视图函数中的route注册装饰器
from apps.views import news_auto_extract
from apps.views import sentiment_analysis

