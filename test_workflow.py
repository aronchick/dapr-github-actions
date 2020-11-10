import os
import sys
import subprocess
import select
from dotenv import load_dotenv
import time
from execute_shell_command import execute
import shutil
        
load_dotenv()
import export_secrets_to_components
from context import WorkflowContext

try:
    shutil.copy("DAPR_COMPONENT_LOCALPUBSUB.yaml.SAMPLE","components/DAPR_COMPONENT_LOCALPUBSUB.yaml")
    shutil.copy("DAPR_COMPONENT_LOCALREDIS.yaml.SAMPLE","components/DAPR_COMPONENT_LOCALREDIS.yaml")
    execute(f"dapr run --app-id dapr_sidecar -d components -P grpc -G {WorkflowContext.get_dapr_port()}")
    import step_1
    import step_2
    execute('dapr run --app-id step_3_consume --app-protocol grpc --app-port $DAPR_APP_PORT -d ./components --log-level error python3 step_3_consume.py', 1000)
    import step_3_publish
finally:
    execute('dapr stop dapr_sidecar')
