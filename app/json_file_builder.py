import json

def write_json(filename, data):
    outfile = open(filename, 'w')
    json.dump(data, outfile)
    outfile.close()
    return outfile

def get_has_manifest(repo_name, suffix, is_valid):
    if is_valid:
        color = "brightgreen"
    else:
        color = "red"
    
    data = {}
    data["schemaVersion"] = 1
    data["label"] = "valid"
    data["message"] = str(is_valid).lower()
    data["color"] = color

    filename = repo_name + suffix + ".json"
    return write_json(filename, data)

def get_num_invalid_usfm(repo_name, suffix, num_invalid):
    if num_invalid > 0:
        color = "red"
    else:
        color = "brightgreen"

    data = {}
    data["schemaVersion"] = 1
    data["label"] = "invalid USFM docs"
    data["message"] = str(num_invalid)
    data["color"] = color

    filename = repo_name + suffix + ".json"
    return write_json(filename, data)