#!/usr/bin/python2


class BuildError(Exception):
    pass


class ToolchainError(Exception):
    pass


class ToolchainNotFoundError(ToolchainError):
    pass
