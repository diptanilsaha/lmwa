def strip_dict_keys(d: dict) -> dict:
    keys = d.keys()
    new_dict = {}
    for k in keys:
        new_dict[k.strip()] = d[k]

    return new_dict