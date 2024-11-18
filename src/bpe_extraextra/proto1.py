#!/usr/bin/python

import tkinter as tk
import re
import sys
import toml
from rich import print
from tkinter import filedialog
import os
import shutil
from urllib.parse import parse_qs, urlparse, unquote, ParseResult
from dataclasses import dataclass
from bpe_extraextra.utils import LoggingClass

# ?   add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar
# ?   upg://path/to/file:old-file=oldfilename
# ?   upg://path/to/file:old-regex=oldregex
# ?   del://filepath
# ?   toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false
# ?   sed://config/createcobblestone-common.toml?/match/replace/opt
#
# shutil.rmtree(path, ignore_errors=False, onerror=None)

# TODO: switch to pathlib
# TODO: switch to using requests instead of urllib
# TODO: run a test with 2 updates, then combine with the class in apply_update_1.py (and revise the code there)

class BaseRequest:
    _strFakeDomain = "ignore.lnk"

    def __init__(self, requeststr: str):
        self._requeststr = requeststr
        self._parse_request(requeststr)

    def _split_params(self, query: str, keep_blank_values: bool = True) -> dict[str, str]:
        params = {}

        if query is not None and query.strip() != "":
            keyname = ""
            # keyvalue = "" # Variable not used, as buffer is dumped into params
            inKeyname = True
            inQuote = False
            buffer = ""

            for i in range(len(query)):
                if inKeyname:
                    if query[i] == '=':
                        keyname = buffer
                        buffer = ""
                        inKeyname = False
                    else:
                        buffer = buffer + query[i]
                else:
                    if inQuote:
                        if query[i] == '"':
                            inQuote = False
                        buffer = buffer + query[i]
                    else:                            
                        if query[i] == '&':
                            if len(buffer) > 0 or keep_blank_values:
                                params[keyname] = buffer
                            # TODO: emit a warning about blank values
                            keyname = ""
                            buffer = ""
                            inKeyname = True
                        elif query[i] == '=':
                            # TODO: emit a warning about '=' in a keyvalue if not in quote
                            buffer = buffer + query[i]
                        elif query[i] == '"':
                            inQuote = True
                            buffer = buffer + query[i]
                # TODO: Finish this area, last work
                # INFO: This is the area I was working on

        return params
    
    def _parse_request(self, requeststr: str):
        # assign local copy of request
        self._request = requeststr
        _request = requeststr.replace("%%", "%25")

        # Modify request to be a valid URL
        # TODO: Make 'ignore.lnk' a constant
        # TODO: Perform additional escaping and validation
        if _request.split('://')[0].lower() not in ["http", "https", "ftp"]:
            _result = urlparse(_request.replace("://", f"://{self._strFakeDomain}/"))
            self._path = _result.path.removeprefix("/")
        else:
            _result = urlparse(_request)
            self._path = _result.hostname
            if _result.port is not None and len(_result.port) > 0:
                self._path = f"{self._path}:{_result.port}"
            self._path = self._path + _result.path

        # set values to self
        self._protocol = _result.scheme
        self._query = _result.query

        if _result.fragment is not None and len(_result.fragment) > 0:
            to_parse = f"{_result.query}#{_result.fragment}"
        else:
            to_parse = _result.query
        
        if len(_result.params) < 1:
            # escape problem characters: +
            to_parse = to_parse.replace("+", "%2B")
            self._params = parse_qs(to_parse, keep_blank_values=True)
        else:
            self._params = _result.params

        self._fragment = _result.fragment
            
    def __repr__(self):
            return f"BaseRequest(request='{self._request}', protocol='{self._protocol}', path='{self._path}', query='{self._query}', params='{self._params}', fragment='{self._fragment}')"

    # Properties
    @property
    def Request(self):
        return self._request

    @property
    def Protocol(self):
        return self._protocol

    @property
    def Path(self):
        return self._path

    @property
    def Query(self):
        return self._query

    @property
    def Params(self):
        return self._params

    @property
    def Fragment(self):
        return self._fragment

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
        print(f"Request '{requeststr}' not recognized; wrong format. No '://'. Error: {e}")
        return None
    except TypeError as e:
        # warn.
        print(f"Request '{requeststr}' not recognized. Unable to 'split' on '://'. Is [request] text? Error: {e}")
        return None
    except Exception as e:
        # warn.
        print(f"Request '{requeststr}' not recognized. Unknown fault. Error: {e}")

    return result

