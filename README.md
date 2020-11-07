# README

This repo demonstrates using Dapr in a GitHub Action. It uses GitHub secrets to store component values.

Using the `export_secrets_to_components.py` it looks for any GitHub secret that is an environment variable that starts with 'COMPONENT_' and writes it to the components/ directory during run.