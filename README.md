# ugt-fwtools

Firmware build tools for Phase-1 uGT

## Install

```bash
pip install git+https://github.com/cms-l1-globaltrigger/ugt-fwtools.git@0.1.0
```

## Synthesis

```bash
ugt-runsynth sample.xml --build 0x1160
```

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
