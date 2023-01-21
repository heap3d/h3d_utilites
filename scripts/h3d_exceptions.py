class H3dExitException(Exception):
    """
    Raises to debug exit
    """
    def __init__(self, message='Debug exit.') -> None:
        self.message = message
        super().__init__(self.message)
