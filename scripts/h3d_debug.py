#!/usr/bin/python
# ================================
# (C)2022-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d debug utilites

import datetime
import inspect
import os.path
import modo

from h3d_utilites.scripts.h3d_exceptions import H3dExitException
import h3d_utilites.scripts.h3d_utils as h3du


class H3dDebug:
    def __init__(self, enable=False, file=None, indent=0, indent_str=" " * 4):
        self.enable = enable
        self.initial_indent = int(indent)
        self.indent = self.initial_indent
        self.indent_str = indent_str
        self.log_path = ""
        self.file_init(file)

    def print_debug(self, message, indent=0):
        if not self.enable:
            return
        self.indent += indent
        curtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        message_upd = "{}{} {}".format(curtime, self.indent_str * self.indent, message)
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
        with open(self.log_path, "a") as f:
            f.write(message)
            f.write("\n")

    def print_to_sys(self, message):
        if not self.enable:
            return
        print(message)

    def exit(self, message="debug exit"):
        self.print_debug(message)
        raise H3dExitException(message)

    def get_name(self, item):
        if not self.enable:
            return
        if not item:
            return

        try:
            name = item.name
        except AttributeError:
            name = ""

        return name

    def print_items(self, items, message=None, indent=0):
        if not self.enable:
            return
        if message:
            self.print_debug(message, indent=indent)
        if not items:
            self.print_debug(items, indent=indent + 1)
            return

        for i in items:
            if "modo.item." in str(type(i)):
                self.print_debug(
                    "<{}> : <{}>".format(i.name, h3du.safe_type(i)), indent=indent + 1
                )
            else:
                self.print_debug("<{}>".format(i), indent=indent + 1)

    def file_init(self, file):
        if not file:
            return

        scene_path = modo.Scene().filename
        if not scene_path:
            self.log_path = None
            return

        scene_dir = os.path.dirname(scene_path)
        log_path = os.path.join(scene_dir, file)
        self.log_path = log_path
        if not self.enable:
            return

        self.log_reset()

    def print_fn_in(self):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        message = "{}(): in >>>>".format(caller)
        self.print_debug(message)
        self.indent_inc()

    def print_fn_out(self):
        if not self.enable:
            return
        caller = inspect.stack()[1][3]
        self.indent_dec()
        message = "<<<< out: {}()".format(caller)
        self.print_debug(message)

    def indent_inc(self, inc=1):
        if not self.enable:
            return
        self.indent += inc

    def indent_dec(self, dec=1):
        if not self.enable:
            return
        self.indent -= dec

    def log_reset(self):
        if not self.log_path:
            return
        with open(self.log_path, "w"):
            # reinitialize log file
            pass
        self.indent = self.initial_indent

    def get_attributes(self, class_item):
        members = inspect.getmembers(class_item)
        public_members = []
        for member in members:
            # skip if starts with underscore
            if member[0].startswith("_"):
                continue
            # skip if member is method
            if inspect.ismethod(member[1]):
                continue
            # add to public members list
            public_members.append(member)

        return public_members
