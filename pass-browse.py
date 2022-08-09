#!/usr/bin/env python3

# First arg should be the name of the password-store entry.
# Also need to pipe in the output of `pass show $1`
# This script will return the Alfred 5 XML for an interactive 
# list of fields to choose from, within the password.

from typing import *

import re
import os
import sys
import subprocess
import functools


QUERY = sys.argv[1] # Must have at least one arg
HOME = os.environ['HOME']
PASS_DIR = os.environ.get('PASSWORD_STORE_DIR', os.path.join(HOME, '.password-store/'))


def get_fields(pass_show_output : str) -> List[str]:
    #pass_show_output = get_pass_show(psp)
    nums_labels_values : List[Tuple[int, str, str]] 
    nums_labels_values = [(0, "Password", pass_show_output.splitlines()[0])]
    nums_labels_values.extend([ 
            (n, *m.groups()) 
            for n,m in map(
                lambda x : (x[0], re.fullmatch("^ *([^:]+): +( ?[^ ]+) *$", x[1])) , 
                enumerate(pass_show_output.splitlines()) ) 
            if m is not None ])
    return nums_labels_values # list of fields. Each is a 3-tuple. (linenum, field_label, field_value)

# Unused. Password will be treated like any other entry. With a fixed label.
if False:
    def password_xml() -> str:
        n,l,v = 0, "Password", 
        return f"""
        <item arg="autotype {n+1:d} {QUERY:s}" valid="YES" autocomplete="{QUERY:s}: {l:s}">
            <title>Secret (first line)</title>
            <subtitle>Copy &amp; autotype. Hold ⌥ to reveal. Hold ⌘ to copy.</subtitle>
            <mod key="option" subtitle="{v:s}"/>
            <mod key="command" subtitle="Copy to clipboard." valid="YES" arg="copy {n+1:d} {QUERY:s}"/>
        </item>"""

# Escape XML strings. Taken from https://stackoverflow.com/a/65450788
table = str.maketrans({
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;",
})
def xmlesc(txt):
    return txt.translate(table)

def field_to_xml(field : Tuple[int,str,str]) -> str:
    n,l,v = field

    # Icon
    # Python 3.10+
    #match l.lower():
    #    case "user" | "username" | "login" :
    #        icon_xml = '<icon type="filetype">public.vCard</icon>'
    #    case "password" :
    #        icon_xml = ''
    if l.lower() in ("user", "username", "login"):
            #icon_xml = '<icon type="filetype">public.vCard</icon>'
            icon_xml = '<icon>UserIcon.icns</icon>'
    elif l.lower() in ("password",):
            icon_xml = ''
    elif l.lower() in ("email", "e-mail"):
            #icon_xml = '<icon>InternetLocation.icns</icon>'
            icon_xml = '<icon>MailAppIcon.icns</icon>'
    elif l.lower() in ("url", "urls"):
            #icon_xml = '<icon>BookmarkIcon.icns</icon>'
            icon_xml = '<icon>SafariAppIcon.icns</icon>'
    elif l.lower() in ("note", "notes", "nb"):
            icon_xml = '<icon>ToolbarInfo.icns</icon>'
    elif l.lower() in ("note", "notes", "nb"):
            icon_xml = '<icon>ToolbarInfo.icns</icon>'
    elif l.lower() in ("alert", "warning"):
            icon_xml = '<icon>AlertNoteIcon.icns</icon>'
    elif l.lower() in ("first_name", "last_name", "first name", "last name", "full_name", "full name", "name", "my name", "my_name"):
            icon_xml = '<icon type="filetype">public.vCard</icon>'
    elif 'password' in l.lower():
            icon_xml = '<icon>icon.png</icon>'
    elif 'ID' in l:
            icon_xml = '<icon>UserIcon.icns</icon>'
    elif 'HIN' in l:
            icon_xml = '<icon>UserIcon.icns</icon>'
    elif 'email' in l.lower():
            #icon_xml = '<icon>InternetLocation.icns</icon>'
            icon_xml = '<icon>MailAppIcon.icns</icon>'
    else:
            icon_xml = '<icon>AllMyFiles.icns</icon>'
            #icon_xml = ''

    return f"""
    <item arg="autotype {n+1:d} {QUERY:s}" valid="YES" autocomplete="{QUERY:s}: {xmlesc(l):s}">
        <title>{l:s}</title>
        {icon_xml:s}
        <subtitle>Copy &amp; autotype. Hold ⌥ to reveal. Hold ⌘ to copy.</subtitle>
        <mod key="option" subtitle="{xmlesc(v):s}"/>
        <mod key="command" subtitle="Copy to clipboard." valid="YES" arg="copy {n+1:d} {QUERY:s}"/>
    </item>""" 

# Debugging
debug = False
if debug:
    print(items)

print(
    '<?xml version="1.0"?>'
    + '\n' + "<items>" 
    + '\n' + ''.join([field_to_xml(field) for field in get_fields(sys.stdin.read())])
    + '\n' + '</items>'
)

