import yaml
import os

with open(os.path.join(os.getcwd(), "config.yaml"), "r") as yaml_file:
    config = yaml.safe_load(yaml_file)

repo_id = config.get("repo_id")
model_file = config.get("model_file")

# You can now work with repo_id and model_file
print("Repo ID:", repo_id)
print("Model File:", model_file)