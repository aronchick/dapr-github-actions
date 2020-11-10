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

step_name = "step_3_publish"
pubsub_name = "redispubsub"
topic_name = "longRunningTasks"

with WorkflowContext(step_name) as context:
    with DaprClient(context["dapr_address"]) as d:
        context.set_value(f"{step_name}: Random Value", uuid4().hex)

        req_data = {
            'id': 0,
            'message': str(uuid4().hex)
        }

        # Create a typed message with content type and body
        resp = d.publish_event(
            pubsub_name=pubsub_name,
            topic=topic_name,
            data=json.dumps(req_data),
        )

        # Print the request
        print(req_data, flush=True)
