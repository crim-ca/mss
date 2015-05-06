"""
Collection of exceptions which can be raised by the MSS.
"""


class MSSException(Exception):
    """
    Base class for MSS exceptions.
    """
    pass


class InvalidConfiguration(MSSException):
    """
    Indicates that the given configuration for the MSS is invalid.
    """
    pass


class SwiftException(MSSException):
    """
    Indicate that Swift has produced an error.
    """
    pass
