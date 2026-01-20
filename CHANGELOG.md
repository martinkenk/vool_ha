# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### Added
- Initial HACS-compatible release
- Support for VOOL EV Charger (Wallbox) via Cloud API
- Support for VOOL Load Management Controller (LMC)
- Full UI configuration through Home Assistant
- Sensors for power (kW), current (A), voltage (V) per phase
- HACS compatibility with CI/CD workflows
- Proper sensor device classes and state classes for energy dashboard compatibility

### Changed
- Restructured for HACS compatibility (custom_components folder structure)
- Updated sensor units to use kW for power (matching energy dashboard requirements)
- Added proper SensorDeviceClass and SensorStateClass for all sensors

## [0.2.0] - Previous Release

### Added
- Initial release with basic VOOL API support
- Power monitoring for Wallbox and LMC devices
