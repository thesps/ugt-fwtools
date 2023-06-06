import argparse
import configparser
import logging
import os
import pathlib
import shutil
import subprocess
import urllib.request
import urllib.parse
import urllib.error
from typing import Dict, List

from . import utils
from .xmlmenu import XmlMenu

BoardAliases: Dict[str, str] = {
    "mp7xe_690": "xe",
}

DefaultVivadoVersion = os.getenv("UGT_VIVADO_VERSION")
if not DefaultVivadoVersion:
    raise RuntimeError("UGT_VIVADO_VERSION is not defined.")

VivadoBaseDir = os.getenv("UGT_VIVADO_BASE_DIR")
if not VivadoBaseDir:
    raise RuntimeError("UGT_VIVADO_BASE_DIR is not defined.")

vivadoPath = os.path.abspath(os.path.join(VivadoBaseDir, DefaultVivadoVersion))
if not os.path.isdir(vivadoPath):
    raise RuntimeError("No installation of Vivado in %r" % vivadoPath)

DefaultBoardType: str = "mp7xe_690"
"""Default board type to be used."""

DefaultFirmwareDir: str = os.path.expanduser("~/work_synth/production")
"""Default output directory for firmware builds."""

DefaultGitlabUrlIPB: str = "https://github.com/ipbus/ipbus-firmware.git"
"""Default URL IPB FW repo."""

DefaultIpbFwTag: str = "v1.4"
"""Default tag IPB FW repo."""

DefaultMP7Url: str = "https://gitlab.cern.ch/arnold/mp7.git"
"""Default URL MP7 FW repo."""

DefaultMP7Tag: str = "v3.2.2_Vivado2021+_ugt"
"""Default tag MP7 FW repo."""

DefaultUgtUrl: str = "https://github.com/cms-l1-globaltrigger/mp7_ugt_legacy.git"
"""Default URL for ugt FW repo."""

DefaultUgtTag: str = "v1.22.3"
"""Default tag for ugt FW repo."""

vhdl_snippets: List[str] = [
    "algo_index.vhd",
    "gtl_module_instances.vhd",
    "gtl_module_signals.vhd",
    "ugt_constants.vhd",
]


def raw_build(build: str) -> str:
    """Return build id without hex prefix."""
    return format(int(build, 16), "04x")


def show_screen_sessions() -> None:
    subprocess.run(["screen", "-ls"])


def start_screen_session(session: str, commands: str) -> None:
    subprocess.run(["screen", "-dmS", session, "bash", "-c", commands]).check_returncode()


def get_ipbb_version() -> str:
    result = subprocess.run(["ipbb", "--version"], stdout=subprocess.PIPE)
    return result.stdout.decode().split()[-1].strip()  # ipbb, version 0.5.2


def download_file_from_url(url: str, filename: str) -> None:
    """Download file from URL."""
    # Remove existing file.
    utils.remove(filename)
    # Download file
    logging.info("retrieving from: %r ", url)
    urllib.request.urlretrieve(url, filename)


def get_uri(path: str) -> str:
    """Return URI from path or URI."""
    if urllib.parse.urlparse(path).scheme:
        return path
    else:
        uri_path = pathlib.Path(path).resolve()
        return urllib.parse.urljoin("file:", urllib.request.pathname2url(str(uri_path)))


