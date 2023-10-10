import re
import argparse
import configparser
import logging
import os
import subprocess
from . import utils

DefaultVivadoVersion = os.getenv("UGT_VIVADO_VERSION", "")
if not DefaultVivadoVersion:
    raise RuntimeError("UGT_VIVADO_VERSION is not defined.")

VivadoBaseDir = os.getenv("UGT_VIVADO_BASE_DIR", "")
if not VivadoBaseDir:
    raise RuntimeError("UGT_VIVADO_BASE_DIR is not defined.")

vivadoPath = os.path.abspath(os.path.join(VivadoBaseDir, DefaultVivadoVersion))
if not os.path.isdir(vivadoPath):
    raise RuntimeError("No installation of Vivado in %r" % vivadoPath)

DefaultUgtRepoName = "mp7_ugt_legacy"

def implement_module(module_id: int, module_name: str, args) -> None:
    """Run module implementation in screen session."""
    # IPBB commands: running IPBB project, synthesis and implementation, creating bitfile
    cmd_ipbb_project = "ipbb vivado generate-project --single"  # workaround to prevent "hang-up" in make-project with IPBB v0.5.2
    cmd_ipbb_synth = "ipbb vivado synth impl package"

    # Set variable "module_id" for tcl script (l1menu_files.tcl in uGT_algo.dep)
    command = f'cd; source {args.settings64}; cd {args.ipbb_dir}/proj/{module_name}; module_id={module_id} {cmd_ipbb_project} && {cmd_ipbb_synth}'

    session = f"build_{args.project_type}_{args.build}_{module_id}"
    logging.info("starting screen session %r for module %s ...", session, module_id)
    start_screen_session(session, command)

def show_screen_sessions() -> None:
    subprocess.run(["screen", "-ls"])

def start_screen_session(session: str, commands: str) -> None:
    subprocess.run(["screen", "-dmS", session, "bash", "-c", commands]).check_returncode()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
#    parser.add_argument("--vivado", metavar="<version>", default=DefaultVivadoVersion, type=utils.vivado_t, help=f"Vivado version to run (default is {DefaultVivadoVersion!r})")
#    parser.add_argument("--build", type=utils.build_str_t, required=True, metavar="<version>", help="menu build version (eg. 0x1001) [required]")
    parser.add_argument("--mod_id", required=True, help="module number (eg. 1) [required]")
    parser.add_argument("--path", metavar="<path>", required=True, type=os.path.abspath, help=f"fw build path to config file [required]")
#    parser.add_argument("--ugt", default=DefaultUgtRepoName, help=f"ugt repo name (default is {DefaultUgtRepoName!r})")
    return parser.parse_args()

def main() -> None:
    """Main routine."""

    # Parse command line arguments.
    args = parse_args()
    
#    args.ipbb_dir = os.path.join(args.path, args.build)
#    args.project_type =  args.ugt
    module_id = args.mod_id
    module_name = f"module_{module_id}"
    proj_path = os.path.join(args.ipbb_dir, "proj")

    # Check for UGT_VIVADO_BASE_DIR
    args.vivado_base_dir = os.getenv("UGT_VIVADO_BASE_DIR")
    if not vivado_base_dir:
        raise RuntimeError("Environment variable 'UGT_VIVADO_BASE_DIR' not set. Set with: 'export UGT_VIVADO_BASE_DIR=...'")

    # Vivado settings
    args.settings64 = os.path.join(args.vivado_base_dir, args.vivado, "settings64.sh")
    if not os.path.isfile(settings64):
        raise RuntimeError(
            f"no such Xilinx Vivado settings file {settings64!r}\n"
            f"  check if Xilinx Vivado {args.vivado} is installed on this machine."
	)

    if not os.path.exists(proj_path):
        raise RuntimeError(f"Path {proj_path!r} does not exist")    
    
    logging.info("===========================================================================")
    logging.info("running IPBB project, synthesis and implementation, creating bitfile for module %s ...", module_id)

    implement_module(module_id, module_name, args)

    # IPBB commands: running IPBB project, synthesis and implementation, creating bitfile
    #cmd_ipbb_project = "ipbb vivado generate-project --single"  # workaround to prevent "hang-up" in make-project with IPBB v0.5.2
    #cmd_ipbb_synth = "ipbb vivado synth impl package"

    # Set variable "module_id" for tcl script (l1menu_files.tcl in uGT_algo.dep)
    #command = f'cd; source {settings64}; cd {ipbb_dir}/{args.build}/proj/{module_name}; module_id={module_id} {cmd_ipbb_project} && {cmd_ipbb_synth}'

    #session = f"build_{project_type}_{args.build}_{module_id}"
    #logging.info("starting screen session %r for module %s ...", session, module_id)

    #start_screen_session(session, command)

    # list running screen sessions
    logging.info("===========================================================================")
    show_screen_sessions()

    os.chdir(ipbb_dir)
    
if __name__ == "__main__":
    main()


