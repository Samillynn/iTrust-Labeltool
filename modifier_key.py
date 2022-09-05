ctrl = False
ctrl_down_event = 'KeyDown-Control'
ctrl_up_event = 'Control'


def listen(event):
    global ctrl
    if event == ctrl_down_event:
        ctrl = True
    elif event.startswith(ctrl_up_event):
        ctrl = False
