import json

def get(repo_name, is_valid):
    if is_valid:
        color = "brightgreen"
    else:
        color = "red"
    
    data = {}
    data["schemaVersion"] = 1
    data["label"] = "valid"
    data["message"] = str(is_valid).lower()
    data["color"] = color

    filename = repo_name + ".json"
    outfile = open(filename, 'w')
    json.dump(data, outfile)
    outfile.close()
    return outfile