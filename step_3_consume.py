from cloudevents.sdk.event import v1
from dapr.ext.grpc import App
import datetime
import os
import time

from uuid import uuid4
from context import WorkflowContext
from dotenv import load_dotenv
from dapr.clients.grpc.client import DaprClient

import json

load_dotenv()

step_name = "step_3_consume"
pubsub_name = "redispubsub"
topic_name = "longRunningTasks"

app = App()

@app.subscribe(pubsub_name=pubsub_name, topic=topic_name)
def longRunningTaskFinished(event: v1.Event) -> None:
    time.sleep(5)
    print(f"{step_name}: Long running task finished at {datetime.datetime.now().isoformat()}", flush=True)
    app.stop()

with WorkflowContext(step_name) as context:
    with DaprClient() as d:
        app.run(20001)

