import PySimpleGUI as sg

layout = [[sg.Text('Window normal', size=(30, 1), key='Status')]]
window = sg.Window('Title', layout, resizable=True, finalize=True)
window.bind('<Configure>', "Configure")
status = window['Status']

while True:

    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == 'Configure':
        print(event, values, window.size)
        if window.TKroot.state() == 'zoomed':
            status.update(value='Window zoomed and maximized !')
        else:
            status.update(value='Window normal')

window.close()
