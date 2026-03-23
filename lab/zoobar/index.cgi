#!/home/eitanbellaiche/Desktop/Shenkar/cyberSecurity/lab/venv/bin/python3
#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.dirname(__file__))

from __init__ import *
from wsgiref.handlers import CGIHandler


if __name__ == "__main__":
    CGIHandler().run(app)
