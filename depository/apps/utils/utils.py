def sub_dict(data, keys):
    new_dict = {}
    for key in keys:
        if key in data:
            new_dict[key] = data[key]
    return new_dict


