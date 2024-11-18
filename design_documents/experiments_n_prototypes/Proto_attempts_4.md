# Attempt at protocol definition

## Protocol definition

### Main instruction file

```yaml
header:
    content: Update Instructions
    content-format: bpe-update-instruction-1.0
    category: Minecraft Modpack
    target: Bipolar Nerds Unleashed
    minecraft-modpack:
        title: Bipolar Nerds Unleashed
        website: discord.bipolarexpedition.com
        previous-version: 20241002-000
        this-version: 20240908-1409
tasks:
  - title: "Introduction"
    requests:
      - "msg://plain?title=Welcome&message=Hi user!"
  - title: "Choose options"
    requests:
      - protocol: msg-checkbox
        title: "Optional Components"
        message: "Choose the optional components you want to install."
        options:
            - Label: "(graphics) Distant Horizons"
              description: "The Distant Horrizons mods renders a lower resolution version of the world beyond your render diestance. This is useful for long distance travel. Note: Lower end computers may have performance issues."
              default: false
              variable: graphics-distant-horizons
  - title: "Install Distant Horizons"
    optional: true
    depends-on:
        - graphics-distant-horizons
    requests:
      - "add://mods/distant-horizons-1.3.1+forge-1.20.1-38.jar"
  - title: "Update mod files"
    description: "Apply updates to several of the installed mods."
    optional: false
    requests:
      - add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar
      - protocol: add
        path: /path/to/file
        files:
            - "file name.ext"
            - name: "file name2.ext"
            replace: false
            - name: "file name3.5.ext"
            old-name: "file name3.4.ext"
            - name: "file name4.7.ext"
            old-regex: "file\s+name\d+(?:\.\d+).ext"
            must-exist: true
            - name: "file name5.8.ext"
            friendly-name: "version 5.8 of file name"
  - title: "Edit the funky config file"
    description: "Apply changes to the funky config file."
    optional: false
    requests:
      - protocol: regex
        path: /path/to/file
        backup-always: false
        backup-suffix: ".bak"
        fail-on-missing: false
        changes:
            - search: "search string"
            replace: "replace string"
            options:
                - i
            - search: "search string"
            replace: "replace string"
            options: "igm"
            - "/2\/4/1\/2/ig"

```

### Request types

- [x] msg
- [x] add
- [x] upg
- [x] del
- [ ] sed
- [ ] toml


#### msg

```yaml
- protocol: msg-plain
    title: The title
    message: "Hello, user! Choose an option: (1, 2, 3)"
    options:
        - Option 1
        - Option 2
```

or 

```yaml
- protocol: msg-plain
  title: "The title"
  message: "Hello, user! Choose an option: (1, 2, 3)"
  options:
    "1": "Option 1"
    "2": "Option 2"
```

or

```yaml
- protocol: msg-plain
  title: "The title"
  message: "Here is a message"
- "msg://This is a quick and dirty message definition. It's understood, but discouraged"
- "msg://plain?title=The title&message=Hello user! Choose an option: (1, 2, 3)"
- protocol: msg-yesno
  title: "Quitting"
  message: "Are you sure you want to quit?"
  default: "No"
```

#### add

```yaml
- protocol: add
  path: /path/to/file
  files:
    - "file name.ext"
    - name: "file name2.ext"
      replace: false
    - name: "file name3.5.ext"
      old-name: "file name3.4.ext"
    - name: "file name4.7.ext"
      old-regex: "file\s+name\d+(?:\.\d+).ext"
      must-exist: true
    - name: "file name5.8.ext"
      friendly-name: "version 5.8 of file name"
```

#### del

```yaml
- protocol: del
  path: /path/to/file
  backup-always: false
  backup-suffix: ".bak"
  fail-on-missing: false
  files:
    - "file name.ext"
    - name: "file name2.ext"
      backup-always: true
      backup-suffix: ".bak"
    - name: "file name3.5.ext"
      fail-on-missing: true
    - name: "file name4.7.ext"
```

#### regex

```yaml
- protocol: regex
  path: /path/to/file
  backup-always: false
  backup-suffix: ".bak"
  fail-on-missing: false
  changes:
    - search: "search string"
      replace: "replace string"
      options:
        - i
    - search: "search string"
      replace: "replace string"
      options: "igm"
    - "/2\/4/1\/2/ig"
```


## Snippets

### parser snippets

```python
import re

def parse_msg_protocol(request: str):
    # Separate protocol and parameters
    protocol_type, query = request.split("://", 1)
    if "?" in query:
        msg_type, params = query.split("?", 1)
    else:
        msg_type, params = query, ""
    
    # Result dictionary
    result = {
        "protocol": protocol_type,
        "type": msg_type,
        "params": {}
    }

    # Parse key-value pairs
    def parse_value(value):
        # Match quoted strings, groups, or plain values
        if value.startswith(("'", '"')):
            return value[1:-1]
        elif value.startswith(("(", "{", "[")):
            return eval(value)  # Use eval for simplicity, replace for safer parsing if needed
        else:
            return value
    
    current_key = None
    current_value = []
    in_quotes = False
    escape = False
    group_stack = []

    i = 0
    while i < len(params):
        char = params[i]

        if escape:
            current_value.append(char)
            escape = False
        elif char == "\\":
            escape = True
        elif char in ('"', "'"):
            if in_quotes:
                in_quotes = False
            else:
                in_quotes = True
            current_value.append(char)
        elif char in "({[":
            group_stack.append(char)
            current_value.append(char)
        elif char in ")}]":
            if group_stack and ((group_stack[-1] == "(" and char == ")") or
                                (group_stack[-1] == "{" and char == "}") or
                                (group_stack[-1] == "[" and char == "]")):
                group_stack.pop()
            current_value.append(char)
        elif char == "=" and not in_quotes and not group_stack:
            if current_key is None:
                current_key = "".join(current_value).strip()
                current_value = []
            else:
                raise ValueError("Unexpected '=' in value")
        elif char == "&" and not in_quotes and not group_stack:
            if current_key:
                result["params"][current_key] = parse_value("".join(current_value).strip())
                current_key = None
                current_value = []
            else:
                raise ValueError("Unexpected '&' without key")
        else:
            current_value.append(char)

        i += 1

    # Final key-value pair
    if current_key:
        result["params"][current_key] = parse_value("".join(current_value).strip())

    return result
```