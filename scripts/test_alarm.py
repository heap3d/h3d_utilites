#!/usr/bin/python
# ================================
# (C)2026 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# test alarm
# ================================

import webbrowser

from h3d_utilites.scripts.h3d_utils import get_user_value

from h3d_utilites.scripts.h3d_utils import USERVAL_ALARM_PATH


def main():
    filename = get_user_value(USERVAL_ALARM_PATH)

    webbrowser.open(filename)


if __name__ == "__main__":
    main()
