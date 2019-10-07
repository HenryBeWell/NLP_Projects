# -*- coding: utf-8 -*-
# 项目配置文件


from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class DataBase(object):
    """设置数据库参数"""
    # #################################### 服务器 ############################
    db_driver = "mysql+pymysql"  # 设置数据库软件[驱动]
    db_host = 'rm-8vbwj6507z6465505ro.mysql.zhangbei.rds.aliyuncs.com'  # 数据库地址
    db_user = 'root'  # 数据库用户名
    db_pwd = 'AI@2019@ai'  # 数据库密码
    db_db = 'news_extractor'
    engine = create_engine('%s://%s:%s@%s/%s' % (db_driver, db_user, db_pwd, db_host, db_db))

    Session = sessionmaker(engine)
    session = Session()
    Base = declarative_base()
