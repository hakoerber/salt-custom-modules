def module(name, source):
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': ''
    }

    hasmodule = name in __salt__['c_selinux.list_modules']()

    if hasmodule:
        ret['result'] = True
        ret['comment'] = "Module {} already installed.".format(name)
        return ret

    if __opts__['test'] is True:
        ret['comment'] = "Module {} will be installed".format(name)
    else:
        __salt__['c_selinux.install_module'](name, source)
        ret['comment'] = "Module {} has been installed".format(name)

    ret['result'] = True
    return ret

