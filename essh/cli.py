from __future__ import print_function

from distutils.spawn import find_executable
from os.path import isfile, getmtime
from os import execv
from six.moves import input

import pickle
import re
import sys
import time

import boto3
import click

CACHE_DIR = '/tmp/essh_cache'
CACHE_TIME_SECONDS = 300

def ssh(user, ip, cmd):
    ssh_path = find_executable("ssh")
    args = ["ssh"]
    if ssh_path is None:
        click.echo("Error: You don't seem to have ssh in your path")
        sys.exit(1)
    if user:
        args = args + ["-l", user]
    args.append(ip)
    if cmd:
        args.append(cmd)
    execv(ssh_path, args)


def get_instances():
    use_cache = True
    if not isfile(CACHE_DIR):
        use_cache = False
    else:
        if int(time.time()) - int(getmtime(CACHE_DIR)) > CACHE_TIME_SECONDS:
            use_cache = False

    if use_cache:
        with open(CACHE_DIR, 'rb') as c:
            instances = pickle.load(c)
    else:
        instances = []
        ec2 = boto3.client('ec2')
        paginator = ec2.get_paginator('describe_instances')
        response_iterator = paginator.paginate()

        for resp in response_iterator:
            for r in resp['Reservations']:
                for i in r['Instances']:
                    instances.append(i)

        with open(CACHE_DIR, 'wb') as c:
            pickle.dump(instances, c)

    return instances


def get_name(instance, pat=None):
    if 'Tags' in instance:
        for t in instance['Tags']:
            for k, _ in t.items():
                if t[k] == 'Name':
                    if pat:
                        if re.search(pat, t['Value'], flags=re.IGNORECASE):
                            return t['Value']
                        return None
                    return t['Value']
        return None

    return None


def get_primary_ip(instance):
    for n in instance['NetworkInterfaces']:
        if 'PrivateIpAddresses' in n:
            for p in n['PrivateIpAddresses']:
                if 'Primary' in p:
                    if p['Primary']:
                        return p['PrivateIpAddress']
                else:
                    return None
        else:
            return None

    return None


@click.command()
@click.option('--user', default=None)
@click.argument('host_pattern', default=None, required=False)
@click.argument('cmd', default=None, required=False)
def cli(user, host_pattern, cmd):
    '''
    ssh into ec2 instance by "Name" tag
    '''
    hosts = []
    for instance in get_instances():
        name = get_name(instance, host_pattern)
        primary_ip = get_primary_ip(instance)

        if not primary_ip or not name:
            continue

        hosts.append((name, primary_ip))

    if len(hosts) > 1:
        try:
            while True:
                click.echo('%' + '-' * 50 + '%')
                click.echo("| Pick from the following hosts (Ctrl C to escape) |")
                click.echo('%' + '-' * 50 + '%')
                sorted_hosts = [h for h in sorted(hosts, key=lambda h: h[0].lower())]
                for idx, host in enumerate(sorted_hosts):
                    click.echo("{}> {} | {}".format(idx, host[0], host[1]))
                try:
                    user_input = int(input(':'))
                    if user_input >= 0 and user_input < len(sorted_hosts):
                        ssh(user, sorted_hosts[user_input][1], cmd)
                        break
                except ValueError:
                    pass
        except (KeyboardInterrupt, EOFError):
            click.echo("\nExiting...")
            sys.exit()

    elif len(hosts) == 1:
        ssh(user, hosts[0][1], cmd)
    else:
        click.echo('No hosts matched pattern')
        sys.exit(1)
