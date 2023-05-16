# ugt-fwtools

Firmware build tools for Phase-1 uGT

## Install

```bash
pip install git+https://github.com/cms-l1-globaltrigger/ugt-fwtools.git@1.0.0
```

## Synthesis

```bash
ugt-runsynth sample.xml --build 0x1160
```

## Vivado archives

Create Vivado archives of all modules.

```bash
ugt-archive ./build_0x1160.cfg
```

Create Vivado archive of individual module.

```bash
ugt-archive ./build_0x1160.cfg -m 1  # module_1
```
