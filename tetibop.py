#tetibop is Text Editor Based On Python
#This is special edition for any terminal supports Curses.

#The main file.
#Entry point to programm
import MainBuffer
import FileLoader

data = FileLoader.load_file_from_cl()
file_name = ''
lines = []
if len(data) >1:
    file_name = data[1]
    lines = data[0]
app = MainBuffer.MainBuffer(lines,file_name)
app.run()
