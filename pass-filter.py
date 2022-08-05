#!/usr/bin/env python3

from dataclasses import dataclass
from typing import *

import fnmatch
import os
import sys
import string


QUERY = sys.argv[1] if len(sys.argv) > 1 else None
HOME = os.environ['HOME']
PASS_DIR = os.environ.get('PASSWORD_STORE_DIR',os.path.join(HOME, '.password-store/'))


# TODO: list_passwords creates cache of passwords for first time
def list_passwords():
    ret = []

    for root, dirnames, filenames in os.walk(PASS_DIR, True, None, True):
        for filename in fnmatch.filter(filenames, '*.gpg'):
            ret.append(os.path.join(root, filename.replace('.gpg','')).replace(PASS_DIR, ''))
    return sorted(ret, key=lambda s: s.lower())


def is_match(password_name, query):
    # Any word of the query is in the password name
    #return any(spaceless_query in password_name.lower() for spaceless_query in query.split())

    # Match beginning of query with beginning of password name
    return password_name.startswith(query)

def search_passwords(query):
    #terms = filter(lambda x: x, query.lower().split())
    #return [ pname for pname in list_passwords() if is_match(pname, query) ]

    exclude_list    = [ ".git" , ".gpg-id" , ".gitattributes" ]
    exclude_hidden  = True # Exclude items beginning with a '.'

    # psp = password-store path. It's the path relative to PASS_DIR.
    def valid_psp(psp):
        # Exclude list
        if psp in exclude_list: return False
        # Exclude hidden
        if exclude_hidden and psp.split("/")[-1].startswith("."): return False
        # Include directories
        if os.path.isdir(os.path.join(PASS_DIR, psp)):  return True
        # Include files ending in '.gpg'
        if os.path.isfile(os.path.join(PASS_DIR, psp)): return psp.endswith('.gpg')
        # Shouldn't be any unhandled cases...
        assert False, f"Unhandled case in `valid_psp(...)`. Input was '{psp}'."

    def sortkey(passitem):
        return (not passitem.is_dir, passitem.psp)

    # Split query into the directory and the word at the end
    psp_query       = query
    if query is None:
        rel_dir = None
        abs_dir = PASS_DIR
        word    = None
    else:
        split = psp_query.rsplit("/", 1)  # Split into (at most) two parts, from the right.
        if len(split) == 1:
            rel_dir = None
            abs_dir = PASS_DIR
            word    = split[0]
        elif len(split) == 2:
            rel_dir, word = split
            abs_dir = os.path.join(PASS_DIR, rel_dir)
        else:
            assert False

    # Replace periods "." in the word at the end with '?' to act as a single-character wildcard.
    if word is not None:
        word = word.replace('.', '?')

    # Search inside the password-store, in rel_dir, for results beginning with 'word'
    def result_to_psp(result : str) -> str:
        if rel_dir is None:
            return result
        else:
            return os.path.join(rel_dir, result)

    # Get search results.
    str_results  = [ result for result in os.listdir(abs_dir) if fnmatch.fnmatch(result.lower(), (word.lower() if word is not None else "") + "*") ] #result.startswith(word if word is not None else "") ]
    psp_results  = [ psp for psp in map(result_to_psp, str_results) if valid_psp(psp) ]
    item_results = sorted(map(PassItem, psp_results), key=sortkey)
    return item_results

class PassItem:
    psp_list:   List[str]
    _psp:       str         = None
    _is_dir:    bool        = None

    def __init__(self, psp_maybe_list):
        if type(psp_maybe_list) is list:
            self.psp_list = psp_list
        elif type(psp_maybe_list) is str:
            self.psp_list = psp_maybe_list.split("/")
        else:
            raise ValueError("Did not receive a 'str' or 'list' type.")

    def __repr__(self):
        return f"PassItem({self.psp:s})"

    @property
    def as_xml(self):
        # See some information at: https://www.alfredapp.com/help/workflows/inputs/script-filter/xml/

        # Must not use UID if I want control over the ordering of displayed results.
        #uid         =   self.psp_noext
        arg         =   self.psp_noext
        autocomplete =  self.psp_noext if not self.is_dir else self.psp + "/"
        valid       =   "NO" if self.is_dir else "YES"

        title       =   self.psp_noext if not self.is_dir else self.psp + "/"
        subtitle    =   "Copy password: " + self.psp_noext if not self.is_dir else "Browse " + self.psp + "/"
        
        icon_xml    = '<icon>icon.png</icon>' if not self.is_dir else '<icon type="filetype">public.folder</icon>'
        mod_xml     = "" if self.is_dir else f"""<mod key="option" subtitle="Autotype password: {self.psp_noext:s}" valid="yes" arg="autotype_firstline {arg:s}"/>
        <mod key="shift" subtitle="Browse fields: {self.psp_noext:s}" valid="yes" arg="browse_fields {arg:s}"/>""" 

        return f"""
    <item arg="copy_firstline {arg:s}" autocomplete="{autocomplete:s}" valid="{valid:s}">
        <title>{title:s}</title>
        <subtitle>{subtitle:s}</subtitle>
        {icon_xml:s}
        {mod_xml:s}
    </item>"""

    @property
    def is_dir(self):
        if self._is_dir is None:
            self._is_dir = os.path.isdir(self.path)
        return self._is_dir

    @property
    def psp(self):
        if self._psp is None:
            self._psp = os.path.join(*self.psp_list)
        return self._psp

    @property
    def psp_noext(self):
        return self.psp.rsplit(".", 2)[0]

    @property
    def path(self):
        return os.path.join(PASS_DIR, self.psp)

if False: items_a.append("""
    <item uid="home" valid="YES" autocomplete="Home Folder" type="file">
        <title>Home Folder</title>
        <subtitle>Home folder ~/</subtitle>
        <subtitle mod="shift">Subtext when shift is pressed</subtitle>
        <subtitle mod="fn">Subtext when fn is pressed</subtitle>
        <subtitle mod="ctrl">Subtext when ctrl is pressed</subtitle>
        <subtitle mod="alt">Subtext when alt is pressed</subtitle>
        <subtitle mod="cmd">Subtext when cmd is pressed</subtitle>
        <text type="copy">Text when copying</text>
        <text type="largetype">Text for LargeType</text>
        <icon type="fileicon">~/</icon>
        <arg>~/</arg>
    </item>""")


items = search_passwords(QUERY)

# Debugging
debug = False
if debug:
    print(items)

print("""
<?xml version="1.0"?>
<items>""")
print(''.join([item.as_xml for item in items]))
print("""
</items>""")


