from src.application import create_app

# import yaml
import json


def openapi(output_file):

    openapi_json = create_app().openapi()
    with open(output_file, "w") as f_:
        json.dump(openapi_json, f_, indent=4)


if __name__ == "__main__":
    openapi("openapi.json")
