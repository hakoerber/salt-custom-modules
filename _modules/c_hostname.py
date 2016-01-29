from __future__ import absolute_import

import subprocess

import salt.utils


def __virtual__():
    required_cmds = ('hostnamectl',)
    for cmd in required_cmds:
        if not salt.utils.which(cmd):
            return False
    return True

def get_hostname():
    return subprocess.check_output(['hostnamectl', 'status', '--static']).strip()


def set_hostname(name):
    return subprocess.call(['hostnamectl', 'set-hostname', name]) == 0

