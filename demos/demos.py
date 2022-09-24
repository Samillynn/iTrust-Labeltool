import PySimpleGUI as sg

# choice, _ = sg.Window('Continue?', [[sg.T('Do you want to continue?')], [sg.Yes(s=10), sg.No(s=10)]],
#                       disable_close=True).read(close=True)

# sg.Window('X', [[sg.T('Name'), sg.I(key='-NAME-')],
#                 [sg.T('Type'), sg.DD(['Tank', 'Pipe', 'Other types'])],
#                 [sg.Submit(), sg.Exit()]]).read()

import PySimpleGUI as sg

layout = [[
    sg.InputText(key='file_save_as_input', enable_events=True, default_text='filename'),
    sg.FileSaveAs(key='file_save_as_key',  initial_folder='/tmp')
]]
window = sg.Window('', layout)

while True:
    event, values = window.Read()
    print("event:", event, "values: ",values)
    if event is None or event == 'Exit':
        break

# event, values = sg.Window('Login Window',
#                   [[sg.T('Enter your Login ID'), sg.In(key='-ID-')],
#                   [sg.B('OK'), sg.B('Cancel') ]]).read(close=True)
# login_id = values['-ID-']
# print(event, login_id)


# sg.theme('BluePurple')
#
# layout = [[sg.Text('Your typed chars appear here:'), sg.Text(size=(15,1), key='-OUTPUT-')],
#           [sg.Input(key='-IN-')],
#           [sg.Button('Show'), sg.Button('Exit')]]
#
# window = sg.Window('Pattern 2B', layout)
#
# while True:  # Event Loop
#     event, values = window.read()
#     print(event, values)
#     if event == sg.WIN_CLOSED or event == 'Exit':
#         break
#     if event == 'Show':
#         # Update the "output" text element to be the value of "input" element
#         window['-OUTPUT-'].update(values['-IN-'])
#
# window.close()
