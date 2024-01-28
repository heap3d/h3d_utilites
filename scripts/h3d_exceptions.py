#!/usr/bin/python
# ================================
# (C)2022-2023 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# h3d exeptions
class H3dExitException(Exception):
    """
    Raises to debug exit
    """
    def __init__(self, message='Debug exit.'):
        self.message = message
        Exception().__init__(message)
