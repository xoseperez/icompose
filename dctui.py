import os
import sys
import time
import flatdict
import yaml
import logging
import json
import socket
import subprocess
import random
import string

# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

APP_NAME = "DCTUI"
APP_VERSION = "v0.0.1"

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------

class Config():

    _data = flatdict.FlatDict({})
    _args = None
    _dirty = False

    def __init__(self, file=None, args={}):
        
        try:
            with open(file or "config.yml", "r") as f:
                _data =  yaml.load(f, Loader=yaml.loader.SafeLoader)
        except FileNotFoundError:
            _data = {'logging': {'level' : logging.INFO}}
        
        self._data = flatdict.FlatDict(_data, delimiter='.')

        # filter out "None" values
        for key in self._data:
            if self._data[key] == None:
                del self._data[key]

        self._args = args

    def get(self, key, default=None):
        
        # External name
        env_name = key.upper().replace('.', '_').replace('-', '_')

        # Arguments have precedence over `config.yml` but do not get persisted
        value = self._args.get(env_name, None)
        
        # Environment variables have precedence over `config.yml` but do not get persisted
        if value is None:
            value = os.environ.get(env_name, None)
        
        # Get the value from `config.yml` or the default
        if value is None:
            value = self._data.get(key)

        if value is None:
            value = default

        return value

    def set(self, key, value):
        if self._data.get(key) != value:
            self._data[key] = value
            self._dirty = true

    def save(self):
        if self._dirty:
            try:
                with open(self._file, "w") as f:
                    yaml.dump(self._data.as_dict(), f, default_flow_style=False)
                self._dirty = False
            except FileNotFoundError:
                None

    def unflat(self):
        return self._data.as_dict()

    def dump(self):
        print(json.dumps(self._data.as_dict(), sort_keys=True, indent=4))


# -----------------------------------------------------------------------------
# Utils
# -----------------------------------------------------------------------------

