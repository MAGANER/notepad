#MainBuffer contains field with text and action line.
import curses as cs
import keyboard as kb
from msvcrt import kbhit
from Keys import Keys
from FileLoader import load_file
from os.path import isfile
from functools import reduce

class CursorPos():
    def __init__(self):
        self.x = 0
        self.y = 0
        self.virtual_y = 0
        self.virtual_x = 0

class MainBuffer():
    def __init__(self,lines,file_name):
        self.lines = lines
        self.action_history = []
        self.see_action_history = False
        
        self.action_line = 'welcome to tetibop!'
        
        self.action_history.append(self.action_line)

        self.see_commands = False
        
        self.quiting = False

        self.cursor_pos = CursorPos()
        self.printing_begin_y_pos = 0
        self.printing_begin_x_pos = 0
        
        self.move_forward_pressed = False
        self.move_backward_pressed= False
        self.move_up_pressed      = False
        self.move_down_pressed    = False
        self.scroll_down_pressed  = False
        self.scroll_up_pressed    = False
        self.scroll_forward_pressed = False
        self.scroll_backward_pressed= False
        self.show_next_found_word_pressed = False
        self.show_prev_found_word_pressed = False
        self.see_history_pressed = False
        self.see_commands_pressed= False
        
        self.open_file_name = file_name
        self.open_file_path = file_name
        if len(self.open_file_name) == 0:
            self.open_file_name = ":no file:"
            
        self.changed = False
        
    def init_colors(self):
        cs.init_pair(1,cs.COLOR_RED,cs.COLOR_GREEN)
        cs.init_pair(2,cs.COLOR_WHITE,cs.COLOR_CYAN)
        cs.init_pair(3,cs.COLOR_RED,cs.COLOR_WHITE)
        
    def print_action_line(self,screen):
        '''put the action line at very end of terminal'''
        height, width = screen.getmaxyx()
        self.action_line += ' '*(width-len(self.action_line)-1)
        y_pos= height-1
        screen.addstr(y_pos,0,self.action_line,cs.color_pair(1))
        screen.refresh()
    def print_state_line(self,screen):
        '''print data about file name, current line and column'''
        height, width = screen.getmaxyx()
        y_pos = height - 2
        save_status = ''
        if self.changed:
            save_status = ":changed:"
        else:
            save_status = ":saved:"
        data = save_status+" "+self.open_file_name+" "+"line="+str(self.cursor_pos.x)+" column="+str(self.cursor_pos.y)+" total lines="+str(len(self.lines))
        data+=' '*(width-len(data)-1)
        screen.addstr(y_pos,0,data,cs.color_pair(3))
        
    def print_all_lines(self,screen,lines):
        '''print file lines untill action line'''
        height, width = screen.getmaxyx()
        end_y = height-3
        line_number = self.printing_begin_y_pos
        y_pos = 0
        while y_pos < end_y and line_number < len(lines):
            line = lines[line_number][self.printing_begin_x_pos:]
            screen.addstr(y_pos,0,line)
            screen.refresh()
            y_pos+=1
            line_number+=1
    def print_cursor(self,screen,lines):
        char = ''
        if self.cursor_pos.y+self.cursor_pos.virtual_y < len(lines):
            curr_line_len = len(lines[self.cursor_pos.y+self.cursor_pos.virtual_y])
            if self.cursor_pos.x+self.cursor_pos.virtual_x < curr_line_len:
                char = lines[self.cursor_pos.virtual_y+self.cursor_pos.y][self.cursor_pos.x+self.cursor_pos.virtual_x]
        screen.addstr(self.cursor_pos.y,self.cursor_pos.x,char,cs.color_pair(2))

    #string processing
    def clear_str(self,string):
        '''take substr between ' and ' '''
        beg = string.find("'")
        end = string.rfind("'")
        return string[beg+1:end]
    def get_file_name(self,string):
        end = string.rfind("/")
        return string[end+1:]
    def save_file(self,path):
        with open(path,"w") as f:
            f.seek(0)
            f.truncate()
            for l in self.lines:
                f.write(l+"\n")

    #finding
    def find_all(self, word, screen):
        '''returns the tuple list of position where first is line number'''
        result = []
        
        def find_all_in_line(word,line,begin):
            x_poses = []
            pos = line.find(word,begin)
            while True:
                if pos == -1:
                    break
                else:
                    x_poses.append(pos)
                    pos = line.find(word,pos+1)
            return x_poses

        y_counter = 0
        for l in self.lines:
            x_poses = find_all_in_line(word,l,0)
            if x_poses != None and len(x_poses) > 0:
                sub_results = []
                for x in x_poses:
                    sub_results.append((y_counter,x))
                for res in sub_results:
                    result.append(res)
            y_counter += 1

        width, height = screen.getmaxyx()
        additional_data = ["lines: "]
        add_data_string = ""
        elem_counter = 0
        max_elem = -1
        for l in result:
            additional_data.append(str(l)+" ")
            length = len(reduce(lambda x,y: x+ y,additional_data))
            if length > width:
                max_elem = elem_counter - 1
            elem_counter += 1
        if max_elem != -1:
            visible_elems = additional_data[:max_elem+1]
            add_data_string = reduce(lambda x,y: x + y,visible_elems)
            self.action_history.append(add_data_string)

            not_visible_elems = additional_data[max_elem+2:]
            data = reduce(lambda x,y : x + y, not_visible_elems)
            self.action_history.append(data)
        else:
            add_data_string = reduce(lambda x,y: x + y,additional_data)
            self.action_history.append(add_data_string)
            
        self.action_line = "total found number is "+str(len(result))
        if len(result):
            self.action_line += " "+add_data_string
        self.print_action_line(screen)
    ##
    
    def process_key(self,screen):
        '''do command related to key code'''

        if kb.is_pressed(Keys["seehistory"]) and not self.see_history_pressed:
            if self.see_action_history:
                self.see_action_history = False
            else:
                self.see_action_history = True
            screen.clear()

            self.cursor_pos = CursorPos()
            self.see_history_pressed = True
            
        #searching
        if kb.is_pressed(Keys["search"]):
            height, width = screen.getmaxyx()
            self.action_line = "enter word to find:"
            self.print_action_line(screen)

            y_pos = height -1
            x_pos = 20
            cs.echo()
            word = self.clear_str(str(screen.getstr(y_pos,x_pos)))
            cs.noecho()
            self.find_all(word,screen)
        #
        
        #quiting
        if kb.is_pressed(Keys["quit"]):
            self.action_line = "do you want to quit?(y/n)"
            self.quiting = True
            self.action_history.append(self.action_line)
        if kb.is_pressed("y") and self.quiting:
            exit(0)
        if kb.is_pressed("n") and self.quiting:
            self.quiting = False
            self.action_line = "done!"
            self.action_history.append(self.action_line)
        ##

        #create new file
        if kb.is_pressed(Keys["createn"]):
            height, width = screen.getmaxyx()
            y_pos = height - 1
            self.action_line ="enter new file name:"
            self.action_history.append(self.action_line)
            self.print_action_line(screen)

            x_pos = 21
            cs.echo()
            name = screen.getstr(y_pos,x_pos)
            name = self.clear_str(str(name))
            cs.noecho()
            self.lines.clear()
            screen.clear()
            self.cursor_pos.x = 0
            self.cursor_pos.y = 0
            self.open_file_name = name
            self.action_line = f"{name} file is created!"
            self.action_history.append(self.action_line)
        ##
            
        
        #loading
        if kb.is_pressed(Keys["open"]):
            height, width = screen.getmaxyx()
            y_pos = height - 1 
            self.action_line ="enter file path: "
            self.action_history.append(self.action_line)
            self.print_action_line(screen)
            
            x_pos = 16
            cs.echo()
            path = screen.getstr(y_pos,x_pos)
            cs.noecho()
            if isfile(path):
                screen.clear()
                self.lines = load_file(path)
                self.print_all_lines(screen)
                self.action_line = f"{path} is loaded!"
                self.print_action_line(screen)
                self.cursor_pos.x = 0
                self.cursor_pos.y = 0
                self.open_file_path = (str(path).replace("'",'')).replace("b",'')
                self.open_file_name = self.get_file_name(self.clear_str(str(path)))
            else:
                self.action_line = f"{path} does not exist!"
                self.print_action_line(screen)
            self.action_history.append(self.action_line)


        #save file
        if kb.is_pressed(Keys["save"]):
            self.action_line="enter path file:"
            self.action_history.append(self.action_line)
            self.print_action_line(screen)
            path = ""

            height, width = screen.getmaxyx()
            y_pos = height - 1
            x_pos = 16

            cs.echo()
            path = screen.getstr(y_pos,x_pos)
            self.save_path = path
            cs.noecho()
            
            self.save_file(path)
            
            self.action_line = f"{path} is saved!"
            self.action_history.append(self.action_line)
        if kb.is_pressed(Keys["savef"]):
            self.save_file(self.open_file_path)
            self.action_line = f"{self.open_file_path} is saved!"
            self.action_history.append(self.action_line)

        if kb.is_pressed(Keys["seecommands"]) and not self.see_commands_pressed:
            if self.see_commands:
                self.see_commands = False
            else:
                self.see_commands = True
            screen.clear()
            self.cursor_pos = CursorPos()
            self.see_commands_pressed = True
            
        #go to line
        if kb.is_pressed(Keys["goto"]):
            self.action_line ="enter line number: "
            self.action_history.append(self.action_line)
            self.print_action_line(screen)
            height, width = screen.getmaxyx()
            y_pos = height - 1
            x_pos = 18
            cs.echo()
            line = screen.getstr(y_pos,x_pos)
            cs.noecho()
            if line.isdigit():
                if int(line) > len(self.lines):
                    self.action_line = "line number is more then total lines' length!"
                else:
                    self.cursor_pos.x = 0
                    self.cursor_pos.y = int(line)
                    self.action_line  = f"moved to {line} line!"
            else:
                self.action_line = f"{line} is not number!"

            self.action_history.append(self.action_line)
            
        
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
            if can_move(new_x,self.cursor_pos.y+self.cursor_pos.virtual_y):
                self.cursor_pos.x = new_x
                self.action_line = "move forward"
            else:
                self.action_line = "can not move forward!"            
            self.move_forward_pressed = True
            self.action_history.append(self.action_line)
            
        if kb.is_pressed(Keys["moveb"]) and not self.move_backward_pressed:
            new_x = self.cursor_pos.x - 1
            if can_move(new_x,self.cursor_pos.y+self.cursor_pos.virtual_y):
                self.cursor_pos.x = new_x
                self.action_line = "move backward"
            else:
                self.action_line = "can not move back!"      
            self.move_backward_pressed = True
            self.action_history.append(self.action_line)
            
        if kb.is_pressed(Keys["movep"]) and not self.move_up_pressed:
            new_y = self.cursor_pos.y - 1
            if can_move(self.cursor_pos.x,new_y):
                self.cursor_pos.y = new_y
                self.action_line = "move to previous line"
            else:
                self.action_line = "can not move to previous line!"            
            self.move_up_pressed = True
            self.action_history.append(self.action_line)
            
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
                self.action_line = "move to next line"
            else:
                self.action_line = "can not move to next line!"         
            self.move_down_pressed = True
            self.action_history.append(self.action_line)

        #scrolling
        if kb.is_pressed(Keys["scrolld"]) and not self.scroll_down_pressed:
            if self.printing_begin_y_pos < len(self.lines):
                self.printing_begin_y_pos += 1
                self.cursor_pos.virtual_y += 1
                screen.clear()
                self.action_line = "scroll down"
                self.print_action_line(screen)
            else:
                self.action_line = "can not scroll down!"
                self.print_action_line(screen)
            self.action_history.append(self.action_line)
            self.scroll_down_pressed = True
            
        if kb.is_pressed(Keys["scrollup"]) and not self.scroll_up_pressed:
            if self.printing_begin_y_pos > 0:
                self.printing_begin_y_pos -= 1
                self.cursor_pos.virtual_y -= 1
                screen.clear()
                self.action_line = "scroll up"
                self.print_action_line(screen)
            else:
                self.action_line = "can not scroll up!"
                self.print_action_line(screen)
            self.action_history.append(self.action_line)
            self.scroll_up_pressed = True
            
        if kb.is_pressed(Keys["scrollf"]) and not self.scroll_forward_pressed:
            max_elem_len = len(max(self.lines))
            if self.printing_begin_x_pos < max_elem_len:
                self.printing_begin_x_pos += 1
                self.cursor_pos.virtual_x += 1
                screen.clear()
                self.action_line = "scroll forward"
            else:
                self.action_line = "can not scroll forward!"
                self.print_action_line(screen)
            self.action_history.append(self.action_line)
            self.scroll_forward_pressed = True
            
        if kb.is_pressed(Keys["scrollb"]) and not self.scroll_backward_pressed:
            if self.printing_begin_x_pos > 0:
                self.printing_begin_x_pos -= 1
                self.cursor_pos.virtual_x -= 1
                screen.clear()
                self.action_line = "scroll backward"
            else:
                self.action_line = "can not scroll backward!"
                self.print_action_line(screen)
            self.action_history.append(self.action_line)
            self.scroll_backward_pressed = True
        #
        
        #
        back_forward_not_pressed = not kb.is_pressed(Keys["movef"]) and not kb.is_pressed(Keys["moveb"])
        up_down_not_pressed      = not kb.is_pressed(Keys["movep"]) and not kb.is_pressed(Keys["moven"])
        scroll_not_pressed       = not kb.is_pressed(Keys["scrollup"]) and not kb.is_pressed(Keys["scrolld"])
        scroll_along_x_not_pressed = not kb.is_pressed(Keys["scrollf"]) and not kb.is_pressed(Keys["scrollb"])
        see_hist_not_pressed = not kb.is_pressed(Keys["seehistory"])
        see_commands = not kb.is_pressed(Keys["seecommands"])
        not_pressed = back_forward_not_pressed and up_down_not_pressed and scroll_not_pressed and scroll_along_x_not_pressed and see_hist_not_pressed and see_commands
        if not_pressed:
           self.move_forward_pressed  = False
           self.move_backward_pressed = False
           self.move_up_pressed       = False
           self.move_down_pressed     = False
           self.scroll_down_pressed   = False
           self.scroll_up_pressed     = False
           self.scroll_forward_pressed= False
           self.scroll_backward_pressed= False
           self.show_next_found_word_pressed = False
           self.show_prev_found_word_pressed = False
           self.see_history_pressed = False
           self.see_commands_pressed= False
        
    def _run(self,screen):
        '''function runs the whole programm, but it's used by curses wrapper'''
        screen.clear()
        self.init_colors()
        cs.curs_set(0)
        
        while True:
            screen.move(self.cursor_pos.y+self.cursor_pos.virtual_y,self.cursor_pos.x)
            self.print_action_line(screen)

            if not self.see_commands:
                if self.see_action_history:
                    self.print_all_lines(screen,self.action_history)
                    self.print_cursor(screen,self.action_history)
                else:
                    self.print_all_lines(screen,self.lines)
                    self.print_cursor(screen,self.lines)
            else:
                data = []
                for key in Keys:
                    string = f"{key} -> {Keys[key]}"
                    data.append(string)
                self.print_all_lines(screen,data)
                self.print_cursor(screen,data)
                
            self.print_state_line(screen)
    
            self.process_key(screen)
            
            screen.refresh()
            cs.delay_output(50)
    def run(self):
        '''inits screen and do all curses staff and call function to run application'''
        cs.wrapper(self._run)
    
