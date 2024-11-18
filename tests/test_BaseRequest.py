import pytest
from bpe_extraextra.proto1 import BaseRequest

@pytest.mark.parametrize(
    "requeststr, expected_protocol, expected_path, expected_query, expected_params, expected_fragment",
    [
        # Happy path tests
        ("http://example.com/path?query=1#frag", "http", "example.com/path", "query=1", {"query": ["1#frag"]}, "frag"),
        ("https://example.com/path/to/resource?query=1&query=2", "https", "example.com/path/to/resource", "query=1&query=2", {"query": ["1", "2"]}, ""),
        ("ftp://example.com/resource", "ftp", "example.com/resource", "", {}, ""),

        # Edge cases
        ("https://www.google.com/search?q=comparison+of+docstring+formats+google+sphinx+numpy&oq=comparison+of+docstring+formats+google+sphinx+numpy",
            "https", "www.google.com/search", 
            "q=comparison+of+docstring+formats+google+sphinx+numpy&oq=comparison+of+docstring+formats+google+sphinx+numpy", 
            {"q": ["comparison+of+docstring+formats+google+sphinx+numpy"], "oq": ["comparison+of+docstring+formats+google+sphinx+numpy"]},
            ""),
        ("http://example.com", "http", "example.com", "", {}, ""),
        ("http://example.com/path?query=", "http", "example.com/path", "query=", {"query": [""]}, ""),
        ("http://example.com/path#fragment", "http", "example.com/path", "", {'#fragment': ['']}, "fragment"),
        
        # Error cases
        ("invalid://example.com", "invalid", "example.com", "", {}, ""),
        ("http://example.com/%%path", "http", "example.com/%25path", "", {}, ""),

        # Actual example requests
        ("add://mods/createcobblestone-1.3.1+forge-1.20.1-38.jar", "add", "mods/createcobblestone-1.3.1+forge-1.20.1-38.jar", "", {}, ""),
        ("upg://path/to/file?old-file=oldfilename", "upg", "path/to/file", "old-file=oldfilename", {"old-file": ["oldfilename"]}, ""),
        ("upg://path/to/file?old-regex=oldregex", "upg", "path/to/file", "old-regex=oldregex", {"old-regex": ["oldregex"]}, ""),
        ("del://filepath", "del", "filepath", "", {}, ""),
        ("toml://config/quark-common.toml?tweaks.compasses_work_everywhere:Enable Clock Nerf=false", "toml", "config/quark-common.toml", "tweaks.compasses_work_everywhere:Enable Clock Nerf=false", {"tweaks.compasses_work_everywhere:Enable Clock Nerf": ["false"]}, ""),
        ("sed://config/createcobblestone-common.toml?s=/match/replace/opt", "sed", "config/createcobblestone-common.toml", "s=/match/replace/opt", {"s": ["/match/replace/opt"]}, ""),
        ("toml://config/quark-common.toml?[tweaks.compasses_work_everywhere]:Enable Clock Nerf=false", "toml", 
            "config/quark-common.toml", "[tweaks.compasses_work_everywhere]:Enable Clock Nerf=false",
            {"[tweaks.compasses_work_everywhere]:Enable Clock Nerf": ["false"]}, ""),
        ("toml://config/quark-common.toml?[[tweaks.compasses_work_everywhere]]:Enable Clock Nerf=false", "toml", 
            "config/quark-common.toml", "[[tweaks.compasses_work_everywhere]]:Enable Clock Nerf=false", 
            {"[[tweaks.compasses_work_everywhere]]:Enable Clock Nerf": ["false"]}, ""),
        ("msg://plain?title=title&message=Text to show the user? Do #2, #3, and #4. Then ask a (6/3) + 3 = 5 question again.", 
            "msg", "plain", 
            "title=title&message=Text to show the user? Do ", 
            {"title": ["title"], "message": ["Text to show the user? Do #2, #3, and #4. Then ask a (6/3) + 3 = 5 question again."]}, "2, #3, and #4. Then ask a (6/3) + 3 = 5 question again.")
    ],
    ids=[
        "http_with_path_query_fragment",
        "https_with_multiple_query_params",
        "ftp_with_resource",
        "actual_url",
        "http_without_path",
        "http_with_empty_query_value",
        "http_with_fragment_only",
        "invalid_protocol",
        "http_with_percent_encoding",
        "add_request",
        "upg_request",
        "upg_request2",
        "del_request",
        "toml_request",
        "sed_request",
        "toml_request2",
        "toml_request3",
        "msg_request"
    ]
)
def test_base_request_parsing(requeststr, expected_protocol, expected_path, expected_query, expected_params, expected_fragment):
    # Act
    base_request = BaseRequest(requeststr)

    # Assert
    assert base_request._protocol == expected_protocol
    assert base_request._path == expected_path
    assert base_request._query == expected_query
    assert base_request._params == expected_params
    assert base_request._fragment == expected_fragment