def analyze_request(requeststr: str):

    re_request = re.compile(r'^(?:(?P<protocol>[^:]+)://)?(?P<path>[^\?]+)(?:\?(?P<query>.*))?')
    trimmed = requeststr

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
    
# TODO: Modify each of protocol handlers to take a request object

def do_toml_request(requeststr: str, toml_obj=None):

    trimmed = requeststr.removeprefix("toml://")
    
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
    results = urlparse(requeststr)

    print(f"filename: {filename}, section: {section}, key: {rkey}, value: {rvalue}")
    print(f"results: {results}")

    modify_toml(mytoml_obj,section, rkey, rvalue)

    if DBG_SIMULATE:
        print("dumping", os.path.join(destination, filename))
    else:
        toml_obj.dump(os.path.join(destination, filename))

def do_file_copy(requeststr: str):
    trimmed = requeststr
    trimmed = trimmed.removeprefix("add://")
    filename = trimmed
    if not os.path.exists(os.path.join(cwd, filename)):
        raise FileNotFoundError(f"File not found: {filename}")

    if DBG_SIMULATE:
        print("shutil.copy", os.path.join(cwd, filename), os.path.join(destination, filename))
    else:
        shutil.copy(os.path.join(cwd, filename), os.path.join(destination, filename))

def do_file_upgrade(requeststr: str):
    """Handle a file upgrade request.
    Currently only supports declaring old-file or old-regex.
    
    :param request: The request to route
    :type request: str
    """

    # Trim off the request prefix, then split into filename and parts
    trimmed = requeststr
    trimmed = trimmed.removeprefix("upg://")
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

def route_request(therequest: BaseRequest):

    if not isinstance(therequest, BaseRequest):
        raise ValueError("Therequest is not a BaseRequest object")
    
    if therequest._protocol not in ["add", "upg", "del", "toml", "sed", "msg"]:
        raise NotImplementedError(f"Protocol {therequest._protocol} not recognized")
    
    # TODO: implement handling of requests

    # if therequest.protocol == "add":
    #     do_file_copy(therequest.path)
    # elif therequest.protocol == "upg":
    #     do_file_upgrade(therequest.path)
    # elif therequest.protocol == "del":
    #     do_file_delete(therequest.path)
    # elif therequest.protocol == "toml":
    #     do_toml_request(therequest.path)
    # elif therequest.protocol == "sed":
    #     do_sed(therequest.path)
    # elif therequest.protocol == "msg":
    #     do_msg(therequest.path)
    
    pass

def do_request(requeststr: str):
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
    req_type, req_content = requeststr.split("://",1)

    if req_type == "toml":
        do_toml_request(req_content)

    elif req_type == "add":
        do_file_copy(req_content)

    elif req_type == "upg":
        do_file_upgrade(req_content)
    # TODO: handle del request
    # TODO: handle sed request
    # TODO: handle msg request

    else:
        # Raise exception about not implemented yet
        raise ValueError(f"Request type [{req_type}] not implemented")


if __name__ == "__main__":
    myLog = LoggingClass("extraextra", "extraextra.log", 'DEBUG', 'DEBUG')
    DBG_SIMULATE = True

    test_req = [
        "add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar",
        "upg://path/to/file?old-file=oldfilename",
        "upg://path/to/file?old-regex=oldregex",
        "del://filepath",
        "toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false",
        "sed://config/createcobblestone-common.toml?s=/match/replace/opt",
        "toml://config/quark-common.toml?[tweaks.compasses_work_everywhere]:Enable Clock Nerf=false",
        "toml://config/quark-common.toml?[[tweaks.compasses_work_everywhere]]:Enable Clock Nerf=false",
        "msg://plain?title=title&message=Text to show the user? Do #2, #3, and #4. Then ask a (6/3) + 3 = 5 question again."
    ]

    for req in test_req:
        result = BaseRequest(req)

        if DBG_SIMULATE:
            print(f"""
request: {result.Request}
\tprotocol: {result.Protocol}
\tpath: {result.Path}
\tquery: {result.Query}
\tparams: {result.Params}
\tfragment: {result.Fragment}"""
)

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
    #request = r"toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false"

    #do_toml_request(request)

    old_simulate = DBG_SIMULATE
    DBG_SIMULATE = True
    test_requests = [
        "add://mods/createcobblestone-1.3.2+forge-1.20.1-38.jar",
        "add://config/createcobblestone-common.toml",
        "toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false"
    ]

    for requeststr in test_requests:
        do_request(requeststr)

    DBG_SIMULATE = old_simulate