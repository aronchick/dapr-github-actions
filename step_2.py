import contextlib
from datetime import datetime
import threading
from time import sleep

from dapr.proto.runtime.v1 import dapr_pb2_grpc
from context import WorkflowContext
from os import urandom
from dapr.clients import DaprClient

from dapr.clients.grpc._request import (
    TransactionalStateOperation,
    TransactionOperationType,
)
from dapr.clients.grpc._state import StateItem, StateOptions, Consistency, Concurrency
from random import randint

from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import concurrent

import os

from uuid import uuid4

key_name = "ContentiousKey"
step_name = "step_2"
etag = ''

def execute_step(args_tuple):
    daprClient = args_tuple[0]
    thread_number = args_tuple[1]
    state_store = args_tuple[2]

    current_value = daprClient.get_state(store_name=state_store, key=key_name)
    etag = current_value.etag

    if thread_number == 0:
        etag=current_value.etag
    else:
        etag=99999999

    value = f"ContentiousValue-{thread_number}"
    print(
        f"Thread-{thread_number}: {key_name} == null. New value: {value}",
        flush="True",
    )
    try:
        g = daprClient.save_state(
            store_name=state_store,
            key=key_name,
            value=value,
            etag=etag,
            options=StateOptions(
                consistency=Consistency.strong, concurrency=Concurrency.first_write
            ),
        )
        h = daprClient.get_state(store_name=state_store, key=key_name)
        if value == str(h.data, 'utf8'):
            print(
            f"Wrote {{ {key_name}: {h.data} }} to DB at {datetime.now().isoformat()} with etag = {h.etag}",
            flush=True,
        )
        else:
            print(f"Failed to write due to contention. 'Winning' value == {h.data}")
    except Exception as e:
        h = daprClient.get_state(store_name=state_store, key=key_name)
        print(
            f"Failed to write state from Thread-{thread_number} due to concurrency issue. Using stored value: {h.data}",
            flush=True,
        )


with WorkflowContext(step_name) as context:
    with DaprClient(context["dapr_address"]) as d:
        # Clearing old value
        state_store = os.environ.get("STATE_STORE_NAME")
        d.delete_state(store_name=state_store, key=key_name)
        d.save_state(store_name=state_store, key=key_name, value="BADVALUE")


        # Create 10 fake threads to mimic multiple workers
        all_threads = []
        for i in range(10):
            all_threads.append((d, i, state_store))

        with ThreadPoolExecutor(max_workers=12) as executor:
            executor.map(execute_step, all_threads)

        final_data = d.get_state(state_store, key_name)
        context.set_value(f"{step_name}: Final Value", str(final_data.data, "utf8"))
        context.set_value(f"{step_name}: Random Value", uuid4().hex)

