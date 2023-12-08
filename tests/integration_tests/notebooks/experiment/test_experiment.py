import os

from playwright.sync_api import BrowserContext

from tests.integration_tests.common import notebook
from tests.integration_tests.common.path import JUPYTER_HUB_URL
from tests.integration_tests.common.setting import read_it_setting
from tests.integration_tests.common.utils import login_gakunin_rdm

FILE_PATH = 'notebooks/experiment/experiment.ipynb'


def experiment(env_key: str, context: BrowserContext):
    it_setting = read_it_setting(env_key)
    page_url = f'{JUPYTER_HUB_URL}/user/{it_setting["user"]}/{it_setting["exp_server"]}/notebooks/WORKFLOWS/{FILE_PATH}'
    page = context.new_page()
    page.goto(page_url)

    # GakuNin RDMへのログイン
    login_gakunin_rdm(page)

    # ノートブックの初期処理
    notebook.init_notebook(page)

    # 共通メニュー
    cell_index = 0
    cell = notebook.get_code_cell(page, cell_index)
    # セルの実行
    notebook.run_code_cell(page, cell_index, None)
    # セル実行後のスクリーンショット保存
    notebook.screenshot(page, 'experiment/experiment_01.png')
    # セルの実行に成功したか確認
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)

    # 1つ目のセルの実行インデックス取得
    execute_index = notebook.get_execute_index(cell)

    # 実験フロー図を表示
    cell_index = 1
    cell = notebook.get_code_cell(page, cell_index)
    execute_index = execute_index + 1
    # セルの実行
    notebook.run_code_cell(page, cell_index, execute_index)
    # セル実行後のスクリーンショット保存
    notebook.screenshot(page, 'experiment/experiment_02.png')
    # セルの実行に成功したか確認
    notebook.check_cell(cell, notebook.CELL_CLASS_SUCCESS)
