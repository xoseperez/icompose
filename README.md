# iCOMPOSE - Interactive Docker Compose Terminal Utility

This tool is meant to manage docker stacks defined in docker-compose.yml files. 

The tool leverages the possibility to add extra tags to docker-compose.yml files from Docker Compose version 3.4 onwards to define metadata about the services in a `x-icompose` tag on the compose file itself. Therefore, both the stack configuration and the metadata are in the same file.

# Using it

This project is a Work In Progress, so proper installation procedure is not yet in place. 

If you want to test it, the recommended way is using `make`. You will need `make` (usually preinstalled on Linux boxes) and also `python3-virtualenv` to create a sandbox to install dependencies. 


For example, for debian-based distros you will:

```
sudo apt install make python3-virtualenv
```

The first time you run `make run` it will create the sandbox and install dependencies. Once done, it will enter the sandbox and run the `icompose` script directly.

```
> make run
set -e ; . .venv/bin/activate ; python3 icompose

iCOMPOSE v0.0.1
Interactive Docker Compose Utility
(c) Xose Pérez <xose.perez@gmail.com>

-----------------------------------------------------------------
Main menu
-----------------------------------------------------------------
[ 1] Create Service 
[ 2] Manage Existing Services 
[ 3] System Maintenance 
[ 4] Exit 

Choose option: 

```

If you don't want to use `make`, you can init the sandbox and run the script manually (from the root folder of the repo):


```
> virtualenv .venv
(...)
> source .venv/bin/activate
(.venv) > pip install -r requirements.txt
(...)
(.venv) > python3 icompose

iCOMPOSE v0.0.1
Interactive Docker Compose Utility
(c) Xose Pérez <xose.perez@gmail.com>

-----------------------------------------------------------------
Main menu
-----------------------------------------------------------------
[ 1] Create Service 
[ 2] Manage Existing Services 
[ 3] System Maintenance 
[ 4] Exit 

Choose option: 

```

Quit the sandbox typing `deactivate`.
