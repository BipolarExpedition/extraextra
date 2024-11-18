#!/usr/bin/python

import tkinter as tk
import re
import sys
import toml
from tkinter import filedialog
import os
import shutil
from urllib.parse import parse_qs, urlparse, unquote

# ?   add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar
# ?   upg://path/to/file:old-file=oldfilename
# ?   upg://path/to/file:old-regex=oldregex
# ?   del://filepath
# ?   toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false
# ?   sed://config/createcobblestone-common.toml?/match/replace/opt
#
# shutil.rmtree(path, ignore_errors=False, onerror=None)

# TODO: switch to pathlib
# TODO: use urllib.parse.urlparse to parse and verify requests
# TODO: run a test with 2 updates, then combine with the class in apply_update_1.py (and revise the code there)

add_files =[
    "mods/createcobblestone-1.3.1+forge-1.20.1-38.jar",
    "config/createcobblestone.toml"
]

# base directory of source paths
self_base_source = ""

# base directory of destination paths
self_base_dest = ""

def modify_toml(toml_obj, section: str, key: str, value: str):
    steps = section.split(".")

    node = toml_obj

    for step in steps:
        if step not in node:
            raise KeyError(f"Key '{step}' not found in section '{section}'")
        else:
            node = node[step]

    if key in node:  
        key = node[key]
        if isinstance(key, bool):
            node[key] = bool(value)
        elif isinstance(key, int):
            node[key] = int(value)
        elif isinstance(key, float):
            node[key] = float(value)
        elif isinstance(key, str):
            node[key] = str(value)
    else:
        if value.lower() == "true" or value.lower() == "false":
            node[key] = bool(value)
        else:
            try:
                node[key] = int(value)
            except ValueError:
                try:
                    node[key] = float(value)
                except ValueError:
                    node[key] = str(value)

def safe_split(fullString: str, delimiter: str = "\n", maxsplit: int = -1, trim: bool = False, comment: str = None):
    if trim:
        fullString = fullString.strip()
    
    if comment is not None and isinstance(comment,str):
        theComment = f"ActionComment: {comment} "
    else:
        theComment = ""

    try:
        result = fullString.split(delimiter, maxsplit)
    except AttributeError as e:
        # warn.
        print(f"Exception splitting string on '{delimiter}'. {theComment}Error: {e}")
        return None
    except ValueError as e:
        # warn.
        print(f"Request '{request}' not recognized; wrong format. No '://'. Error: {e}")
        return None
    except TypeError as e:
        # warn.
        print(f"Request '{request}' not recognized. Unable to 'split' on '://'. Is [request] text? Error: {e}")
        return None
    except Exception as e:
        # warn.
        print(f"Request '{request}' not recognized. Unknown fault. Error: {e}")

    return result

def analyze_request(request: str):

    re_request = re.compile(r'^(?:(?P<protocol>[^:]+)://)?(?P<path>[^\?]+)(?:\?(?P<query>.*))?')
    trimmed = request

    result = safe_split(trimmed, "://", 1, trim=True)
    
    # if result is not None, set protocol=result[0] and further process result[1]
    if result is not None and len(result) > 1:
        protocol = result[0]
        result = safe_split(result[1], "?", 1)

        if result is not None:
            cmdpath = result[0]
            parts = dict()
            if len(result) > 1:
                parts = safe_split(result[1], "&")
    

    



def do_toml_request(request: str, toml_obj=None):

    trimmed = request
    if trimmed.startswith("toml://"):
        trimmed = trimmed[7:]
    
    filename, parts = trimmed.split("?",1)

    if not os.path.exists(os.path.join(destination, filename)):
        raise ValueError(f"File not found: {filename}")
    
    if toml_obj is None:
        # raise ValueError("No TOML object provided. Loading not implemented yet.")
        with open(os.path.join(destination, filename), "r") as f:
            toml_obj = toml.load(f)

    mytoml_obj = toml_obj

    section, kv = parts.split(":",1)
    rkey, rvalue = kv.split("=",1)
    results = urlparse(request)

    print(f"filename: {filename}, section: {section}, key: {rkey}, value: {rvalue}")
    print(f"results: {results}")

    modify_toml(mytoml_obj,section, rkey, rvalue)

    if DBG_SIMULATE:
        print("dumping", os.path.join(destination, filename))
    else:
        toml_obj.dump(os.path.join(destination, filename))

