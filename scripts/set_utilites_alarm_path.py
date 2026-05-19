#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# set alarm path
# ================================

import modo

from h3d_utilites.scripts.h3d_utils import get_user_value, set_user_value

from h3d_utilites.scripts.h3d_utils import USERVAL_ALARM_PATH


def main():
    filename = get_user_value(USERVAL_ALARM_PATH)

    dialog_result = modo.dialogs.fileOpen(ftype='', title="Specify alarm path", path=filename)
    if dialog_result:
        set_user_value(USERVAL_ALARM_PATH, dialog_result)


if __name__ == "__main__":
    main()