class color:

    black = "\033[90m"
    red = "\033[91m"
    green = "\033[92m"
    orange = "\033[93m"
    blue = "\033[94m"
    purple = "\033[95m"
    cyan = "\033[96m"
    white = "\033[97m"
    
    reset = '\033[0m'
    bold = "\033[1m"
    underline = "\033[4m"
    reverse = "\033[7m"
    clear = "\033[2J\033[H"

    ask = orange
    error = red
    info = green
    header = blue


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('8.8.8.8', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
    
# -----------------------------------------------------------------------------
# Logic
# -----------------------------------------------------------------------------

def write_stack_default(index, defaults):
    None

def get_stacks():
    stacks = []
    try:
        command="docker compose ls -a --format json"
        p = subprocess.run(command, shell=True, capture_output=True)
        output = json.loads(p.stdout.decode().strip())
        for stack in output:
            stacks.append({
                'name': stack['Name'],
                'running': (stack['Status']).startswith('running')
            })
    except:
        None
    return stacks

def read_stacks(config):
    
    stacks=[]

    try:
        folders=[x[0] for x in os.walk(config.get('stacks.folder'))]
        folders.sort()
    except:
        folders=[]
    
    for folder in folders:
        files = os.listdir(folder)
        for file in files:
            file = folder + "/" + file
            if not os.path.isfile(file):
                continue
            if not file.endswith(".yml") and not file.endswith(".yaml"):
                continue
            data={}
            with open(file, 'r') as h:
                data = yaml.safe_load(h)
            if "x-dctui" in data:
                slug = folder.split('/')[-1]
                stacks.append({
                    "slug": slug,
                    "file": file,
                    "data": data['x-dctui'],
                })
    
    return stacks


def show_header(text):
    print(f"{color.header}-----------------------------------------------------------------{color.reset}")
    print(f"{color.header}{color.bold}{text}{color.reset}")
    print(f"{color.header}-----------------------------------------------------------------{color.reset}")

'''
Options is a list of option objects
Each option has a name and a descripction that will be show in brackets
'''
def show_menu(title, options):

    error = False
    num_options = len(options)
    if num_options == 0:
        return 0

    while (True):
    
        print(f"{color.reset}")
        if error:
            print(f"{color.error}{color.bold}Invalid option. Try again.{color.reset}\n") 
            error = False 
        show_header(title)         
        for index in range(num_options):
            name = options[index]['name']
            description = options[index].get('description',None)
            print(f"[{color.ask}{index+1:2d}{color.reset}] {name} {color.info+'('+description+')'+color.reset if description else ''}")

        try:
            ans = int(input(f"\n{color.ask}Choose option: {color.white}"))
            if (0 < ans) and (ans <= num_options):
                return ans-1
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            ans = 0
        error = True
       
def replace_value(value):
    if isinstance(value, str):
        value = value.replace("{{IP}}", get_ip())
        value = value.replace("{{RANDOM16}}", get_random_string(16))
        value = value.replace("{{RANDOM32}}", get_random_string(32))
    return value

def get_field(title, default):

    default = replace_value(default)
    prompt=f"{title} [{default}]"
    try:
        ans = input(f"{color.ask}{prompt}: {color.white}") or default
    except KeyboardInterrupt:
        sys.exit(1)

    return ans

def get_field_options(title, default, options):

    num_options = len(options)

    try:
        default = options.index(default)
    except ValueError:
        default = 1
    
    print(f"{color.ask}{title}:{color.reset}")
    for index in range(num_options):
        print(f"[{color.ask}{index+1:2d}{color.reset}] {options[index]}")
    
    ans=0
    while 0 == ans:
        try:
            ans = int(get_field("Select option", default+1))
            if (ans < 1) or (ans > num_options):
                ans = 0
        except KeyboardInterrupt:
            sys.exit(1)
        except:
            ans = 0

    return options[ans-1]

def yesno(prompt):

    try:
        ans = input(f"{color.ask}{prompt} [y/N]: {color.white}") or 'N'
    except KeyboardInterrupt:
        sys.exit(1)

    return ans.upper() == 'Y'

# -----------------------------------------------------------------------------
# Menus
# -----------------------------------------------------------------------------

def configure_service_menu(index):

    options = []
    stack = stacks[index]
    options.append({'name': 'Exit'})

    print()
    show_header(f"Configure {stack['data']['name']}")
    slug = get_field("Stack name", stack['slug'])

    fields = stack['data'].get('fields', [])
    envs = {}
    for field in fields:
        if 'options' in field:
            envs[field['name']] = get_field_options(field.get('description', field.get('name')), field['default'], field['options'])
        else:
            envs[field['name']] = get_field(field.get('description', field.get('name')), field['default'])
    
    print(f"\n{color.info}I will start stack {slug} using this configuration: {envs}{color.reset}")
    proceed = yesno("Proceed?")
    if proceed:
        print(f"{color.info}\nBringing up {slug} stack{color.reset}")
        env_string = ' '.join([f"{key}={envs[key]}" for key in envs])
        command = f"{env_string} docker compose -f {stack['file']} -p {slug} up -d"
        p = subprocess.run(command, shell=True)
        if p.returncode == 0:
            print(f"{color.info}\nService succesfully started{color.reset}")
        else:
            print(f"{color.error}\nError starting service{color.reset}")
            command = f"docker compose -p {slug} down"
            p = subprocess.run(command, shell=True)


def manage_stack_menu(stack):

    options = [{'name': option} for option in [f"{'Stop' if stack['running'] else 'Start'}", 'Destroy', 'Logs', 'Exit']]

    while (True):
        selected = show_menu(f"Manage stack {stack['name']}", options)
        if 0 == selected:
            command=f"docker compose -p {stack['name']} {'stop' if stack['running'] else 'start'}"
            p = subprocess.run(command, shell=True)
            return True
        elif 1 == selected:
            command=f"docker compose -p {stack['name']} down"
            p = subprocess.run(command, shell=True)
            return True
        elif 2 == selected:
            command=f"docker compose -p {stack['name']} logs -f"
            try:
                p = subprocess.run(command, shell=True)
            except KeyboardInterrupt:
                None
            except:
                sys.exit(1)
        else:
            return False

def existing_stacks_menu():

    options = get_stacks()
    options.append({'name': 'Exit'})

    while (True):
        selected = show_menu("Existing stacks", options)
        if selected < len(options)-1:
            if manage_stack_menu(options[selected]):
                return
        else:
            return

def create_stack_menu():

    global stacks
    options=[ {"name": stack['data']['name'], "description": stack['data'].get('description', '')} for stack in stacks]
    options.append({'name': 'Exit'})

    while (True):
        selected = show_menu("Create stack", options)
        if selected < len(options)-1:
            configure_service_menu(selected)
        else:
            return

def main_menu():

    options=[
        {'name': "Create stack"},
        {'name': "Manage stack"},
        {'name': "Exit"},
    ]

    while (True):
        selected = show_menu("Main menu", options)
        if 0 == selected:
            create_stack_menu()
        elif 1 == selected:
            existing_stacks_menu()
        else:
            return


# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    
    # Welcome message
    print(f"\n{color.header}{color.bold}{APP_NAME} {APP_VERSION}{color.reset}")
    print(f"{color.header}Docker Compose Terminal User Interface{color.reset}")
    print(f"{color.header}(c) Xose Pérez <xose.perez@gmail.com>{color.reset}")

    # Load configuration file
    config = Config('config.yml')

    # Load stacks
    stacks = read_stacks(config)

    # Show menu
    main_menu()

    # Bye
    print("Exiting")




