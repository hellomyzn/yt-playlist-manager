"""common.exceptions.my_exceptions"""


class MyException(Exception):
    """Base class
    """


class MyRequestsException(MyException):
    """My requests exception

    Args:
        MyException (Exception): base class
    """


class MyJsonDecodeException(MyException):
    """My json decode exception

    Args:
        MyException (Exception): base class
    """


class MyParamikoException(MyException):
    """My paramiko exception

    Args:
        MyException (Exception): base class
    """
