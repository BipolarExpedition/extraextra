import os.path
import os
import shutil
import re

UPDATE_NAME="20240908-1409"


# NOTES
#
#  TOML notation:     section.subsection:key=value
#  INI notation:      section:key=value    Preprocess to remove comments ; #

# header:
#   # ... (similar to TOML/INI)

# folder-mappings:
#   source: config  # Source directory
#   destination: config  # Destination directory (can be same)
#   groups:
#     - name: Ignore (Examples)  # More descriptive group name
#       type: Ignore  # Predefined type for files to exclude
#       # ... (similar to TOML/INI)

#     - name: Update JSON Files  # More descriptive group name
#       type: UpdateJSON  # Predefined type for JSON updates
#       files:
#         - name: "example.json"
#           modifications:
#             - path: $.config.general  # JSON path to modify
#             - key: keyname
#             - operation: replace  # Operation type (e.g., replace, append, delete)
#               value: new value   # Only valid for replace operation


class GLOBALS:
    """Class for global variables, and shared static methods"""

    BASE_DIR=r"/home/doc/src/my/BNU"
    ACTIVE=f"{BASE_DIR}/linked/active"
    PUBLISHED=f"{BASE_DIR}/linked/stuff"
    TESTING=f"{BASE_DIR}/linked/testing"
    ORIGINAL=f"{BASE_DIR}/linked/BipolarNerdsUnleashed.zip"
    UPDATES=f"{BASE_DIR}/linked/BNU-projects"
    WEBROOT=r"/usr/share/nginx/html"

