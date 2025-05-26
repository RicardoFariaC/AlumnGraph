<div align="center">
    <pre>
        <code>
 █████╗ ██╗     ██╗   ██╗███╗   ███╗███╗   ██╗
██╔══██╗██║     ██║   ██║████╗ ████║████╗  ██║
███████║██║     ██║   ██║██╔████╔██║██╔██╗ ██║
██╔══██║██║     ██║   ██║██║╚██╔╝██║██║╚██╗██║
██║  ██║███████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚████║
╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝

"System-Theoretic Process Analysis Graph Tool"
        </code>
    </pre>
</div>

---

Alumn is a tool that generate hierarchical models via graphviz and dot language based on a JSON file as input. This tool uses [diagrams by mingrammer](https://github.com/mingrammer/diagrams) as its backend. Alumn uses concepts from System-Theoretic Accident Model and Processes (STAMP) and hierarchical structure models.

## "Our philosophy"

## Installation & Usage

You'll need to install it before using. It can be done by using:

> ```sh
> pipx install git+'git'
> ```

From that point on, you can use the following commands.

> ```sh
> alumn paint <file_path> # Accepts only JSON files for now.
> alumn about # Shows you some general informations.
> alumn howto # Gives you a tutorial about using Alumn.
> ```

## JSON Format

###### BASE STRUCTURE

To be able to write a JSON that can be accepted by Alumn tool, you need to include the three structures:


- `controllers` - define system components.
- `groups` - optional grouping (can be empty).
- `actions` - describe the flow of actions and responses between components.

###### CONTROLLERS

Each controller is defined by an object with:

- `id` - short identifier
- `label` - human-readable name
- `level` - hierarchy representing number (lower is higher-level)

> ```json
> {
>   "controllers": [{
>       "id": "pa",
>       "label": "Platform Automation",
>       "level": 2
>   }]
> }
> ```

###### GROUPS

You can use this structure to define clusters of controllers:

> ```json
> {
>   "groups": [{
>       "id": "grp_ctrl",
>       "label": "Automation System",
>       "controllers_list": ["pa", "pc"]
>   }]
> }
> ```

###### ACTIONS

Each action describes a communication from one controller to another:

- `from` - sender controller ID
- `to` - receiver controller ID
- `action` - request from sender controller
- `feedback` - expected response from receiver (it can be optinal)

> ```json
> {
>  "actions": [{
>       "from": "pa",
>       "to": "pc",
>       "action": "Automate the compiler process",
>       "feedback": "Return a signal to stop automation tool"
>   }]
> }
> ```

## Disclaimer

## Contributing
