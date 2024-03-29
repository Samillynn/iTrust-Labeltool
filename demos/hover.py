import PySimpleGUI as sg

"""
    Extending PySimpleGUI using the tkinter event bindings

    The idea here is to enable you to receive tkinter "Events" through the normal place you
    get your events, the window.read() call.

    Both elements and windows have a bind method.
    window.bind(tkinter_event_string, key)   or   element.bind(tkinter_event_string, key_modifier)
    First parameter is the tkinter event string.  These are things like <FocusIn> <Button-1> <Button-3> <Enter>
    Second parameter for windows is an entire key, for elements is something added onto a key.  This key or modified key is what is returned when you read the window.
    If the key modifier is text and the key is text, then the key returned from the read will be the 2 concatenated together.  Otherwise your event will be a tuple containing the key_modifier value you pass in and the key belonging to the element the event happened to.
"""
sg.theme('Dark Blue 3')

layout = [  [sg.Text('Move mouse over me', key='-TEXT-')],
            [sg.In(key='-IN-')],
            [sg.Button('Right Click Me', key='-BUTTON-'), sg.Button('Exit')]  ]

window = sg.Window('Window Title', layout, finalize=True)

window.bind('<FocusOut>', '+FOCUS OUT+')

window['-BUTTON-'].bind('<Button-3>', '+RIGHT CLICK+')
# window['-TEXT-'].bind('<Enter>', '+MOUSE OVER+')
# window['-TEXT-'].bind('<Leave>', '+MOUSE AWAY+')
window['-TEXT-'].bind('<Motion>', '+Motion')
window['-IN-'].bind('<FocusIn>', '+INPUT FOCUS+')

while True:             # Event Loop
    event, values = window.read()
    print(event, values)
    if event in (None, 'Exit'):
        break
window.close()