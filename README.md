# README

This repo demonstrates using Dapr in a GitHub Action. It uses GitHub secrets to store component values.

Using the `export_secrets_to_components.py` it looks for any GitHub secret that is an environment variable that starts with 'DAPR_COMPONENT_' and writes it to the components/ directory during run.

You can also set specific values for the run at the top of the workflow (but the defaults are fine to debug):

```
DAPR_PORT: "20000"
DAPR_APP_PORT: "20001"
STATE_STORE_NAME: "redisstatestore"
PUBSUB_NAME: "kafkapubsub"
SAMPLE_KEY_NAME: "sample_key_name"
```

# Execution
To execute this workflow, simply make any change and push it. You'll be able to see all the outputs in the Actions tab.

# Debugging Locally
To debug your workflows locally, I've created `test_workflow.py` which can be used for testing local functioning and mimic the production GitHub environment.

You need to update