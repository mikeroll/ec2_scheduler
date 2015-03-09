#!/usr/bin/env python2

from __future__ import print_function

from boto import ec2,route53
from croniter import croniter
from datetime import datetime
from time import sleep

def get_wanted_state(instance):
    start = croniter(instance.tags['start_time'], datetime.utcnow())
    stop = croniter(instance.tags['stop_time'], datetime.utcnow())
    return "running" if start.get_prev() > stop.get_prev() else "stopped"

def manage_state(target):
    print("[{0}]".format(target['instance'].tags['Name']), end=' ')
    if target['wanted_state'] == 'running':
        print("starting...")
        target['instance'].start()
    if target['wanted_state'] == 'stopped':
        print("stopping")
        target['instance'].stop()

def manage_uri(target, zone):
    pub_ip = target['instance'].ip_address
    uri = target['instance'].tags['uri'].replace('_', '.')
    if t['wanted_state'] == 'running':
        print('[{0}] setting uri {1}'.format(target['instance'].tags['Name'], uri))
        if zone.get_a(uri):
            zone.update_a(uri, pub_ip, '60')
        else:
            zone.add_a(uri, pub_ip, '60')
    if t['wanted_state'] == 'stopped' and zone.get_a(uri):
        print('[{0}] deregistering uri {1}'.format(target['instance'].tags['Name'], uri))
        zone.delete_a(uri)


if __name__ == '__main__':
    ec2_conn = ec2.connect_to_region('eu-west-1')
    r53_conn = route53.connect_to_region('eu-west-1')
    instances = ec2_conn.get_only_instances(filters={ 
        "instance-state-name": ['running', 'stopped'],
        "tag:automated": ['yes', 'Yes', 'true', 'True'],
        "tag:start_time":"*", 
        "tag:stop_time":"*" 
    })
    targets = [ 
        { 
            'instance': i, 
            'wanted_state': get_wanted_state(i) 
        } 
        for i in instances if get_wanted_state(i) != i.state 
    ]
    
    if not targets:
        print('Nothing to do here.')
        exit

    for t in targets:
        manage_state(t)

    if targets: print("Waiting for state transitions to complete...")
    while any(True for t in targets if t['instance'].update() != t['wanted_state']):
        sleep(5)
    
    for t in targets:
        if t['instance'].tags.has_key('uri'):
            zone = t['instance'].tags['uri'].split('_')[1]
            z = r53_conn.get_zone(zone)
            manage_uri(t, z)
