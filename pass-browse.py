#!/usr/bin/env python3

# First arg should be the name of the password-store entry.
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


def get_pass_show(psp : str) -> str:
    result = subprocess.run(['pass', 'show', psp], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output
   
def get_fields(psp : str) -> List[str]:
    pass_show_output = get_pass_show(psp)
    nums_labels_values : List[Tuple[int, str, str]] = [ 
            (n, *m.groups()) 
            for n,m in map(
                lambda x : (x[0], re.fullmatch("^ *([^:]+): +( ?[^ ]+) *$", x[1])) , 
                enumerate(pass_show_output.splitlines()) ) 
            if m is not None ]
    return nums_labels_values # list of fields. Each is a 3-tuple. (linenum, field_label, field_value)

def password_xml() -> str:
    n,l = 0, "Password"
    return f"""
    <item arg="copy {n+1:d} {QUERY:s}" valid="YES" autocomplete="{QUERY:s}: {l:s}">
        <title>{l:s}</title>
        <subtitle>Copy</subtitle>
        <mod key="shift" subtitle="Copy &amp; autotype" valid="YES" arg="autotype {n+1:d} {QUERY:s}"/>
    </item>""" 

def field_to_xml(field : Tuple[int,str,str]) -> str:
    n,l,v = field
    return f"""
    <item arg="copy {n+1:d} {QUERY:s}" valid="YES" autocomplete="{QUERY:s}: {l:s}">
        <title>{l:s}: ******</title>
        <subtitle>Copy '{l:s}' to clipboard</subtitle>
        <mod key="shift" subtitle="Copy &amp; autotype" valid="YES" arg="autotype {n+1:d} {QUERY:s}"/>
    </item>""" 

# Debugging
debug = False
if debug:
    print(items)

print("""
<?xml version="1.0"?>
<items>""")
#print(''.join([item.as_xml for item in items]))
#print(get_fields(QUERY))
print(password_xml())
print(''.join([field_to_xml(field) for field in get_fields(QUERY)]))
print("""
</items>""")


