#MainBuffer contains field with text and action line.
import curses as cs
import keyboard as kb
from msvcrt import kbhit
from Keys import Keys
from FileLoader import load_file

class CursorPos():
    def __init__(self):
        self.x = 0
        self.y = 0

class MainBuffer():
    def __init__(self,lines):
        self.lines = lines
        self.action_line = 'welcome to tetibop!'
        
        self.quiting = False

        self.cursor_pos = CursorPos()

        self.move_forward_pressed = False
        self.move_backward_pressed= False
        self.move_up_pressed = False
        self.move_donw_pressed = False
        
    def init_colors(self):
        cs.init_pair(1,cs.COLOR_RED,cs.COLOR_GREEN)
        cs.init_pair(2,cs.COLOR_WHITE,cs.COLOR_CYAN)
        
    def print_action_line(self,screen):
        '''put the action line at very end of terminal'''
        height, width = screen.getmaxyx()
        self.action_line += ' '*(width-len(self.action_line)-1)
        y_pos= height-1
        screen.addstr(y_pos,0,self.action_line,cs.color_pair(1))
        screen.refresh()
    def print_all_lines(self,screen):
        '''print file lines untill action line'''
        height, width = screen.getmaxyx()
        end_y = height-2
        y_pos = 0
        while y_pos < end_y and y_pos < len(self.lines):
            line = self.lines[y_pos]
            screen.addstr(y_pos,0,line)
            screen.refresh()
            y_pos+=1
    def print_cursor(self,screen):
        char = ''
        if len(self.lines) > 0 and len(self.lines[self.cursor_pos.y]) > 0:
            char = self.lines[self.cursor_pos.y][self.cursor_pos.x]
        screen.addstr(self.cursor_pos.y,self.cursor_pos.x,char,cs.color_pair(2))
            
    def process_key(self,screen):
        '''do command related to key code'''

        #quiting
        if kb.is_pressed(Keys["quit"]):
            self.action_line = "do you want to quit?(y/n)"
            self.quiting = True
        if kb.is_pressed("y") and self.quiting:
            exit(0)
        if kb.is_pressed("n") and self.quiting:
            self.quiting = False
            self.action_line = "done!"
        ##

        #loading
        if kb.is_pressed(Keys["open"]):
            height, width = screen.getmaxyx()
            y_pos = height - 1 
            self.action_line ="enter file path:"
            self.print_action_line(screen)
            
            x_pos = len(self.action_line)+1
            
            #self.cursor_pos.x = x_pos-1
            #self.cursor_pos.y = y_pos
            #self.print_cursor(screen)
            
            self.lines.clear()
            screen.clear()
        
        #moving
        def can_move(x,y):
            if x < 0 or y < 0:
                return False
            
            along_y = y < len(self.lines)
            if along_y and x < len(self.lines[y]):
                return True
            return False

        if kb.is_pressed(Keys["movef"]) and not self.move_forward_pressed:
            new_x = self.cursor_pos.x + 1
            if can_move(new_x,self.cursor_pos.y):
                self.cursor_pos.x = new_x
            else:
                self.action_line = "can not move forward!"
            self.move_forward_pressed = True
        if kb.is_pressed(Keys["moveb"]) and not self.move_backward_pressed:
            new_x = self.cursor_pos.x - 1
            if can_move(new_x,self.cursor_pos.y):
                self.cursor_pos.x = new_x
            else:
                self.action_line = "can not move back!"
            self.move_backward_pressed = True
        if kb.is_pressed(Keys["movep"]) and not self.move_up_pressed:
            new_y = self.cursor_pos.y - 1
            if can_move(self.cursor_pos.x,new_y):
                self.cursor_pos.y = new_y
            else:
                self.action_line = "can not move to previous line!"
            self.move_up_pressed = True
        if kb.is_pressed(Keys["moven"]) and not self.move_down_pressed:
            new_y = self.cursor_pos.y + 1
            _can_move = can_move(self.cursor_pos.x,new_y)
            if _can_move:
                self.cursor_pos.y = new_y
            if not _can_move and new_y < len(self.lines):
                line = self.lines[new_y]
                if len(line) == 0:
                    self.cursor_pos.x = 0
                else:
                    self.cursor_pos.x = len(line)-1
                self.cursor_pos.y = new_y
            else:
                self.action_line = "can not move to next line!"
            self.move_down_pressed = True

        back_forward_not_pressed = not kb.is_pressed(Keys["movef"]) and not kb.is_pressed(Keys["moveb"])
        up_down_not_pressed      = not kb.is_pressed(Keys["movep"]) and not kb.is_pressed(Keys["moven"])
        not_pressed = back_forward_not_pressed and up_down_not_pressed
        if not_pressed:
           self.move_forward_pressed  = False
           self.move_backward_pressed = False
           self.move_up_pressed       = False
           self.move_down_pressed     = False
        
    def _run(self,screen):
        '''function runs the whole programm, but it's used by curses wrapper'''
        screen.clear()
        self.init_colors()
        cs.curs_set(0)
        
        while True:
            self.print_action_line(screen)
            self.print_all_lines(screen)
            self.print_cursor(screen)

            self.process_key(screen)
            
            screen.refresh()
            cs.delay_output(90)
    def run(self):
        '''inits screen and do all curses staff and call function to run application'''
        cs.wrapper(self._run)
    
