from __future__ import absolute_import

import logging
import os
import subprocess
import tempfile

import salt.utils


log = logging.getLogger(__name__)


def __virtual__():
    required_cmds = ('checkmodule', 'semodule_package', 'semodule')
    for cmd in required_cmds:
        if not salt.utils.which(cmd):
            return False
    if not salt.utils.is_linux():
        return False
    return True

def list_modules():
    output = subprocess.check_output(['semodule', '--list'])
    modules = output.split('\n')
    modules = [module and module.split()[0] for module in modules]
    return modules

def install_module(name, source):
    tempdir = tempfile.mkdtemp()
    log.info("Building in \"{}\".".format(tempdir))
    try:
        ret = __salt__['cp.get_url'](
            path=source,
            dest=salt.utils.path_join(tempdir, name + '.te'))
        if not ret:
            raise salt.exceptions.CommandExecutionError(
                'File \"{}\" could not be transferred.'.format(source))


        for cmd in (
            ('checkmodule', '-M', '-m', '-o', name + '.mod', name + '.te'),
            ('semodule_package', '-o', name + '.pp', '-m', name + '.mod'),
            ('semodule', '-i', name + '.pp'),
        ):
            log.info("Running \"{}\".".format(" ".join(cmd)))
            process = subprocess.Popen(
                args=cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=tempdir)
            (stdout, stderr) = process.communicate()
            process.wait()
            if process.returncode != 0:
                raise salt.exceptions.CommandExecutionError(
                    'Process \"{args}\" returned {ret}.\nStdout: {stdout}\n'
                    'Stderr: {stderr}'.format(
                        args=" ".join(cmd),
                        ret=process.returncode,
                        stdout=stdout, stderr=stderr))
    finally:
        pass
        #salt.utils.rm_rf(tempdir)
    return True

