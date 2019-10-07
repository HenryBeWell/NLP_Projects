from flask import Blueprint

# 实例化cms_bp的蓝图对象
app = Blueprint('nlp', __name__, url_prefix='/nlp')

# 导入蓝图管理的视图函数，目的是执行各视图函数中的route注册装饰器
from views import news_auto_extract
