import os
import glob
import requests
import sys
sys.path.append('..')
from utils.path import path
from utils.message import message, display
from utils.params import param_json
from utils.gin import sync


def organize_flow(workflow_identifier:str):
    """リサーチフローの最適化処理

    Args:
        workflow_identifier (str): ワークフロー識別子

    Note:
        dmp.jsonに"fields"プロパティがある想定
    """

    path_flows = os.path.join(path.RES_DIR_PATH)
    templates = glob.glob(os.path.join(path_flows, '**'), recursive=True)

    # 選択外の分野のセクション群を削除
    for tmpl in templates:
        file = os.path.basename(tmpl)
        if not os.path.isdir(tmpl) and os.path.splitext(file)[1] == '.ipynb':
            if 'base_' not in file and workflow_identifier not in file:
                os.remove(tmpl)


def update_gin_url():
    """params.json の"siblings": {"ginHttp", "ginSsh"}を更新する"""

    url = sync.get_remote_url()

    try:
        # update param json
        param_json.update_param_url(url)
    except requests.exceptions.RequestException as e:
        display.display_err(message.get('communication', 'error'))
        raise e
    except Exception as e:
        raise e