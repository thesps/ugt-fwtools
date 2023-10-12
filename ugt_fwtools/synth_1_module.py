import re
import argparse
import configparser
import logging
import os
import subprocess
import shutil
import sys
from . import utils
from .synthesis import create_module, implement_module, show_screen_sessions, start_screen_session

tty_bold_red = "\033[1;31m"
tty_reset = "\033[0m"

def print_error(message):
    if sys.stdout.isatty():
        message = f"{tty_bold_red}{message}{tty_reset}"
    print(message)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("mod_id", help="module number (eg. 1)")
    parser.add_argument("path", metavar="<path>", type=os.path.abspath, help=f"fw build path to config file")
    return parser.parse_args()

def main() -> None:
    """Main routine."""

    # Parse command line arguments.
    args = parse_args()
    
    if not os.path.isfile(args.path):
        message = f"\n===> no such file {args.path!r}\n"
        print_error(message) 
        raise RuntimeError("missing build config file") 

    config = configparser.ConfigParser()
    config.read(args.path)

    args.board_type = config.get("device","name")
    args.build = config.get("menu","build")
    args.ipbb_dir = config.get("firmware","buildarea")
    args.project_type = config.get("firmware","type")
    args.vivado = config.get("vivado","version")
    module_id = args.mod_id
    module_name = f"module_{module_id}"
    module_path = os.path.join(args.ipbb_dir, "proj", module_name)

    # Check for UGT_VIVADO_BASE_DIR
    args.vivado_base_dir = os.getenv("UGT_VIVADO_BASE_DIR")
    if not args.vivado_base_dir:
        message = "\n===> environment variable 'UGT_VIVADO_BASE_DIR' not set. Set with: 'export UGT_VIVADO_BASE_DIR=...'\n"
        print_error(message) 
        raise RuntimeError("missing variable: UGT_VIVADO_BASE_DIR") 

    # Vivado settings
    args.settings64 = os.path.join(args.vivado_base_dir, args.vivado, "settings64.sh")
    if not os.path.isfile(args.settings64):
        message = f"\n===> no such Xilinx Vivado settings file {args.settings64!r}\n    check if Xilinx Vivado {args.vivado} is installed on this machine\n"
        print_error(message) 
        raise RuntimeError("missing settings file") 

    if os.path.exists(module_path):
        shutil.rmtree(module_path)

    logging.info("===========================================================================")
    logging.info("creating IPBB project for module %s ...", module_id)

    create_module(module_id, module_name, args)

    logging.info("===========================================================================")
    logging.info("running IPBB project, synthesis and implementation, creating bitfile for module %s ...", module_id)

    implement_module(module_id, module_name, args)

    logging.info("===========================================================================")
    show_screen_sessions()
    
if __name__ == "__main__":
    main()



