"""common.retry.retry"""
##################################################
# Python提供パッケージ
##################################################
from typing import Callable

##################################################
# 外部ライブラリ提供パッケージ
##################################################
from tenacity import retry, stop_after_attempt, wait_fixed

##################################################
# 開発パッケージ
##################################################
# None


def create_retry_decorator(attempts: int, wait_sec: int, is_reraise: bool = False) -> Callable:
    """ リトライデコレーターの作成
        メソッドのリトライ処理をするためのもの

    Args:
        attempts (int): リトライ回数
        wait_sec (int): リトライ間隔(秒)
        is_reraise (bool): True: 発生した例外でraise / False: Retry Exceptionでraise

    Ex:
        from common.retry import create_retry_decorator
        retry_decorator = create_retry_decorator(attempts=attempts, wait_sec=wait_sec, is_reraise=is_reraise)

        @retry_decorator
        def do_something():

    Returns:
        tenacity: リトライデコレーター
    """
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_fixed(wait_sec),
        reraise=is_reraise
    )
