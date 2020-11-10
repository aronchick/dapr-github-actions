from dapr.clients import DaprClient
from uuid import uuid4
import os

from context import WorkflowContext

step_name = "step_1"

with WorkflowContext(step_name) as context:
    with DaprClient(context["dapr_address"]) as d:
        store_name = os.environ.get('STATE_STORE_NAME')
        key = os.environ.get('SAMPLE_KEY_NAME')
        value = uuid4().hex

        print(f"Storing key locally:\n\tkey: {key}\n\tvalue: {value}")
        resp = d.save_state(store_name=store_name, key=key, value=value)

        context.set_value(f"{step_name}: Stored key/value", f"{key}-{value}")
