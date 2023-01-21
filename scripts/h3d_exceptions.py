class H3dExitException(Exception):
    """
    Raises to debug exit
    """
    def __init__(self, message='Debug exit.'):
        self.message = message
        Exception().__init__(message)
