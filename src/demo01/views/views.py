import flask_login as login
from flask import url_for, redirect, request
import os.path as op
import flask_admin as admin
from flask_admin import form as form1
from flask_admin import helpers, expose
from flask_admin.contrib import sqla

file_path = op.join(op.dirname(__file__), 'files')

# Create customized index view class that handles login & registration


class AlertStrategyView(sqla.ModelView):
    # Override form field to use Flask-Admin FileUploadField
    can_view_details = True
    column_list = ['name', 'vol_name', 'light_name']
    column_labels = {
        'name': '策略名称',
        'vol_name': '关联资源1',
        'light_name': '关联资源2',
        'speed_lower': '区间下限',
        'speed_upper': '区间上限'
    }
    form_overrides = {
        'path': form1.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'AlertStrategy',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

    def is_accessible(self):
        return login.current_user.is_authenticated


class LightStrategyView(sqla.ModelView):
    # Override form field to use Flask-Admin FileUploadField
    can_view_details = True
    column_list = ['name', 'period', 'light_on']
    column_labels = {
        'name': '策略名称',
        'period': '周期',
        'light_on': '时长'
    }
    form_overrides = {
        'path': form1.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'LightStrategy',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

    def is_accessible(self):
        return login.current_user.is_authenticated


class VolFileView(sqla.ModelView):
    # Override form field to use Flask-Admin FileUploadField
    column_list = ['name', 'path']
    column_labels = {
        'name': '资源名称',
        'path': '资源路径'
    }

    form_overrides = {
        'path': form1.FileUploadField
    }

    # Pass additional parameters to 'path' to FileUploadField constructor
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

    def is_accessible(self):
        return login.current_user.is_authenticated
