'''prepare_multi_from_s3.ipynbから呼び出されるモジュール'''
import os, json, urllib, traceback
from ipywidgets import Text, Button, Layout
from IPython.display import display, clear_output, Javascript
from datalad import api
from ..utils.git import annex_util, git_module
from ..utils.path import path
from ..utils.message import message, display as display_util
from ..utils.gin import sync
from ..utils.common import common
from ..utils.aws import s3
from ..utils.except_class import DidNotFinishError, UnexpectedError

def add_url():
    """リポジトリに取得データのS3オブジェクトURLと格納先パスを登録する

    Exception:
        DidNotFinishError: .tmp内のファイルが存在しない場合

        AddurlsError: addurlsに失敗した場合
    """
    annex_util.addurl()
    display_util.display_info(message.get('from_repo_s3', 'create_link_success'))
