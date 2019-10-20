import json

data = {}
filename = r'config.json'

def load(file):
    global data
    global filename
    print("Hey")
    filename = file
    with open(filename, 'r+') as f:
        data = json.loads(f.read())


def save():
    global data
    global filename
    with open(filename, mode='w') as f:
        f.write(json.dumps(data, indent=4, sort_keys=True))

# TODO: Verify json integrity, reset to defaults