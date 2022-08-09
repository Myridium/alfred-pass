#!/usr/bin/env python3

# First arg should be the name of the password-store entry.

from typing import *

import os
import sys
import subprocess
import functools


QUERY = sys.argv[1] # Must have at least one arg
HOME = os.environ['HOME']
PASS_DIR = os.environ.get('PASSWORD_STORE_DIR', os.path.join(HOME, '.password-store/'))

# Unused. If this is called within this script, then Alfred loses focus if a password prompt appears.
def get_pass_show(psp : str) -> str:
    result = subprocess.run(['pass', 'show', psp], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

print(get_pass_show(QUERY), end="")

