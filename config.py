config = {
    "categories": ['Big Tank', 'Small Tank', 'Dosing Tank', 'Pumps', 'Small Pump', None],
    "display": {
        "font": {
            "format": "{parent}",
            "type": "Courier New Bold",
            "size": 8,
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
    },
    "type": ["FIT", "LIT", "LITA", "AV", "P", "AIT", "CIT", "FIC", "UV", "AIC", "PIT", "PDI", "F", "FD", "PSH", "Button"],
    "tesseract_config": "--psm 6",
}
