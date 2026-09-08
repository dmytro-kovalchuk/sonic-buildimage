#!/usr/bin/env python3
import time
import redis
from swsscommon import swsscommon

def main():
    print("Starting L2MC Manager Daemon with State Cache...", flush=True)
    r_config = redis.Redis(unix_socket_path='/var/run/redis/redis.sock', db=4, decode_responses=True)
    appl_db = swsscommon.DBConnector("APPL_DB", 0, True)
    producer = swsscommon.ProducerStateTable(appl_db, "L2MC_TABLE")
    
    current_state = {}

    while True:
        try:
            new_state = {}
            keys = r_config.keys("STATIC_L2MC|*")
            for k in keys:
                parts = k.split("|")
                if len(parts) == 3:
                    entry_key = f"{parts[1]}:{parts[2]}"
                    new_state[entry_key] = r_config.hgetall(k)
            
            # Обробка нових та змінених записів (SET)
            for key, data in new_state.items():
                if key not in current_state or current_state[key] != data:
                    fvs = swsscommon.FieldValuePairs(list(data.items()))
                    producer.set(key, fvs)
            
            # Обробка видалених записів (DEL)
            for key in current_state:
                if key not in new_state:
                    # У SWIG-обгортці SONiC видалення викликається через _del
                    producer._del(key)
                    
            current_state = new_state
        except Exception as e:
            print(f"Sync error: {e}", flush=True)
        time.sleep(2)

if __name__ == '__main__':
    main()