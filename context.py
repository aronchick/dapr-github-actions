import datetime
import subprocess
from typing import Dict, OrderedDict
import json
from json import dumps, loads
import datetime
import os
import uuid
from dotenv import load_dotenv
import collections
from random import randrange

from dapr.clients.grpc.client import DaprClient

class WorkflowContext(Dict):
    __default_state_code = "NOSHAGENERATED"
    __default_storename = "redisstatestore"
    __default_port = '20000'

    @staticmethod
    def get_dapr_port():
        dapr_port = os.environ.get("DAPR_PORT", WorkflowContext.__default_port)
        if os.environ.get("RANDOM_PORTS", None) is not None:
            dapr_port = randrange(21000, 65000)
            os.environ["DAPR_PORT"] = str(dapr_port)
            del os.environ["RANDOM_PORTS"]
        
        return dapr_port

    def __init__(self, step_name):
        load_dotenv()

        self.state_code = os.environ.get("GITHUB_SHA", self.__default_state_code)
        if os.environ.get("GENERATE_SHA") is not None and self.state_code == self.__default_state_code:
            self.state_code = uuid.uuid4().hex
            os.environ['GITHUB_SHA'] = self.state_code

        self.storename = os.environ.get("STATE_STORE_NAME", self.__default_storename)

        dapr_port = WorkflowContext.get_dapr_port()        
        self['dapr_port'] = dapr_port
        self['dapr_app_port'] = int(dapr_port) + 1

        self["dapr_address"] = f"localhost:{dapr_port}"


        dict.__init__(self)
        with DaprClient(address=self["dapr_address"]) as d:
            kv = d.get_state(self.storename, self.state_code)
            if kv.data == b"":
                kv.data = "{}"
            self.rehydrate(kv.data)


        self.start_step(step_name)

        print("==============================")
        print(f"{step_name} Output ")
        print("==============================")

    def __getitem__(self, key):
        val = dict.__getitem__(self, key)
        return val

    def __setitem__(self, key, val):
        dict.__setitem__(self, key, val)

    def dehydrate(self):
        return dumps(self)

    def rehydrate(self, state_string):
        self.update(json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(str(state_string, 'utf8')))

    def __enter__(self):
        return self

    def start_step(self, step_name):
        self["current_step_name"] = step_name
        
        if not 'steps_executed' in self:
            self['steps_executed'] = []
        
        self['steps_executed'].append(step_name)

        if not 'step_context' in self:
            self['step_context'] = {}
        
        self.set_value(f"{self['current_step_name']}: Start", datetime.datetime.now().isoformat())

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        with DaprClient(address=self["dapr_address"]) as d:
            self.end_step()
            kv = d.save_state(self.storename, self.state_code, self.dehydrate())
            os.popen(f'dapr stop --app-id {self["current_step_name"]}')
        
        print("==============================")
        print(f"Current Context: ")
        print("==============================")
        self.print_context()

    def end_step(self):
        self.set_value(f"{self['current_step_name']}: End", datetime.datetime.now().isoformat())

    def set_value(self, key, value):
        current_step_name = self["current_step_name"] 
        if not (current_step_name in self['step_context']):
            self['step_context'][current_step_name] = {}

        self['step_context'][current_step_name][key] = value

    def print_context(self):
        print(f"DAPR GRPC ADDRESS: {self['dapr_address']}", flush=True)
        print(f"CURRENT STEP NAME: {self['current_step_name']}", flush=True)
        print("STEPS EXECUTED: ", flush=True)
        for step_executed in self['steps_executed']:
            print(f" - {step_executed}", flush=True)

        print("STEP CONTEXT: ", flush=True)
        for key in self['step_context'].keys():
            print(f" == {key}:")
            for subkey in self['step_context'][key].keys():
                print(f"     --  {subkey} - {self['step_context'][key][subkey]}", flush=True)