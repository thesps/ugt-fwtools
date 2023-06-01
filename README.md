# ugt-fwtools

Firmware build tools for Phase-1 uGT

## Install

```bash
pip install git+https://github.com/cms-l1-globaltrigger/ugt-fwtools.git@main
```

## Synthesis

```bash
ugt-simulate sample.xml --tv sample_ttbar.txt
```

Use command line option `--ugttag <tag>` to run with a different ugt tag or branch.

## Synthesis

```bash
ugt-synthesize sample.xml --build 0x1160
```

Use command line option `--ugttag <tag>` to run with a different ugt tag or branch.

## Check results

```bash
ugt-checksynth build_0x1160.cfg
```

## Build report

Print textile formatted information to be inserted in redmine issues and wiki.

```bash
ugt-buildreport build_0x1160.cfg
```

## Bundle firmware

```bash
ugt-fwpacker build_0x1160.cfg
```

## Vivado archives

Create Vivado archives of all modules.

```bash
ugt-archive build_0x1160.cfg
```

Create Vivado archive of individual module.

```bash
ugt-archive build_0x1160.cfg -m 1  # module_1
```