def get_menu_name(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def replace_vhdl_templates(vhdl_snippets_dir: str, src_fw_dir: str, dest_fw_dir: str) -> None:
    """Replace VHDL templates with snippets from VHDL Producer."""
    # Read generated VHDL snippets
    logging.info("replace VHDL templates with snippets from VHDL Producer ...")
    replace_map = {
        "{{algo_index}}": utils.read_file(os.path.join(vhdl_snippets_dir, "algo_index.vhd")),
        "{{ugt_constants}}": utils.read_file(os.path.join(vhdl_snippets_dir, "ugt_constants.vhd")),
        "{{gtl_module_signals}}": utils.read_file(os.path.join(vhdl_snippets_dir, "gtl_module_signals.vhd")),
        "{{gtl_module_instances}}": utils.read_file(os.path.join(vhdl_snippets_dir, "gtl_module_instances.vhd")),
    }

    gtl_fdl_wrapper_dir = os.path.join(src_fw_dir, "hdl", "payload")
    fdl_dir = os.path.join(gtl_fdl_wrapper_dir, "fdl")
    pkg_dir = os.path.join(src_fw_dir, "hdl", "packages")

    # Patch VHDL files in IPBB area (
    utils.template_replace(os.path.join(fdl_dir, "algo_mapping_rop_tpl.vhd"), replace_map, os.path.join(dest_fw_dir, "algo_mapping_rop.vhd"))
    utils.template_replace(os.path.join(pkg_dir, "fdl_pkg_tpl.vhd"), replace_map, os.path.join(dest_fw_dir, "fdl_pkg.vhd"))
    utils.template_replace(os.path.join(gtl_fdl_wrapper_dir, "gtl_module_tpl.vhd"), replace_map, os.path.join(dest_fw_dir, "gtl_module.vhd"))


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument("menu_xml", help="path to menu xml file (in repository or local")
    parser.add_argument("--vivado", metavar="<version>", default=DefaultVivadoVersion, type=utils.vivado_t, help=f"Vivado version to run (default is {DefaultVivadoVersion!r})")
    parser.add_argument("--ipburl", metavar="<path>", default=DefaultGitlabUrlIPB, help=f"URL of IPB firmware repo (default is {DefaultGitlabUrlIPB!r})")
    parser.add_argument("-i", "--ipbtag", metavar="<tag>", default=DefaultIpbFwTag, help=f"IPBus firmware repo: tag or branch name (default is {DefaultIpbFwTag!r})")
    parser.add_argument("--mp7url", metavar="<path>", default=DefaultMP7Url, help=f"URL of MP7 firmware repo (default is {DefaultMP7Url!r})")
    parser.add_argument("--mp7tag", metavar="<tag>", default=DefaultMP7Tag, help=f"MP7 firmware repo: tag name (default is {DefaultMP7Tag!r})")
    parser.add_argument("--ugturl", metavar="<path>", default=DefaultUgtUrl, help=f"URL of ugt firmware repo (default is {DefaultUgtUrl!r})")
    parser.add_argument("--ugttag", metavar="<tag>", default=DefaultUgtTag, help=f"ugt firmware repo: tag or branch name (default is {DefaultUgtTag!r})")
    parser.add_argument("--build", type=utils.build_str_t, required=True, metavar="<version>", help="menu build version (eg. 0x1001) [required]")
    parser.add_argument("--board", metavar="<type>", default=DefaultBoardType, choices=list(BoardAliases.keys()), help=f"set board type (default is {DefaultBoardType!r})")
    parser.add_argument("-p", "--path", metavar="<path>", default=DefaultFirmwareDir, type=os.path.abspath, help=f"fw build path (default is {DefaultFirmwareDir!r})")
    return parser.parse_args()


def main() -> None:
    """Main routine."""

    # Parse command line arguments.
    args = parse_args()

    xml_uri = get_uri(args.menu_xml)
    menu_name = get_menu_name(xml_uri)

    # check menu name
    utils.menuname_t(menu_name)

    # Setup console logging
    logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

    # Check for UGT_VIVADO_BASE_DIR
    vivado_base_dir = os.getenv("UGT_VIVADO_BASE_DIR")
    if not vivado_base_dir:
        raise RuntimeError("Environment variable 'UGT_VIVADO_BASE_DIR' not set. Set with: 'export UGT_VIVADO_BASE_DIR=...'")

    # TODO
    # Board type taken from mp7url repo name
    board_type_repo_name = os.path.basename(args.mp7url)
    if board_type_repo_name.find(".") > 0:
        board_type = board_type_repo_name.split(".")[0]    # Remove ".git" from repo name
    else:
        board_type = board_type_repo_name

    # TODO
    # Project type taken from ugturl repo name
    project_type_repo_name = os.path.basename(args.ugturl)
    if project_type_repo_name.find(".") > 0:
        project_type = project_type_repo_name.split(".")[0]    # Remove ".git" from repo name
    else:
        project_type = project_type_repo_name

    # TODO
    vivado_version = f"vivado_{args.vivado}"
    ipbb_dir = os.path.join(args.path, args.build, menu_name, project_type, args.ugttag, args.mp7tag, vivado_version)
    ipbb_dir_build = os.path.join(args.path, args.build)

    if os.path.isdir(ipbb_dir_build):
        raise RuntimeError(f"build area already exists: {ipbb_dir_build}")

    logging.info("===========================================================================")
    logging.info("creating IPBB area ...")

    ipbb_version = get_ipbb_version()
    logging.info("ipbb_version: %s", ipbb_version)

    # IPBB commands: creating IPBB area
    subprocess.run(["ipbb", "init", ipbb_dir]).check_returncode()
    subprocess.run(["ipbb", "add", "git", args.ipburl, "-b", args.ipbtag], cwd=ipbb_dir).check_returncode()
    subprocess.run(["ipbb", "add", "git", args.mp7url, "-b", args.mp7tag], cwd=ipbb_dir).check_returncode()
    subprocess.run(["ipbb", "add", "git", args.ugturl, "-b", args.ugttag], cwd=ipbb_dir).check_returncode()

    xml_filename = os.path.join(ipbb_dir, "src", f"{menu_name}.xml")

    logging.info("===========================================================================")
    logging.info("retrieve %r...", xml_filename)
    download_file_from_url(xml_uri, xml_filename)

    html_uri = urllib.parse.urljoin(xml_uri, f"../doc/{menu_name}.html")
    html_filename = os.path.join(ipbb_dir, "src", f"{menu_name}.html")

    logging.info("===========================================================================")
    logging.info("retrieve %r...", html_filename)
    download_file_from_url(html_uri, html_filename)

    menu = XmlMenu(xml_filename)

    # Fetch menu name from path.
    menu_name = menu.name

    if not menu_name.startswith("L1Menu_"):
        raise RuntimeError(f"Invamenu_nameme: {menu_name!r}")

    # Fetch number of menu modules.
    modules = menu.n_modules

    if not modules:
        raise RuntimeError("Menu contains no modules")

    ipbb_src_fw_dir = os.path.abspath(os.path.join(ipbb_dir, "src", project_type, "firmware"))

    for module_id in range(modules):
        module_name = f"module_{module_id}"
        ipbb_module_dir = os.path.join(ipbb_dir, module_name)

        ipbb_dest_fw_dir = os.path.abspath(os.path.join(ipbb_dir, "src", module_name))
        os.makedirs(ipbb_dest_fw_dir)

        # Download generated VHDL snippets from repository and replace VHDL templates
        logging.info("===========================================================================")
        logging.info(" *** module %s ***", module_id)
        logging.info("===========================================================================")
        logging.info("retrieve VHDL snippets for module %s and replace VHDL templates ...", module_id)
        vhdl_snippets_dir = os.path.join(ipbb_dest_fw_dir, "vhdl_snippets")
        os.makedirs(vhdl_snippets_dir)

        # TODO
        for vhdl_snippet in vhdl_snippets:
            filename = os.path.join(vhdl_snippets_dir, vhdl_snippet)
            snippet_uri = urllib.parse.urljoin(xml_uri, f"../vhdl/{module_name}/src/{vhdl_snippet}")
            download_file_from_url(snippet_uri, filename)

        replace_vhdl_templates(vhdl_snippets_dir, ipbb_src_fw_dir, ipbb_dest_fw_dir)

        logging.info("patch the target package with current UNIX timestamp/username/hostname ...")
        top_pkg_tpl = os.path.join(ipbb_src_fw_dir, "hdl", "packages", "gt_mp7_top_pkg_tpl.vhd")
        top_pkg = os.path.join(ipbb_src_fw_dir, "hdl", "packages", "gt_mp7_top_pkg.vhd")
        subprocess.run(["python", os.path.join(ipbb_src_fw_dir, "..", "scripts", "pkgpatch.py"), "--build", args.build, top_pkg_tpl, top_pkg]).check_returncode()

        # Vivado settings
        settings64 = os.path.join(vivado_base_dir, args.vivado, "settings64.sh")
        if not os.path.isfile(settings64):
            raise RuntimeError(
                f"no such Xilinx Vivado settings file {settings64!r}\n"
                f"  check if Xilinx Vivado {args.vivado} is installed on this machine."
            )

        logging.info("===========================================================================")
        logging.info("creating IPBB project for module %s ...", module_id)

        subprocess.run(["ipbb", "proj", "create", "vivado", module_name, f"{board_type}:../{project_type}"], cwd=ipbb_dir).check_returncode()

        logging.info("===========================================================================")
        logging.info("running IPBB project, synthesis and implementation, creating bitfile for module %s ...", module_id)

        # IPBB commands: running IPBB project, synthesis and implementation, creating bitfile
        cmd_ipbb_project = "ipbb vivado generate-project --single"  # workaround to prevent "hang-up" in make-project with IPBB v0.5.2
        cmd_ipbb_synth = "ipbb vivado synth impl package"

        # Set variable "module_id" for tcl script (l1menu_files.tcl in uGT_algo.dep)
        command = f'cd; source {settings64}; cd {ipbb_dir}/proj/{module_name}; module_id={module_id} {cmd_ipbb_project} && {cmd_ipbb_synth}'

        session = f"build_{project_type}_{args.build}_{module_id}"
        logging.info("starting screen session %r for module %s ...", session, module_id)
        start_screen_session(session, command)

    # list running screen sessions
    logging.info("===========================================================================")
    show_screen_sessions()

    os.chdir(ipbb_dir)

    # Creating configuration file.
    config = configparser.RawConfigParser()
    config.add_section("environment")
    config.set("environment", "timestamp", utils.timestamp())
    config.set("environment", "hostname", utils.hostname())
    config.set("environment", "username", utils.username())

    config.add_section("menu")
    config.set("menu", "build", utils.build_t(args.build))
    config.set("menu", "name", menu_name)
    config.set("menu", "location", xml_uri)
    config.set("menu", "modules", modules)

    config.add_section("ipbb")
    config.set("ipbb", "version", ipbb_version)

    config.add_section("vivado")
    config.set("vivado", "version", args.vivado)

    config.add_section("firmware")
    config.set("firmware", "ipburl", args.ipburl)
    config.set("firmware", "ipbtag", args.ipbtag)
    config.set("firmware", "mp7url", args.mp7url)
    config.set("firmware", "mp7tag", args.mp7tag)
    config.set("firmware", "ugturl", args.ugturl)
    config.set("firmware", "ugttag", args.ugttag)
    config.set("firmware", "type", project_type)
    config.set("firmware", "buildarea", ipbb_dir)

    config.add_section("device")
    config.set("device", "type", args.board)
    config.set("device", "name", board_type)
    config.set("device", "alias", BoardAliases[args.board])

    config_filename = f"build_{args.build}.cfg"

    # Writing configuration file
    with open(config_filename, "wt") as fp:
        config.write(fp)

    logging.info("created configuration file: %r", config_filename)
    logging.info("done.")


if __name__ == "__main__":
    main()
