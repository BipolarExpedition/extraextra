import re
import sys
import toml
import os
import shutil
#from urllib.parse import parse_qs, urlparse, unquote, ParseResult
#from dataclasses import dataclass
from bpe_extraextra.utils import LoggingClass as LOG

class Instructions:
    def __init__(self):
        self._header = None
        self._tasks = None
        self._location = None   # Directory where the instructions are stored

        # TODO: Instructions class: Load values from yaml node object
class InstructionsHeader:
    def __init__(self):
        self._content = None
        self._zcontent = 'Update Instructions'
        self._content_format = None
        self._zcontent_format = 'bpe-update-instruction-1.0'
        self._category = None      # Category of what we are targeting. ie: Minecraft Modpack
        self._target = None        # Logical name of what this update is for
        self._author = None
        self._link = None
        self._description = None

        # TODO: InstructionsHeader class: Load values from yaml node object

class InstructionsTask:
    def __init__(self):
        self._title = None
        self._description = None
        self._optional = False
        self._depends_on = None
        self._requests = None

        # TODO: InstructionsTask class: Load values from yaml node object

class RequestFileObject:
    def __init__(self):
        self._name = None
        self._old_name = None
        self._old_regex = None
        self._replace = True
        self._must_exist = False
        self._friendly_name = None
        self._relPathSource = None
        self._relPathTarget = None

        # TODO: RequestFileObject class: Load values from yaml node object
class BaseRequest:
    # TODO: BaseRequest class: Load values from yaml node object and string
    def __init__(self, requeststr: str):
        self._protocol = None
        self._path = None
        self._files = None      # Move this to AddRequest and DeleteRequest

# TODO: BaseRequest class: Implement extentions for loading values in child classes

class MessageRequest(BaseRequest):
    def __init__(self, requeststr: str):
        super().__init__(requeststr)

class AddRequest(BaseRequest):
    def __init__(self, requeststr: str):
        super().__init__(requeststr)

class DeleteRequest(BaseRequest):
    def __init__(self, requeststr: str):
        super().__init__(requeststr)

class RegexRequest(BaseRequest):
    def __init__(self, requeststr: str):
        super().__init__(requeststr)
        self


if __name__ == "__main__":
    mylog = LOG("proto2", logFile="proto2.log", consoleLevel="DEBUG", fileLevel="DEBUG")
    LOG.info("Starting proto2 test program...")

