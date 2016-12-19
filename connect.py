#!/usr/bin/python

# Copyright (C) 2016 Appformation sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from colorclass import Color
import os
import sys
import subprocess
import time


# Contains all ssh entries
ssh_entries = []


# Load and parse ssh config file and fill out ssh_entries
def load_and_parse_ssh_config():

    user_dir = os.path.expanduser('~')
    with open('%s/.ssh/config' % user_dir) as f:
        content = f.readlines()

    last_entry = None
    current_letter = 96

    for entry in content:

        if entry.startswith('Host '):

            if last_entry is not None:
                ssh_entries.append(last_entry)
                last_entry = None

            if last_entry is None:
                last_entry = {}
                current_letter += 1
                if current_letter == 58:
                    current_letter = 97

            last_entry['key'] = current_letter
            last_entry['name'] = entry[5:].strip()

        elif entry.strip().startswith("HostName "):
            last_entry['host'] = entry.strip()[9:]
        elif entry.strip().startswith("User "):
            last_entry['user'] = entry.strip()[5:]

    if last_entry is not None:
        ssh_entries.append(last_entry)


# Print header
def print_header():

    print ""
    print Color("  {autocyan}EasyConnect{/autocyan}")
    print Color("  {autocyan}-----------{/autocyan}")
    print Color("  {autoyellow}Select ssh configuration to launch{/autoyellow}")
    print ""


# Print list of all entries
def print_list_of_entries():

    for entry in ssh_entries:
        print Color("  {autocyan}" + chr(entry['key']) + "){/autocyan} {autowhite}" + entry['name'] + "{/autowhite}")

    print ""


# Wait for a key press on the console and return it
# Found on http://stackoverflow.com/a/34956791/2024830
# Credits goes to Gringo Suave
def wait_key():

    result = None
    print Color("  {autowhite}>{/autowhite}"),

    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        old_term = termios.tcgetattr(fd)
        new_attr = termios.tcgetattr(fd)
        new_attr[3] = new_attr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, new_attr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)
            print Color("{autoyellow}" + result + "{/autoyellow}\n")

    return result


# Launch
if __name__ == "__main__":

    print_header()

    load_and_parse_ssh_config()
    print_list_of_entries()

    key = wait_key()

    for entry in ssh_entries:
        if entry['key'] == ord(key.lower()):

            time.sleep(1)
            subprocess.call("clear")

            try:
                subprocess.call("ssh %s" % entry['name'], shell=True)
            except:
                pass
