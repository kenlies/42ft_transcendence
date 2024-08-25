#!/usr/bin/env bash

echo "Checking for required packages..."

if ! hash python3 &>/dev/null; then
	echo "Python is not installed. Exiting..."
	exit 1
fi

if python3 -c 'import sys; sys.version_info.major >= 3 and sys.version_info.minor >= 5' 2>/dev/null; then
	echo "Python version satisfies the requirements."
else
	echo "Python version is not compatible. Exiting..."
	exit 1
fi

for p in $(cat cli_client/requirements.txt); do
	if ! python3 -c "import $p" &>/dev/null; then
		echo "$p not found. Please install $p to continue. Exiting..." >&2
		exit 1
	fi
done
echo "All required packages are installed. Starting the CLI client..."

cd cli_client

# Ignore Ctrl+Z (SIGTSTP)
trap '' TSTP

python3 -m main.py

# Restore Ctrl+Z handling
trap - TSTP
