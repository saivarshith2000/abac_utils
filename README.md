### ABAC
Command-line tool to manage the ABAC linux security module.

### Installation
1. Install dependencies (python3, pip and setuptools)
```bash
# On debian
sudo apt install python3-pip
pip install setuptools

# On Fedora
sudo dnf install python3-pip python3-wheel
pip install setuptools

# For other distributions, please refer to your distributions manual/documentation
```

2. Run the installation script (requires root previleges)
```bash
chmod +x install.sh
su
./install.sh
```

3. Verify that the abac command is available
```bash
which abac
```

4. Verify that the Systemd services are up and running
```bash
systemctl status abac.service
systemctl status abac_env.service
systemctl status abac_watch.service
```

### Shared Directory
Currently, a shared directory with appropriate permissions is created at `/home/secured/`. Only files in this directory are protected by ABAC LSM.

### Usage
The abac cli tool contains ALL the tool required for managing attributes and policies.  
The cli tool can be invoked using the `abac` command followed by specific commands such as `user, obj` etc.  
The main functions of the tool are explained below -   
1. `abac obj` - Manage object attributes. The available functions are `add, list, change, delete`.
2. `abac user` - Add, remove and manage users and their attributes. The available functions are `add, list, delete, manage`.
3. `abac policy` - Manage the ABAC policy. The available functions are `add, list, delete`.
4. `abac avp` - Add available attribute value pairs for objects and users. The available functions are `add, list, delete, modify`.
5. `abac load` - Load the abac attributes and policy into the kernel.
6. `abac server` - Start the ABAC attribute server. This is automaticlly done by the systemd service.
7. `abac init` - Initialize the abac config directory. This is automatically done during installation.

For each of the above subcommands, passing the flag `--help` prints the required help.
None of the above subcommands, except `abac obj` are available to normal users.