class UpdateInstrucions:
    """Class for the update instructions.

    Args:
        location: location of the update instructions file 
        files_to_add: list of files to add
        files_to_update: list of files to update
        files_to_remove: list of files to remove
        configs_to_update: list of configs to update
        configs_to_remove: list of configs to remove
        configs_to_add: list of configs to add
    """

    def __init__(self, location=None, file_base=None,files_to_add=None, files_to_update=None, files_to_remove=None,
                 configs_to_update=None, configs_to_remove=None, configs_to_add=None):
        self.location = location
        self.files_to_add = files_to_add
        self.files_to_update = files_to_update
        self.files_to_remove = files_to_remove
        self.configs_to_update = configs_to_update
        self.configs_to_remove = configs_to_remove
        self.configs_to_add = configs_to_add
        self._update_project = "UNKNOWN"
        self._update_version = "UNKNOWN"
        self._target_version = "UNKNOWN"

        # TODO: read in the update instructions at `self.location`. For now, use values from parameters

        if file_base is None:
            if location is None:
                raise ValueError("No location provided for where update files are stored")
            else:
                self._file_base = os.path.dirname(os.path.abspath(location)) # Assume it's in the same directory


    @property
    def ProjectName(self):
        return self._update_project

    @property
    def TargetVersion(self):
        return self._target_version

    @property
    def UpdateVersion(self):
        return self._update_version

    @property
    def FileBase(self):
        if os.path.exists(os.path.abspath(self.location)):
            return os.path.dirname(os.path.abspath(self.location))
        return None

    def getMatchingFileNames(self, fileobject):
        """Get all filenames in a directory that match a pattern"""

        if "path" in fileobject:
            basedir = fileobject["path"]
        else:
            basedir = os.path.dirname(os.path.abspath(fileobject["name"]))

        filepattern = fileobject["old-regex"]

        return [f for f in os.listdir(basedir) if re.match(filepattern, f)]

    def removeOldFiles(self, fileobject):
        # if old-regex is provided, use it to remove old files. Otherwise, use old-file
        if ("old-file" in fileobject) or ("old-regex" in fileobject):
            if "old-regex" in fileobject:
                old_files = self.getMatchingFileNames(fileobject)

                # Delete old files
                for oldfile in old_files:
                    src = os.path.join(self.FileBase, oldfile)
                    os.unlink(src)
            elif "old-file" in fileobject:
                oldfile = fileobject["old-file"]
                src = os.path.join(self.FileBase, oldfile)
                os.unlink(src)

    def apply_update(self, dest_dir: str):
        """Apply the update instructions to the destination directory"""

        # Confirm the file_base (where update files come from) and dest_dir (base of where they go) actually exist
        if self.FileBase is None:
            raise ValueError(f"FileBase not found for {self.location}")
        if not os.path.exists(os.path.abspath(dest_dir)):
            raise ValueError(f"Destination directory not found: {dest_dir}")

        # Copy the files in the files_to_add list and configs in the configs_to_add list
        for mylist in [self.files_to_add, self.configs_to_add]:
            if mylist is not None:
                for ufile in mylist:
                    if isinstance(ufile, dict):
                    # Copy to destination, overwriting if needed
                        if ("path" in ufile):
                            # Entry has extended information
                            # TODO: Fully handle extra functions allowed by extended data

                            filename = os.path.join(ufile["path"], ufile["name"])
                        else:
                            filename = ufile["name"]

                    elif isinstance(ufile, str):
                        filename = ufile

                    
                    src = os.path.join(self.FileBase, filename)
                    dest = os.path.join(dest_dir, filename)
                    if not os.path.exists(src):
                        raise FileNotFoundError(f"Source file for update, {filename}, not found!")
                    
                    if ("old-file" in ufile) or ("old-regex" in ufile):
                        self.removeOldFiles(ufile)

                    shutil.copy2(src, dest)

                    # TODO: Add proper logging
                    print(f"Added {filename} to {dest_dir}")
        
        # Now apply the files_to_update
        if self.files_to_update is not None:
            for ufile in self.files_to_update:
                # Determine type of file modification, by file type
                filename=ufile["name"]


                # type://(folder/subfolder)?(key=value)
                try:
                    if "quick" in ufile:
                        #m = re.match(r"(^[^\:\/]+):\/\/([^\?]+)\?(.*?)$")
                        m = re.match(r"(^[^\:\/]+):\/\/([^\?]*?)$", ufile["quick"].strip())
                        if m:
                            # The type of update
                            updatetype = m.group(1)
                            updatecmd = m.group(2).strip()

                            # If its a config file, call the appropriate function
                            if updatetype.lower() in ["json", "yaml", "toml", "ini", "cfg"]:
                                m = re.match(r"([^\?]+)\?(.*)", updatecmd)
                                if m:
                                    updatepath=m.group(1)
                                    updatevalue=m.group(2)

                                    # Call the appropriate function
                                    if updatetype.lower() == "json":
                                        self.modify_json_file(updatepath, updatevalue)
                                    elif updatetype.lower() == "yaml":
                                        self.modify_yaml_file(updatepath, updatevalue)
                                    elif updatetype.lower() == "toml":
                                        self.modify_toml_file(updatepath, updatevalue)
                                    elif updatetype.lower() == "ini":
                                        self.modify_ini_file(updatepath, updatevalue)
                                    elif updatetype.lower() == "cfg":
                                        self.modify_cfg_file(updatepath, updatevalue)
                            elif updatetype.lower() == "sed":
                                print("Sed not implemented yet")
                                raise NotImplementedError
                            elif updatetype.lower() == "msg":
                                self.doMsg(updatepath, updatevalue)
                except Exception as e:
                    print(f"Expception processing {ufile}")
                    raise e
                
    def doMsg(self, updatepath, updatevalue):
        # { "quick": "msg://plain/title/Text to show the user. \n\nIt should describe what they need to do to manually update." }
        # msg://plain/title/?The very long text body for the message        "msg", "plain/title/", "The very long text body for the message"

        parts = updatepath.split("/")
        if len(parts) > 1:
            title = parts[1]
        else:
            title = "Update"

        print(f"======{title}======")
        print(updatevalue)

        print("===========")
        print("")


    def modify_json_file(self, ufile):
        # path/file.ext
        # key=value pairs separated by '&'
        pass

    def modify_yaml_file(self, ufile):
        pass

    def modify_toml_file(self, ufile):
        pass

    def modify_ini_file(self, ufile):
        pass

    def modify_cfg_file(self, ufile):
        pass


