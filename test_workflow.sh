#!/bin/bash

export GITHUB_SHA=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)
echo "Here is the sha: $GITHUB_SHA"

python3 export_secrets_to_components.py
python3 step_1.py
python3 step_2.py
dapr run --app-id step_3 --app-protocol grpc --app-port 20001 -d ./components --log-level error python3 step_3.py