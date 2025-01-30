#!/bin/bash

set -euo pipefail

/local/repository/setup-node.sh

branch="$1"
id="$2"
advertise_ip="$3"
manager_ip="$4"

git clone --branch "${branch}" https://github.com/netiken/emu.git ~/emu
cd ~/emu || exit

# Wait for the switch to come up.
sleep 6m

nohup ~/.cargo/bin/cargo run --release worker \
    --id "$id" \
    --advertise-ip "${advertise_ip}" \
    --control-port 50000 \
    --data-port 50001 \
    --manager-addr "${manager_ip}:50000" \
    --metrics-addr 0.0.0.0:9000 \
    >emu.log 2>&1 &
