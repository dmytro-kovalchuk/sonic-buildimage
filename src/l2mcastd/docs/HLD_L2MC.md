# SONiC Static L2 Multicast (L2MC) High Level Design

## 1. Feature Overview
Enables static Layer 2 Multicast forwarding for specific IPv4 multicast groups inside a VLAN boundary using `CONFIG_DB` declarations.

## 2. Database Schema

### CONFIG_DB
Table: `STATIC_L2MC`
Key: `STATIC_L2MC|VLAN_NAME|GROUP_IP`
* `members`: Comma-separated member ports (e.g. `Ethernet0,Ethernet4`)

### APPL_DB
Table: `L2MC_TABLE`
Key: `VLAN_NAME:GROUP_IP`
* `members`: List of egress ports.

## 3. Architecture & Data Flow
1. User configures group via CLI / `sonic-cfggen` / `sonic-db-cli`.
2. `l2mcastd` detects update via `swss::Select` and `SubscriberStateTable` on `CONFIG_DB`.
3. `l2mcastd` enables snooping state on VLAN and writes entry mapping to `APPL_DB` (`L2MC_TABLE`).
4. `l2mcorch` in `orchagent` receives `APPL_DB` notification.
5. `l2mcorch` maps logical ports to SAI bridge port OIDs and invokes SAI L2MC APIs to program ASIC forwarding state.

## 4. SAI API Usage
* `sai_vlan_api->set_vlan_attribute`:
  * `SAI_VLAN_ATTR_CUSTOM_IGMP_SNOOPING_ENABLE`
  * `SAI_VLAN_ATTR_IPV4_MCAST_LOOKUP_KEY_TYPE`
* `sai_l2mc_group_api`:
  * `create_l2mc_group`
  * `create_l2mc_group_member`
* `sai_l2mc_api`:
  * `create_l2mc_entry` (with mandatory `SAI_L2MC_ENTRY_ATTR_PACKET_ACTION` and `SAI_L2MC_ENTRY_ATTR_OUTPUT_GROUP_ID`)
  * `remove_l2mc_entry`