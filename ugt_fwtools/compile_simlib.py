import argparse
import logging
import os
import shutil

DefaultQuestaSimPath = "/opt/mentor/questasim"
DefaultQuestaSimLibsPath = "questasimlibs"

pwd_script = os.path.dirname(__file__)
pwd = os.getcwd()


def run_command(*args):
    command = " ".join(args)
    logging.info(">$ %s", command)
    os.system(command)


def run_compile_simlib(vivado, questasim, questasimlib_path):

    # Check for UGT_VIVADO_BASE_DIR
    vivado_base_dir = os.getenv("UGT_VIVADO_BASE_DIR")
    if not vivado_base_dir:
        raise RuntimeError("Environment variable 'UGT_VIVADO_BASE_DIR' not set. Set with: 'export UGT_VIVADO_BASE_DIR=... (e.g. export UGT_VIVADO_BASE_DIR=/opt/xilinx/Vivado'")

    settings64 = os.path.join(vivado_base_dir, vivado, "settings64.sh")

    # Simulation directory
    sim_dir = os.path.join(pwd_script, "..", "firmware", "sim")
    # Installation path of questasim (tcl syntax)
    questasim_path = "{" + questasim + "/bin}"
    # Variable for compile_simlib syntax
    questasimlib_path_tcl = "{" + f"{questasimlib_path}" + "}"
    # Path and compile_simlib command of tcl file used in Vivado
    tcl_file = os.path.join(sim_dir, "scripts", "compile_simlib.tcl")
    tcl_compile_cmd = "compile_simlib -simulator questa -simulator_exec_path {questasim_path} -family virtex7 -language vhdl -library all -dir {questasimlib_path_tcl}".format(**locals())

    # Writing commands to tcl file
    with open(tcl_file, "wt") as fp:
        fp.write("#!/usr/bin/tcls\n")
        fp.write(f"{tcl_compile_cmd}\n")
        fp.write("exit\n")

    # Checking if questasimlib_path exists
    if not os.path.isdir(questasimlib_path):
        logging.info("===========================================================================")
        # Remove modelsim.ini before creating sim libs to get correct modelsim.ini in $HOME/questasimlibs_<version>
        utils.remove(os.path.join(pwd, "modelsim.ini"))
        source_tcl = os.path.join(pwd_script, "..", "firmware", "sim", "scripts", "compile_simlib.tcl")
        command = f'bash -c "source {settings64}; vivado -mode batch -source {source_tcl}"'
        logging.info("Creating Questa sim libs in %s (running %r)", questasimlib_path, source_tcl)
        run_command(command)
        utils.remove(os.path.join(pwd, "modelsim.ini"))
        logging.info("Done!")
        logging.info("===========================================================================")
    else:
        logging.info("===========================================================================")
        logging.info("Questa sim libs in %s already exists", questasimlib_path)
        logging.info("Nothing to do!")
        logging.info("===========================================================================")

    # Copy modelsim.ini from questasimlib dir to sim dir (to get questasim libs corresponding to Vivado version)
    shutil.copyfile(os.path.join(questasimlib_path, "modelsim.ini"), os.path.join(sim_dir, "modelsim.ini"))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vivado", help="Vivado version", required=True)
    parser.add_argument("--questasim", default=DefaultQuestaSimPath, help="Questasim installation path")
    parser.add_argument("--output", default=DefaultQuestaSimLibsPath, help="Questasim Vivado libraries path")
    return parser.parse_args()


def main():

    args = parse_args()

    # Setup console logging
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    run_compile_simlib(args.vivado, args.questasim, args.output)


if __name__ == "__main__":
    main()
