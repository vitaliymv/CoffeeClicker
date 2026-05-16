import json

def save_to_file(data):
    with open("save.json", "w") as file:
        json.dump(data, file, indent=4)

def load_from_file():
    try:
        with open("save.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}