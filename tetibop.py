#tetibop is Text Editor Based On Python
#This is special edition for any terminal supports Curses.

#The main file.
#Entry point to programm
import MainBuffer
import FileLoader

app = MainBuffer.MainBuffer(FileLoader.load_file_from_cl())
app.run()
