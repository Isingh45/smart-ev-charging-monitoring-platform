#!/usr/bin/env python3
"""
smart_ev_sim.py
================
Smart EV Charging — SDN simulation with hybrid-cloud telemetry.

This script builds a small Containernet topology that models two EV charging
stations attached to a single OpenFlow-managed Open vSwitch. Each "station"
is a Docker container, allowing real Linux processes (e.g. an MQTT
publisher or a boto3 client) to run inside the simulated network host.

SDN logic in this demo:
  - A single reference Controller (c0) manages s1 via OpenFlow.
  - s1 is a programmable Open vSwitch whose forwarding table is populated
    by the controller (default reference-controller learning-switch logic).
  - The Docker hosts act as real EV charging stations: they generate
    telemetry and the simulation forwards a copy of that telemetry to the
    cloud via boto3 -> DynamoDB.

Run with:
    sudo python3 smart_ev_sim.py
"""
from decimal import Decimal
import json
import random
import time
from datetime import datetime, timezone

# Containernet is a fork of Mininet, so its classes live under the
# standard `mininet.*` namespace once the package is installed.
from mininet.net import Containernet
from mininet.node import Controller, Docker, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import info, setLogLevel

# boto3 is optional at runtime — the simulation degrades gracefully if
# it isn't installed or AWS credentials aren't configured. This keeps
# the script demoable offline.
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DOCKER_IMAGE = "ubuntu:trusty"
DYNAMO_TABLE = "EVChargingLogs"
AWS_REGION = "us-east-1"


# ---------------------------------------------------------------------------
# Cloud integration
# ---------------------------------------------------------------------------
def send_telemetry_to_dynamodb(telemetry: dict, table_name: str = DYNAMO_TABLE):
    """
    Push one telemetry record into DynamoDB.

    Wrapped in a try/except so a missing boto3 install, missing AWS
    credentials, or a network outage will NOT crash the simulation.
    The simulation should always be able to run end-to-end locally.
    """
    if not BOTO3_AVAILABLE:
        info(f'*** boto3 not installed — skipping cloud upload '
             f'for {telemetry["station_id"]}\n')
        return

    try:
        dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
        table = dynamodb.Table(table_name)
        # DynamoDB requires non-numeric "Decimal" types in some cases; for
        # this demo we round floats to 2dp and let boto3's serializer
        # auto-convert. In production prefer decimal.Decimal explicitly.
        table.put_item(Item=telemetry)
        info(f'*** Telemetry uploaded -> {table_name} '
             f'({telemetry["station_id"]})\n')
    except (BotoCoreError, ClientError) as e:
        info(f'*** AWS upload failed (simulation continues): {e}\n')
    except Exception as e:  # noqa: BLE001 — final safety net
        info(f'*** Unexpected upload error: {e}\n')


def generate_telemetry(station_id: str) -> dict:
    """Synthesize one realistic-looking telemetry record for an EV station."""
    return {
        "station_id":   station_id,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
        # We wrap the rounded floats in Decimal(str()) for DynamoDB compatibility
        "battery_pct":  Decimal(str(round(random.uniform(20, 100), 2))),
        "voltage_v":    Decimal(str(round(random.uniform(220, 240), 2))),
        "current_a":    Decimal(str(round(random.uniform(10, 32), 2))),
        "status":       random.choice(["Charging", "Idle", "Available"]),
    }

# ---------------------------------------------------------------------------
# Topology
# ---------------------------------------------------------------------------
def build_topology():
    """
    Build the SDN topology.

        c0 (default Controller)
              |
              | OpenFlow
              v
            +----+
            | s1 |  (Open vSwitch, kernel datapath)
            +----+
            /    \\
       station1   station2
       10.0.0.1   10.0.0.2
       (Docker)   (Docker)

    Notes
    -----
    * `controller=Controller` tells Containernet to spin up Mininet's
      reference OpenFlow controller. s1 dials c0 on tcp/6653 and learns
      MAC->port mappings on its own.
    * `cls=OVSSwitch` (with no `datapath='user'`) uses the in-kernel OVS
      datapath, which is what we want on a real Ubuntu host.
    """
    net = Containernet(controller=Controller, link=TCLink)

    info('*** Adding default OpenFlow controller (c0)\n')
    net.addController('c0')

    info('*** Adding Docker hosts (EV charging stations)\n')
    station1 = net.addDocker('station1', ip='10.0.0.1', dimage=DOCKER_IMAGE)
    station2 = net.addDocker('station2', ip='10.0.0.2', dimage=DOCKER_IMAGE)

    info('*** Adding Open vSwitch s1 (kernel datapath)\n')
    s1 = net.addSwitch('s1', cls=OVSSwitch)

    info('*** Creating links\n')
    net.addLink(station1, s1)
    net.addLink(station2, s1)

    return net


# ---------------------------------------------------------------------------
# Simulation driver
# ---------------------------------------------------------------------------
def run_telemetry_burst(station_ids, count: int = 3):
    """Generate `count` telemetry samples per station, send each to AWS."""
    info(f'*** Generating {count} telemetry sample(s) per station\n')
    for i in range(count):
        for sid in station_ids:
            sample = generate_telemetry(sid)
            
            # --- MOVE THE FIX INSIDE THIS LOOP ---
            # Convert Decimals to floats just for the terminal printout
            printable_sample = {k: (float(v) if isinstance(v, Decimal) else v) for k, v in sample.items()}
            
            # Use printable_sample for the info() log
            info(f'    [{i+1}] {json.dumps(printable_sample)}\n')
            
            # Use the original sample (with Decimals) for the actual AWS upload
            send_telemetry_to_dynamodb(sample)
        time.sleep(1)

def start_simulation():
    net = build_topology()

    info('*** Starting network\n')
    net.start()

    # Trigger one round of pings so the controller's learning-switch
    # logic populates s1's flow table BEFORE the user starts poking
    # around in the CLI.
    info('*** Warming up forwarding tables (pingAll)\n')
    net.pingAll()

    # Hybrid-cloud step: push a few telemetry rows to DynamoDB.
    run_telemetry_burst(['STN-001', 'STN-002'], count=3)

    info('*** Mininet CLI ready — try: nodes, pingall, '
         'station1 ifconfig, dpctl dump-flows\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    start_simulation()
