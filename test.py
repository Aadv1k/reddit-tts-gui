import PySimpleGUI as sg
# set the theme for the screen/window
sg.theme("DarkTanBlue")
# define layout
sz = (10, 20)
col1 = [[sg.Text('Column1', background_color='red', size=sz)]]
col2 = [[sg.Text('Column2', background_color='green', size=sz)]]
col3 = [[sg.Text('Column3', background_color='yellow', size=sz)]]
col4 = [[sg.Text('Column4', background_color='blue', size=sz)]]

layout = [[sg.Pane(col1), sg.Column(col2, element_justification='c'), sg.Column(
    col3, element_justification='c'), sg.Column(col4, element_justification='c')]]

window = sg.Window("Column and Frame", layout)

event, values = window.read()

window.close()
