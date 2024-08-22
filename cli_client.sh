#!/usr/bin/env bash

pip3 install -r ./cli_client/requirements.txt >/dev/null 2>&1
cd cli_client

# Ignore Ctrl+Z (SIGTSTP)
trap '' TSTP

python3 -m main.py

# Restore Ctrl+Z handling
trap - TSTP
