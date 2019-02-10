import functools

from store import *
from hasher import *

global_session = None

class Session:
    user = None

    def __init__(self, username, password):
        try:
            self.user = User.select().where(User.username == username).get()
            hasher.verify(self.user.password_hash, password)
        except (User.DoesNotExist, VerifyMismatchError) as e:
            self.__logged = False
        else:
            self.__logged = True

    @property
    def logged(self):
        return self.__logged

def set_session(username, password):
    global global_session 
    s = Session(username, password)
    global_session = s

def authenticated(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        if global_session and global_session.logged:
            return func(*args, **kwargs)

    return wrapped_func


def authorized(func):
    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        if len(args) and args[0] and args[0] == global_session.user.username:
            return func(*args, **kwargs)

    return wrapped_func

