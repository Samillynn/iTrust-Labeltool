config = {
    "categories": ['Big Tank', 'Small Tank', 'Dosing Tank', 'Pumps', 'Small Pump'],
    "display": {
        "font": {
            "format": "{name}",
            "type": "Courier New Bold",
            "size": 10,
            "color": "red"
        }
    },
    "export": {
        "connection": {
            # available variables are:
            # name, fullname, category, parent, flip, rotation
            "key_format": "{name}/{fullname}",
            "val_format": "{name}/{fullname}"
        }
    }
}