def do_file_copy(request: str):
    trimmed = request
    if trimmed.startswith("add://"):
        trimmed = trimmed[6:]
    
    filename = trimmed
    if not os.path.exists(os.path.join(cwd, filename)):
        raise FileNotFoundError(f"File not found: {filename}")
    
    if DBG_SIMULATE:
        print("shutil.copy", os.path.join(cwd, filename), os.path.join(destination, filename))
    else:
        shutil.copy(os.path.join(cwd, filename), os.path.join(destination, filename))

def do_file_upgrade(request: str):
    """Handle a file upgrade request.
    Currently only supports declaring old-file or old-regex.
    
    :param request: The request to route
    :type request: str
    """

    # Trim off the request prefix, then split into filename and parts
    trimmed = request
    if trimmed.startswith("upg://"):
        trimmed = trimmed[6:]
    filename = trimmed
    filename, parts = trimmed.split(":",1)

    # Confirm the new file actually exists with the install files
    if not os.path.exists(os.path.join(cwd, filename)):
        raise FileNotFoundError(f"Source file not found: {filename}")

    # Determine if old-file or old-regex is used, and act accordingly
    if parts.lower().startswith("old-file"):
        old_filename = parts.split("=",1)[1]
        if os.path.exists(os.path.join(destination, old_filename)):
            if DBG_SIMULATE:
                print("os.unlink", os.path.join(destination, old_filename))
            else:
                os.unlink(os.path.join(destination, old_filename))
        else:
            # TODO: Possibly make this an error, via command line option
            #raise FileNotFoundError(f"File not found: {old_filename}")
            print(f"Warning: Old version of the file, {old_filename}, not found. Skipping.")
    elif parts.lower().startswith("old-regex"):
        raise NotImplementedError("Old regex not implemented. Skipping.")
         
    # Copy the file

    if DBG_SIMULATE:
        print("shutil.copy", os.path.join(cwd, filename), os.path.join(destination, filename))
    else:
        shutil.copy(os.path.join(cwd, filename), os.path.join(destination, filename))


def do_request(request: str):
    """
    Read a request and route it if implemented.
    
    Supported requests:
    -   add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar
    -   upg://path/to/file?old-file=oldfilename
    -   upg://path/to/file?old-regex=oldregex
    -   del://filepath
    -   toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false
    -   sed://config/createcobblestone-common.toml?s=/match/replace/opt
    -   msg://plain?title=title&message=Text to show the user.

    :param request: The request to route
    :type request: str
    """
    req_type, req_content = request.split("://",1)

    if req_type == "toml":
        do_toml_request(req_content)

    elif req_type == "add":
        do_file_copy(req_content)

    elif req_type == "upg":
        do_file_upgrade(req_content)

    else:
        # Raise exception about not implemented yet
        raise ValueError(f"Request type [{req_type}] not implemented")

if __name__ == "__main__":
    DBG_SIMULATE = True


    test_req = [
        "add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar",
        "upg://path/to/file?old-file=oldfilename",
        "upg://path/to/file?old-regex=oldregex",
        "del://filepath",
        "toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false",
        "sed://config/createcobblestone-common.toml?s=/match/replace/opt",
        "msg://plain?title=title&message=Text to show the user."
    ]

    for req in test_req:
        upr = req
        upr = upr.replace("://", "://127.0.0.1/")
        upr = upr.replace("%%", "%25")
        result = urlparse(upr)
        params = parse_qs(result.query, keep_blank_values=True)    

        print(f"request: {upr}\n\tprotocol: {result.scheme}\tpath: {result.path}\tquery: {result.query}")
        for p in params.keys():
            print(f"\t\t{p}: {params[p]}")


    sys.exit(0)

    # change to source folder
    if DBG_SIMULATE:
        mysrc = r"/home/doc/Documents/MCExports/BNU/20240908-1409"
        os.chdir(mysrc)
        cwd = mysrc
    else:
        # get current working directory
        cwd = os.getcwd()

    assumed = r"/mnt/rust1/vdirs/doc/src/my/BNU/linked/testing/minecraft"


    # Use tkinter to ask for destination folder of minecraft folder
    root = tk.Tk()
    root.withdraw()
    destination = filedialog.askdirectory(parent=root, initialdir=assumed, title='Please select destination folder')
    root.destroy()

    if not os.path.exists(destination):
        raise FileNotFoundError(f"Destination directory not found: {destination}")
    

    # Modify a toml file
    request = r"toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false"

    #do_toml_request(request)

    old_simulate = DBG_SIMULATE
    DBG_SIMULATE = True
    test_requests = [
        "add://mods/createcobblestone-1.3.2+forge-1.20.1-38.jar",
        "add://config/createcobblestone-common.toml",
        "toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false"
    ]

    for request in test_requests:
        do_request(request)

    DBG_SIMULATE = old_simulate