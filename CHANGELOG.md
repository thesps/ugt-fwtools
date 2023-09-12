# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.2] - 2023-09-12

### Changed
- module 'simulation' (added option "-lic_noqueue" to 'cmd' [vsim_bin, ...] in 'run_vsim')
to prevent waiting for license in a queue.  

## [0.1.1] - 2023-06-15

### Changed
- default mp7 repository to `https://gitlab.cern.ch/cms-l1-globaltrigger/mp7.git`

### Fixed
- bugs in modules `fwpacker` and `synthesis`

## [0.1.0] - 2023-05-12

### Added
- Migrated scripts from `ugt_mp7_legacy/scripts` repo.

[Unreleased]: https://github.com/cms-l1-globaltrigger/ugt-fwtools/compare/0.1.1...HEAD
[0.1.1]: https://github.com/cms-l1-globaltrigger/ugt-fwtools/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/cms-l1-globaltrigger/ugt-fwtools/releases/tag/0.1.0
