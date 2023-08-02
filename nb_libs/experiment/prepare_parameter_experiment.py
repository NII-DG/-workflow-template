import os
import json
import traceback

import panel as pn
from IPython.display import clear_output, display

from ..utils.ex_utils import dmp, package as ex_pkg
from ..utils.common import common
from ..utils.form import prepare as pre
from ..utils.message import message as msg_mod, display as msg_display
from ..utils.params import ex_pkg_info
from ..utils.path import path as p
from ..utils.except_class import DidNotFinishError, DGTaskError

FILE_PATH = os.path.join(p.RF_FORM_DATA_DIR, 'prepare_parameter_experiment.json')


# ----- tmp_file handling -----
def set_params(ex_pkg_name:str, param_ex_name:str):
    params_dict = {
    "ex_pkg_name" : ex_pkg_name,
    "param_ex_name" : param_ex_name,
    }
    common.create_json_file(FILE_PATH, params_dict)


def get_params()->tuple[str, str]:
    with open(FILE_PATH, mode='r') as f:
            params = json.load(f)
    try:
        experiment_title = params["ex_pkg_name"]
        param_name = params["param_ex_name"]

    except KeyError:
        msg_display.display_err(msg_mod.get('setup_sync', 'not_entered'))
        raise DidNotFinishError

    return experiment_title, param_name


def delete_tmp_file():
    """ファイルがあれば消す"""
    common.delete_file(FILE_PATH)


def preparation_completed():
    """事前準備が完了しているかどうかを確認"""
    if not (os.path.isfile(FILE_PATH)):
        msg_display.display_err(msg_mod.get('setup_sync', 'not_entered'))
        raise DidNotFinishError


# ----- for cell -----
def display_forms():
    delete_tmp_file()
    initial_experiment()


def create_param_folder():
    """パラメータ実験フォルダの作成"""
    preparation_completed()
    experiment_title, param_name = get_params()

    # validation
    try:
        # フォルダ名の空文字禁止
        for v in [experiment_title, param_name]:
            if len(v) <= 0:
                raise DGTaskError

        # 親フォルダが存在していない場合エラー
        if not os.path.isdir(p.create_experiments_with_subpath(experiment_title)):
            raise DGTaskError

        # 作成するフォルダと同名のフォルダが存在する場合エラー
        if os.path.isdir(p.create_experiments_with_subpath(experiment_title, param_name)):
            raise DGTaskError

    except DGTaskError as e:
        msg_display.display_err(msg_mod.get('setup_package', 'param_validate_error'))
        raise e

    else:
        ex_pkg.create_param_folder(p.create_experiments_with_subpath(experiment_title, param_name))


def syncs_config() -> tuple[list[str], list[str], list[str], str, list[str]]:
    """同期のためにファイルとメッセージの設定"""
    preparation_completed()
    # get parameter
    experiment_title, param_name = get_params()
    # set sync path
    git_path, gitannex_path, gitannex_files = ex_pkg.create_syncs_path(p.create_experiments_with_subpath(experiment_title))
    nb_path = os.path.join(p.EXP_DIR_PATH, 'prepare_parameter_experiment.ipynb')
    git_path.append(nb_path)
    get_paths = ['experiments/{}'.format(experiment_title)]
    # set commit message
    commit_message = msg_mod.get('commit_message', 'prepare_parameter_experiment').format(experiment_title, param_name)
    # delete temporarily file
    delete_tmp_file()
    return git_path, gitannex_path, gitannex_files, commit_message, get_paths


# ----- utils -----
def submit_init_experiment_callback(input_forms, error_message, submit_button):
    """Processing method after click on submit button"""
    def callback(event):
        delete_tmp_file()
        paramfolder_name = input_forms[0].value
        package_name = ex_pkg_info.exec_get_ex_title()
        # validate value for forms
        if not pre.validate_parameter_folder_name(paramfolder_name, package_name, submit_button):
            return

        try:
            set_params(package_name, paramfolder_name)

        except Exception as e:
            submit_button.button_type = 'danger'
            submit_button.name =  msg_mod.get('DEFAULT','unexpected')
            error_message.value = 'ERROR : {}'.format(traceback.format_exception_only(type(e), e)[0].rstrip('\\n'))
            error_message.object = pn.pane.HTML(error_message.value)
            return
        else:
            submit_button.button_type = 'success'
            submit_button.name =  msg_mod.get('setup_package','success')
            return
    return callback


def initial_experiment():
    pn.extension()

    if not dmp.is_for_parameter(dmp.get_datasetStructure()):
        msg_display.display_warm(msg_mod.get('setup_package','excluded_warm'))
        return

    # form
    param_form = pre.create_param_form()

    # Instance for exception messages
    error_message = pre.layout_error_text()

    button = pre.create_button(name=msg_mod.get('DEFAULT','end_input'))

    # Define processing after clicking the submit button
    button.on_click(submit_init_experiment_callback(param_form, error_message, button))

    clear_output()
    # Columnを利用すると値を取れない場合がある
    display(param_form)
    display(button)
    display(error_message)
