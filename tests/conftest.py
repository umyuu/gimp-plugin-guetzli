# -*- coding: utf-8 -*-
import sys
import os

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
for path in [parent_dir , os.path.join(parent_dir, 'src')]:
    if not (path in sys.path):
        sys.path.insert(0, path)
