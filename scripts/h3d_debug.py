#!/usr/bin/python
# ================================
# (C)2022-2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d debug utilites

import datetime
import inspect
import os.path
from typing import Union, Iterable
import subprocess

import modo

from h3d_utilites.scripts.h3d_utils import replace_file_ext, safe_type


DEFAULT_FOLDER = r'~\AppData\Roaming\Luxology\Temp'


class H3dDebug:
    def __init__(self, enable=False, file='', fullpath='', indent=0, indent_str=' ' * 4):
        self.enable = enable
        self.initial_indent = int(indent)
        self.indent = self.initial_indent
        self.indent_str = indent_str
        self.log_path = ''
        self.last_emptyline = True
        self.filename_init(shortname=file, fullname=fullpath)
        if self.enable:
            self.enable_debug_output()
        else:
            print(f'log enabled: {self.enable}')
            print(f'log path: {self.log_path}')

    def enable_debug_output(self, state=True):
        self.enable = state
        self.log_reset()

    def print_debug(self, message, indent=0, forced=False):
        if not self.enable:
            return
        if message == '' and self.last_emptyline and not forced:
            return
        if message == '':
            self.last_emptyline = True
        else:
            self.last_emptyline = False
        self.indent += indent
        curtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        message_upd = '{}{} {}'.format(curtime, self.indent_str * self.indent, message)
        if self.log_path:
            self.print_to_file(message_upd)
        else:
            self.print_to_sys(message_upd)
        self.indent -= indent

    def print_to_file(self, message):
        if not self.enable:
            return
        if not self.log_path:
            self.print_to_sys(message)
            return
        with open(self.log_path, 'a') as f:
            f.write(message)
            f.write('\n')

    def print_to_sys(self, message):
        if not self.enable:
            return
        print(message)

    def exit(self, message='debug exit'):
        self.print_debug(message)
        print(message)
        raise SystemExit(message)

    def get_name(self, item):
        if not self.enable:
            return
        if not item:
            return

        try:
            name = item.name
        except AttributeError:
            name = ''

        return name

    def print_items(self, items, message=None, indent=0, emptyline=True):
        if not self.enable:
            return

        if emptyline:
            self.print_debug('')

        if message:
            self.print_debug(message + f' ({len(items)})', indent=indent)
        else:
            self.print_debug(f'{len(items)} items:', indent=indent)

        if not items:
            self.print_debug(items, indent=indent + 1)
            if emptyline:
                self.print_debug('')
            return

        if isinstance(items, dict):
            for k, v in items.items():
                if 'modo.item.' in str(type(k)):
                    dict_key = f'<{k.name}>:<{safe_type(k)}>'
                else:
                    dict_key = f'<{k}>'
                if 'modo.item.' in str(type(v)):
                    dict_val = f'<{v.name}>:<{safe_type(v)}>'
                else:
                    dict_val = f'<{v}>'
                self.print_debug(f'{dict_key} :: {dict_val}', indent=indent + 1)
        else:
            for k in items:
                if 'modo.item.' in str(type(k)):
                    self.print_debug(f'<{k.name}>:<{safe_type(k)}>', indent=indent + 1)
                else:
                    self.print_debug(f'<{k}>', indent=indent + 1)

        if emptyline:
            self.print_debug('')

    def filename_init(self, shortname='', fullname=''):
        if not shortname and not fullname:
            return

        self.log_path = fullname

        if not self.log_path:
            scene_path = modo.Scene().filename
            if not scene_path:
                scene_path = get_log_default_path()

            if os.path.isfile(scene_path):
                scene_directory = os.path.dirname(scene_path)
            else:
                scene_directory = scene_path
            self.log_path = os.path.join(scene_directory, shortname)

        if self.log_path.endswith('.lxo'):
            self.log_path = f'{self.log_path}.log'

    def print_fn_in(self, message='', emptyline=True):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        out_string = f'>>>> in: {caller}() {message}'
        if emptyline:
            self.print_debug('')
        self.print_debug(out_string)
        if emptyline:
            self.print_debug('')
        self.indent_inc()

    def print_fn_out(self, message='', emptyline=True):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        self.indent_dec()
        out_string = f'<<<< out: {caller}() {message}'
        if emptyline:
            self.print_debug('')
        self.print_debug(out_string)
        if emptyline:
            self.print_debug('')

    def indent_inc(self, inc=1):
        if not self.enable:
            return
        self.indent += inc

    def indent_dec(self, dec=1):
        if not self.enable:
            return
        self.indent -= dec

    def log_reset(self):
        if not self.enable:
            return

        self.filename_init(fullname=self.log_path)

        if not self.log_path:
            return

        try:
            with open(self.log_path, 'w'):
                # reinitialize log file
                pass
        except Exception:
            # output to event Log
            self.log_path = ''

        self.indent = self.initial_indent

        print(f'log enabled: {self.enable}')
        print(f'log path: {self.log_path}')

    def get_attributes(self, class_item):
        members = inspect.getmembers(class_item)
        public_members = []
        for member in members:
            # skip if starts with underscore
            if member[0].startswith('_'):
                continue
            # skip if member is method
            if inspect.ismethod(member[1]):
                continue
            # add to public members list
            public_members.append(member)

        return public_members

    def print_smart(
            self, variable: Union[None, int, float, Iterable, modo.Item, modo.Vector3],
            indent=0, emptyline=True, forced=False
            ):
        if not self.enable:
            return
        var_name = f'{get_variable_name_deep(variable)}'
        if var_name is None:
            var_name = f'{get_variable_name(variable)}'
        try:
            item_name = f'<{variable.name}>'  # type: ignore
        except AttributeError:
            item_name = ''

        var_string = f'{item_name}'

        try:
            variable_type = variable.type
        except AttributeError:
            variable_type = type(variable)

        try:
            _ = [i for i in variable]  # type: ignore
        except TypeError:
            self.print_debug(f'var<{var_name}>:{var_string}:<{variable}>:<{variable_type}>', indent)
        else:
            if not isinstance(variable, str):
                self.print_items(variable, f'var<{var_name}>:', indent, emptyline)
                return

            if var_name is None:
                self.print_debug(variable, indent, forced)
            elif not var_string:
                self.print_debug(f'<{variable}>', indent, forced)
            else:
                self.print_debug(f'var<{var_name}>:<{var_string}>:<{variable}>:<{variable_type}>', indent, forced)

    def show_log_in_explorer(self):
        if not self.enable:
            return

        subprocess.Popen(f'explorer /select,"{self.log_path}"')


def get_variable_name(var) -> Union[str, None]:
    current_frame = inspect.currentframe()
    try:
        frame_locals = current_frame.f_back.f_locals  # type: ignore
        var_name = [name for name, value in frame_locals.items() if value is var][0]
        return var_name

    except IndexError:
        return None

    finally:
        del current_frame


def get_variable_name_deep(var) -> Union[str, None]:
    current_frame = inspect.currentframe()
    try:
        frame_locals = current_frame.f_back.f_back.f_locals  # type: ignore
        var_name = [name for name, value in frame_locals.items() if value is var][0]
        return var_name

    except IndexError:
        return None

    finally:
        del current_frame


def get_log_default_path() -> str:
    scene_path = os.path.expanduser(DEFAULT_FOLDER)
    if not os.path.exists(scene_path):
        os.makedirs(scene_path)
    return scene_path


try:
    _ = h3dd  # type: ignore
except NameError:
    h3dd = H3dDebug(file=replace_file_ext(modo.Scene().name, ".log"))
    prints = h3dd.print_smart
    fn_in = h3dd.print_fn_in
    fn_out = h3dd.print_fn_out
