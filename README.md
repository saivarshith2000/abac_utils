### ABAC
Command-line tool to manage the ABAC linux security module.

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
None of the above subcommands, except `abac obj` are available to normal users. The tool is mainly meant to be used by the admin (root).  
