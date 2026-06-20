#!/bin/bash

while true
do
    sudo docker cp mn.station1:/ev_sim_cloud_log.json ~/smart_ev_lab/stn1.json 2>/dev/null
    sudo docker cp mn.station2:/ev_sim_cloud_log.json ~/smart_ev_lab/stn2.json 2>/dev/null

    echo '{"telemetry": [' > ~/smart_ev_lab/temp_log.json

    { tail -n 15 ~/smart_ev_lab/stn1.json 2>/dev/null; \
      tail -n 15 ~/smart_ev_lab/stn2.json 2>/dev/null; } \
      | grep "{" | paste -sd, - >> ~/smart_ev_lab/temp_log.json

    echo ']}' >> ~/smart_ev_lab/temp_log.json

    mv ~/smart_ev_lab/temp_log.json ~/smart_ev_lab/ev_sim_cloud_log.json

    sleep 2
done
