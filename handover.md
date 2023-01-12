## libraries:
- framework: PySimpleGUI (tkinter)
- other: tesseract (google NLP)
    1. pytesseract
    2. tesseract.exe

## architecture
- run program (incomplete, hardcoded path): main.py
- entry: workspace
    1. `show_workspace` function: working - workspace.py
    2. `Workspace` class: try to refactor but failed
- main component: `graph_handler: GraphHandler`
- important handlers: `CursorHandler`, `NewLabelHandler` (click_handler.py), `UpdateLabelHandler`, etc
- design patterns: 
    1. responsibility chain pattern (event handler)
    2. observer pattern (model/view)

## manual operations
1. Delete all labels: delete all label obj in json file
2. remove "click any empty place to create new pair"

## Todo
1. update name of "create new" component (there might be bugs)
2. export: different export requirement from Yutian

