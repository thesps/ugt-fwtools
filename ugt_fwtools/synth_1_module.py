import re
import argparse
import configparser
import logging
import os
import subprocess
import shutil
import sys
from . import utils
from .synthesis import create_module, implement_module, show_screen_sessions


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("module_id", type=int, help="module ID (eg. 1)")
    parser.add_argument("filename", type=os.path.abspath, help=f"build config file (*.cfg)")
    return parser.parse_args()


def main() -> None:
    """Main routine."""

    # Parse command line arguments.
    args = parse_args()

    logger = utils.get_colored_logger(__name__)

    if not os.path.isfile(args.filename):
        logger.error(f"no such file: %r", args.filename)
        raise RuntimeError("missing build config file")

    # Check for UGT_VIVADO_BASE_DIR
    args.vivado_base_dir = os.getenv("UGT_VIVADO_BASE_DIR")
    if not args.vivado_base_dir:
        logger.error("environment variable 'UGT_VIVADO_BASE_DIR' not set.")
        logger.error("  Set with: 'export UGT_VIVADO_BASE_DIR=...'")
        raise RuntimeError("missing variable: UGT_VIVADO_BASE_DIR")

    config = configparser.ConfigParser()
    config.read(args.filename)

    args.board_type = config.get("device", "name")
    args.build = config.get("menu", "build")
    args.ipbb_dir = config.get("firmware", "buildarea")
    args.project_type = config.get("firmware", "type")
    args.vivado = config.get("vivado", "version")

    module_id = args.module_id
    module_name = f"module_{module_id}"
    module_path = os.path.join(args.ipbb_dir, "proj", module_name)

    # Vivado settings
    args.settings64 = os.path.join(args.vivado_base_dir, args.vivado, "settings64.sh")
    if not os.path.isfile(args.settings64):
        logger.error("no such Xilinx Vivado settings file: %r", args.settings64)
        logger.error("  check if Xilinx Vivado %r is installed on this machine.", args.vivado)
        raise RuntimeError("missing settings file")

    if os.path.exists(module_path):
        shutil.rmtree(module_path)

    logger.info("===========================================================================")
    logger.info("creating IPBB project for module %s ...", module_id)

    create_module(module_id, module_name, args)

    logger.info("===========================================================================")
    logger.info("running IPBB project, synthesis and implementation, creating bitfile for module %s ...", module_id)

    implement_module(module_id, module_name, args)

    logger.info("===========================================================================")
    show_screen_sessions()


if __name__ == "__main__":
    main()
