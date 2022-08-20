import PySimpleGUI as sg

sg.theme('DefaultNoMoreNagging')

graph = sg.Graph(key='graph', canvas_size=(0, 0), graph_bottom_left=(-1, -1), graph_top_right=(1, 1), expand_x=True,
                 expand_y=True, float_values=True)

functional_column = [
    [sg.Text("Log Settings", justification="center")],
    [
        sg.Text("Scanned ID:", justification="center"),
        sg.Text(size=(30, 1), key="-TOUT-", justification="center", background_color="white")
    ],
    [sg.Button("Enter")],
    [sg.Button("Exit")],
    [sg.Button("Display Log")]
]
layout = [
    [
        graph,
        sg.Column(functional_column, element_justification='c')
    ]
]
window = sg.Window("Entry/Exit Log Management System", layout, location=(300, 150), resizable=True, finalize=True)
window.bind('<Configure>', '+RESIZE')
graph = window['graph']
# graph.set_size((100, 100))
while True:
    event, values = window.read()
    if event == '+RESIZE':
        graph.erase()
        # print(event, values)
        # print('before', window['graph'].get_size())
        width, height = graph.get_size()
        graph.expand_x = True

        # print('after', window['graph'].get_size())
        # print(window.size)
        width -= 2
        height -= 2
        # if width > 2*height:
        #     width = 2*height
        # else:
        #     height = int(width/2)
        graph.set_size((width, height))
        print(graph.draw_rectangle((-0.9, 0.9), (0.9, -0.9)))
    elif event is None:
        break
