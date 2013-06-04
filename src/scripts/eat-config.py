#!/usr/bin/env python

from os import system
import curses
import getpass

def get_param(prompt_string):
     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, prompt_string)
     screen.refresh()
     input = screen.getstr(10, 10, 60)
     return input

def execute_cmd(cmd_string, halt=True):
     system("clear")
     a = system(cmd_string)
     print ""
     if a == 0:
	  pass
          #print "Command executed correctly"
     else:
          print "Command terminated with error"
     
     if halt:
          raw_input("Press enter")
          print ""

x = 0
user = getpass.getuser()

while x != ord('4'):
     screen = curses.initscr()

     screen.clear()
     screen.border(0)
     screen.addstr(2, 2, "EAT - Enables Automated Testing configuration")
     screen.addstr(4, 4, "1 - Add eat ssh-key for the current user (" + user + ")" )
     screen.addstr(5, 4, "2 - Add eat ssh-key for another user")
     screen.addstr(6, 4, "3 - List users")
     screen.addstr(7, 4, "4 - Exit")
     screen.refresh()

     x = screen.getch()

     if x == ord('1'):
          curses.endwin()
          execute_cmd("install-eat-key.sh")
     if x == ord('2'):
	  username = get_param("user name")
          curses.endwin()
          execute_cmd("su - " + username + " \"install-eat-key.sh \"")
     if x == ord('3'):
          curses.endwin()
          execute_cmd("cat /etc/passwd | cut -d: -f1")

curses.endwin()

