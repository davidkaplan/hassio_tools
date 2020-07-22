#!/bin/bash
set -x
ha core stop
docker stop addon_core_zwave
docker cp addon_core_zwave:/data/ozw/config/ozwcache_0xe252b249.xml .
python3 modify_xml.py -i ozwcache_0xe252b249.xml
docker cp ozwcache_0xe252b249.xml addon_core_zwave:/data/ozw/config
docker start addon_core_zwave
ha addons start core_zwave
ha core start