def test_apply_update(src_dir: str, dest_dir: str):
    UPDATE_SRC_FILES_DIR=src_dir
    DEST_DIR=dest_dir

    files_to_update = [

    ]

    files_to_add = [
        {
            "name": "createcobblestone",
            "path": "mods",
            "reason": "cobblestone generation that is gentler on the server",
            "optional": False,
            "new-file": "createcobblestone-1.3.2+forge-1.20.1-38.jar",
            "old-file": "createcobblestone-1.3.1+forge-1.20.1-38.jar",
            "old-regex": "createcobblestone-[\d+\.]+\+forge-[\d+\.]+-\d+.jar",
            "new-md5": "2f9c5b9e0f5c0f5c0f5c0f5c0f5c0f5",
            "new-size": 5551212,
            "bundled": True,
            "bundled-path": "mods",
            "direct-download": True,
            "personal-hosting": False,
            "project-page": "https://github.com/BipolarNerdsUnleashed/BipolarNerdsUnleashed/releases/tag/1.3.2",
            "project-page2": "https://github.com/BipolarNerdsUnleashed/BipolarNerdsUnleashed",
            "url": "https://github.com/BipolarNerdsUnleashed/BipolarNerdsUnleashed/releases/download/1.3.2/createcobblestone-1.3.2+forge-1.20.1-38.jar",
            "download-page": "https://github.com/BipolarNerdsUnleashed/BipolarNerdsUnleashed/releases/tag/1.3.2"
        }
    ]

    files_to_add = [
        "mods/createcobblestone-1.3.2+forge-1.20.1-38.jar"
    ]

    configs_to_update = [
        {
            "name": "createcobblestone-common",
            "path": "config",
            "reason": "cobblestone generation that is gentler on the server",
            "optional": False,
            "backup": False,
            "duplicate-ok": False,
            "file-name": "config/createcobblestone-common.toml",
            "section": "[general]/secrect-variable",
            "new-value": "secret",

            "old-file": "createcobblestone-common-1.3.1+forge-1.20.1-38.toml",
            "old-regex": "createcobblestone-common-[\d+\.]+\+forge-[\d+\.]+-\d+.toml",
            "new-md5": "2f9c5b9e0f5c0f5c0f5c0f5c0f5c0f5",
            "new-size": 5551212,
            "bundled": True,
            "bundled-path": "config",
            "direct-download": True,
            "personal-hosting": False,
            "project-page": "https://github.com/BipolarNerdsUnleashed/BipolarNerdsUnleashed/releases/tag/1.3.2",
        },
        { "quick": "config/createcobblestone-common.toml/[general]/secret-variable=secret" },
        { "quick": "config/createcobblestone-common.toml/[general]/secret-array+=appended_value" },
        { "quick": "sed://config/createcobblestone-common.toml?/match/replace/opt" },
        { "quick": "msg://plain/title/Text to show the user. \n\nIt should describe what they need to do to manually update." }
    ]

    configs_to_update = [
        { 
            "quick": "config/quark-common.toml/[tweaks][tweaks.compasses_work_everywhere]/\"Enable Clock Nerf\"=false",
            "optional": True,
            "reason": "Allows animated clock in hourglass mod to work" 
        },
        { "quick": "defaultconfigs/hourglass-server.toml/[time][time.effects]/randomTickEffect=NEVER" },
        { "quick": "defaultconfigs/hourglass-server.toml/[time][time.effects]/blockEntityEffect=NEVER" },
        {
            "quick": "#BASE#serverconfig/hourglass-server.toml/[time][time.effects]/randomTickEffect=NEVER",
            "server-only": True
        },
        {
            "quick": "#BASE#serverconfig/hourglass-server.toml/[time][time.effects]/blockEntityEffect=NEVER",
            "server-only": True
        },

    ]

    configs_to_add = [
        "config/createcobblestone-common.toml"
    ]
    myTestInstructions = UpdateInstrucions(None, 
            files_to_add=files_to_add, files_to_update=files_to_update,
            configs_to_update=configs_to_update, configs_to_add=configs_to_add)
    
    myTestInstructions.apply_update()



def main():
    test_apply_update(f"{GLOBALS.UPDATES}/20240908-1409", GLOBALS.TESTING)

if __name__ == "__main__":
    main()