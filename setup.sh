#!/bin/bash

function setup() {
    PI=$1
    ssh pi@"$PI" "cd BLE-based-IPS/; source .venv/bin/activate; python3 ~/BLE-based-IPS/client/BLE-based-IPS/threadtests.py --ip_port \"192.168.68.141:8080\" --target_mac \"94:DB:56:02:E2:46\" --id $2 &; sudo hciconfig hci0 down; sudo hciconfig hci0 up; cd btlemonrun/build/; sudo sh -c \"hcitool lescan --duplicates >/dev/null & ./btlemonrun | nc -U /tmp/btlemon.sock\" &"
}

PI1="192.168.68.131"
PI2="192.168.68.136"
PI3="192.168.68.144"
PI4="192.168.68.147"

setup "$PI1" "1"
setup "$PI2" "2"
setup "$PI3" "3"
setup "$PI4" "4"

EOL