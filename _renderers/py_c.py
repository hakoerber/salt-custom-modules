# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os

from salt.exceptions import SaltRenderError
import salt.utils.templates


def render(template, saltenv='base', sls='', tmplpath=None, **kws):
    template = tmplpath
    if not os.path.isfile(template):
        raise SaltRenderError('Template {0} is not a file!'.format(template))

    tmp_data = salt.utils.templates.py(
        template,
        True,
        __salt__=__salt__,
        salt=__salt__,
        __grains__=__grains__,
        grains=__grains__,
        __opts__=__opts__,
        opts=__opts__,
        __pillar__=__pillar__,
        pillar=__pillar__,
        __env__=saltenv,
        saltenv=saltenv,
        __sls__=sls,
        sls=sls,

        get_interface=get_interface,
        get_network=get_network,
        get_domain=get_domain,
        get_interface_of_network=get_interface_of_network,
        appconf=appconf,
        appnet=appnet,
        appdom=appdom,
        appif=appif,
        appdomconf=appdomconf,
        appnetconf=appnetconf,
        get_localnets=get_localnets,
        prepare=prepare,
        include=include,
        get_network_of_interface=get_network_of_interface,
        get_domain_of_interface=get_domain_of_interface,

        **kws)
    if not tmp_data.get('result', False):
        raise SaltRenderError(tmp_data.get('data',
            'Unknown render error in py renderer'))

    return tmp_data['data']


def get_interface(name=None):
    """
    Return interface with specified name (or default interface if None)
    """
    interfaces = [i for i in __pillar__['interfaces'] if not 'vpn' in i]
    if name is None:
        if len(interfaces) == 1:
            return interfaces[0]
        for interface in interfaces:
            if interface.get('primary', False) is True:
                return interface
        raise SaltRenderError("No primary interface defined")
    for interface in interfaces:
        if inferface['name'] == name:
            return interface
    raise SaltRenderError("Interface {0} not found.".format(name))


def get_network(name=None):
    """
    Return network with the specified name (or network attached to default
    interface if None is given).
    """
    networks = [net for net in __pillar__['networks'] if not net.get('vpn')]
    if name is None:
        return get_network(get_interface(None)['network'])
    for network in networks:
        if network['name'] == name:
            return network
    raise SaltRenderError("Network {0} not found.".format(name))


def get_domain(name=None):
    """
    Returns domain with the given name (or domain that contains the default
    network if None is given).
    """
    if name is None:
        return get_domain(get_network(None)['domain'])
    for domain in __pillar__['domains']:
        if domain['name'] == name:
            return domain
    raise SaltRenderError("Domain {0} not found.".format(name))


def get_interface_of_network(name):
    """
    Return interface attached to the network with the specified name.
    """
    for interface in __pillar__['interfaces']:
        if interface['network'] == name:
            return interface
    raise SaltRenderError("No interface found for network {0}.".format(name))


def appconf(name):
    """
    Return host specific application configuration
    """
    conf = __pillar__['applications']
    for sub in name.split('.'):
        conf = conf[sub]
    return conf


def appnet(cfg):
    """
    Return network belonging to application
    """
    return get_network(cfg.get('network', None))


def appdom(cfg):
    """
    Return domain belonging to application
    """
    return get_domain(cfg.get('domain', None))


def appif(cfg):
    """
    Return interface belonging to application
    """
    return get_interface_of_network(appnet(cfg)['name'])


def appdomconf(appdom, appname):
    """
    Return domain specific application configuration
    """
    conf = appdom['applications']
    for sub in appname.split('.'):
        conf = conf[sub]
    return conf


def appnetconf(appnet, appname):
    """
    Return domain specific application configuration
    """
    conf = appnet['applications']
    for sub in appname.split('.'):
        conf = conf[sub]
    return conf


def get_network_of_interface(name):
    """
    Get network containing interface.
    """
    interface = get_interface(name)
    return get_network(interface['network'])

def get_domain_of_interface(name):
    """
    Get domain containing network that is connected to given interface
    """
    interface = get_interface(name)
    network = get_network(interface['network'])
    return get_domain(network['domain'])


#def get_interface_of_network(name):
#    """
#    Returns interface attached to the given network (or attached to default
#    network if None).
#    """
#    if name is None:
#        return get_interface_of_network(get_default_network()['name'])
#    for interface in __pillar__['interfaces']:
#        if interface['network'] == name:
#            return interface
#    raise SaltRenderError("Interface {0} not found.".format(name))
#
#
#def get_domain_of_interface(intname=None):
#    interface = get_interface(intname)
#    return get_network(get_interface(intname)['network'])
#
#
#def get_domain_of_network(netname=None):
#    """
#    Get domain containing network (or domain of default network of None is
#    specified)
#    """
#    return get_domain(get_network(netname)['domain'])
#
#
#def get_network_of_domain(domain):
#    """
#    Get network belonging to domain
#    """
#    if domain is None:
#        domain = get_default_domain()['name']
#    for network in __pillar__['networks']:
#        if get_domain_of_network(network['name'])['name'] == domain:
#            return network
#    raise SaltRenderError("No network found for domain {0}.".format(domain))
#
#
#def get_interface_of_domain(domain=None):
#    """
#    Get interface attached to network belonging to domain
#    """
#    return get_interface(get_network_of_domain(domain)['name'])


def get_localnets():
    localnets = []
    for network in __pillar__['networks']:
        if network.get('local', False) is True:
            localnets.append(network['ip'] + '/' + network['prefix'])
            for also in network.get('local_also', []):
                localnets.append(also)
    return localnets


def prepare():
    config = {}
    config['include'] = list()
    config['extend'] = dict()
    return config


def include(state, config, **params):
    if state in config['include']:
        raise SaltRenderError("State {0} already defined.".format(state))
    config['include'].append(state)
    if len(params) > 0:
        config['extend'][state+'::params'] = {}
        config['extend'][state+'::params']['stateconf.set'] = []
        for k, v in params.items():
            config['extend'][state+'::params']['stateconf.set'].append({k: v})
