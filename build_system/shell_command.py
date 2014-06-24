#!/usr/bin/python2

from subprocess import Popen, PIPE


class ShellCommand(object):
    def __init__(self, cmd, flags):
        if isinstance(flags, str):
            self.flags = [flags]
        self.output = ''
        self.cmd = [cmd]
        self.cmd += flags
        self.process = Popen(self.cmd,
                             stdin=PIPE,
                             stdout=PIPE,
                             stderr=PIPE)

    def run(self, stdin=''):
        """

        :rtype : str
        """
        if self.output:
            return self.output

        stdout, stderr = self.process.communicate(stdin)
        if 0 != self.process.returncode:
            self.output = stderr
            raise ValueError(stderr)
        else:
            self.output = stdout
        return self.output

    @property
    def command(self):
        return ' '.join(self.cmd)

    def __str__(self):
        return self.command
