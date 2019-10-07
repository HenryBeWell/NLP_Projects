import threading
import datetime
import time

thread_local = threading.local()
thread_local.need = True


def creat_log():
    if not False:
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    name = 'static/log/{}'.format(now)
    thread_local.logger = open(name, 'a')
    return thread_local


def create_a_log():
    if not False:
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    name = 'static/log/{}.log'.format(now)
    thread_local.logger = open(name, 'a')
    return thread_local


def write_a_log(stage, sub_title, value):
    if not False:
        return
    if not hasattr(thread_local, 'logger'):
        create_a_log()
    content = '---{}:::{}    {}\n'.format(stage, sub_title, str(value))
    thread_local.logger.write(content)


def close_a_log():
    if not False:
        return
    thread_local.logger.close()


def clock(func):
    """
    装饰器用于计时
    :param func:
    :return:
    """

    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        arg_str = ', '.join(repr(arg) for arg in args)
        print(name, ' :', elapsed, 's')
        return result

    return clocked
