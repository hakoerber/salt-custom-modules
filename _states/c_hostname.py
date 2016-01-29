def set(name):
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': ''
    }

    current_name = __salt__['c_hostname.get_hostname']()
    if name == current_name:
        ret['result'] = True
        ret['comment'] = "Hostname \"{0}\" already set.".format(name)
        return ret

    if __opts__['test'] is True:
        ret['comment'] = "Hostname \"{0}\" will be set".format(name)
    else:
        __salt__['c_hostname.set_hostname'](name)
        ret['changes']['hostname'] = {'old': current_name, 'new': name}
        ret['comment'] = "Hostname \"{0}\" has been set".format(name)

    ret['result'] = True
    return ret

