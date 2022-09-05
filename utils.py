import time

# noinspection PyUnresolvedReferences,PyPep8Naming
import PySimpleGUI as sg


def current_milli_time():
    return round(time.time() * 1000)


