from cloudevents.sdk.event import v1
from dapr.ext.grpc import App

app = App()

@app.subscribe(pubsub_name='redispubsub', topic='longRunningTasks')
def mytopic(event: v1.Event) -> None:
    print(event.Data(),flush=True)

app.run(50051)