#!/usr/bin/env python3
"""Issue short-lived lab certificates offline. Use your organizational CA in production."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess


def run(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=60)


