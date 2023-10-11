import re
import argparse
import configparser
import logging
import os
import subprocess
from . import utils
from .synthesis import create_module, implement_module, show_screen_sessions, start_screen_session

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
        raise RuntimeError(
            f"\033[1;31m no such file {args.path!r} \033[0m"
        )

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
        raise RuntimeError("\033[1;31m Environment variable 'UGT_VIVADO_BASE_DIR' not set. Set with: 'export UGT_VIVADO_BASE_DIR=...' \033[0m")

    # Vivado settings
    args.settings64 = os.path.join(args.vivado_base_dir, args.vivado, "settings64.sh")
    if not os.path.isfile(args.settings64):
        raise RuntimeError(
            f"\033[1;31m no such Xilinx Vivado settings file {args.settings64!r}\n \033[0m"
            f"   \033[1;31m check if Xilinx Vivado {args.vivado} is installed on this machine. \033[0m"
        )

    if os.path.exists(module_path):
        subprocess.run(["rm", "-rf", module_path]).check_returncode()

    logging.info("===========================================================================")
    logging.info("creating IPBB project for module %s ...", module_id)

    create_module(module_id, module_name, args)

    logging.info("===========================================================================")
    logging.info("running IPBB project, synthesis and implementation, creating bitfile for module %s ...", module_id)

    implement_module(module_id, module_name, args)

    logging.info("===========================================================================")
    show_screen_sessions()

    os.chdir(args.ipbb_dir)
    
if __name__ == "__main__":
    main()


