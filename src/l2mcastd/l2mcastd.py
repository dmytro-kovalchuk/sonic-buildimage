#!/usr/bin/env python3
import sys
import signal
import swsscommon.swsscommon as swss

def sig_handler(signum, frame):
    sys.exit(0)

def handle_entry(key, op, fv_dict, appl_table, vlan_appl_table):
    # Key format in CONFIG_DB: "Vlan100|239.1.1.1"
    if '|' not in key:
        return
    vlan, group_ip = key.split('|', 1)
    appl_key = f"{vlan}:{group_ip}"

    if op == "SET":
        members = fv_dict.get('members', '')
        
        # 1. Enable snooping on VLAN in APPL_DB
        fvs_vlan = swss.FieldValuePairs([('custom_igmp_snooping', 'enabled')])
        vlan_appl_table.set(vlan, fvs_vlan)

        # 2. Push to L2MC_TABLE in APPL_DB
        fvs_l2mc = swss.FieldValuePairs([('members', members)])
        appl_table.set(appl_key, fvs_l2mc)
    elif op == "DEL":
        appl_table._del(appl_key)

def run():
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)

    # Database connections
    config_db = swss.DBConnector("CONFIG_DB", 0, False)
    appl_db = swss.DBConnector("APPL_DB", 0, False)

    # APPL_DB producers (matches "L2MC_TABLE" registered in orchdaemon.cpp)
    appl_table = swss.ProducerStateTable(appl_db, "L2MC_TABLE")
    vlan_appl_table = swss.ProducerStateTable(appl_db, "VLAN_TABLE")

    # CONFIG_DB subscriber for live updates
    sub_table = swss.SubscriberStateTable(config_db, "STATIC_L2MC")
    sel = swss.Select()
    sel.addSelectable(sub_table)

    # Initial dump from CONFIG_DB
    cfg_connector = swss.ConfigDBConnector()
    cfg_connector.connect()
    cur_entries = cfg_connector.get_table('STATIC_L2MC')
    for key, data in cur_entries.items():
        handle_entry(key, "SET", data, appl_table, vlan_appl_table)

    # Event loop to keep container running and process new events
    while True:
        state, _ = sel.select(1000)
        if state == swss.Select.OBJECT:
            key, op, fvs = sub_table.pop()
            if not key:
                continue
            fv_dict = dict(fvs)
            handle_entry(key, op, fv_dict, appl_table, vlan_appl_table)

if __name__ == '__main__':
    run()