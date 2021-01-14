#MainBuffer contains field with text and action line.
import curses as cs

class MainBuffer():
    def __init__(self):
        self.lines = []
        self.action_line = 'welcome to tetibop!'
        self.key_codes = {"escape":27}
        
    def init_colors(self):
        cs.init_pair(1,cs.COLOR_RED,cs.COLOR_GREEN)
        
    def print_action_line(self,screen):
        '''put the action line at very end of terminal'''
        height, width = screen.getmaxyx()
        self.action_line += ' '*(width-len(self.action_line)-1)
        y_pos= height-1
        screen.addstr(y_pos,0,self.action_line,cs.color_pair(1))
        screen.refresh()
    def process_key(self,key):
        '''do command related to key code'''
        if key == self.key_codes["escape"]:
            exit(0)
            
    def _run(self,screen):
        '''function runs the whole programm, but it's used by curses wrapper'''
        screen.clear()
        self.init_colors()
        
        while True:
            self.print_action_line(screen)

            key = screen.getch()
            self.process_key(key)

            screen.refresh()       
    def run(self):
        '''inits screen and do all curses staff and call function to run application'''
        cs.wrapper(self._run)
    
