# System Configuration & Parameter Validation

This folder contains YAML configuration files controlling simulation defaults, parameter validation ranges, and energy modeling parameters.

## Files
- `default.yaml`: Default parameters for signal acquisition, UART/I2C serial buses, cache hierarchy, and acceptable input validation ranges for the CLI and REST API.
- `energy_params.yaml`: Energy model parameters (active and sleep current draw, voltage, duty cycle) referencing manufacturer datasheets.

## Handling of PLACEHOLDER Values (Hard Constraint)
As required by the project constraints:
1. Every placeholder value is strictly labeled `PLACEHOLDER: true` inside `config/energy_params.yaml`.
2. Every simulation run, CLI report, and API response checks this flag and automatically injects a visible warning:
   `"WARNING: Energy parameters are unverified PLACEHOLDER values pending datasheet confirmation by student (see docs/OPEN_ITEMS.md). Results are estimated from manufacturer datasheets; never claim real battery life."`
3. Until the student confirms the specific microcontroller datasheet, page number, and revision, all energy metrics are explicitly worded as **"estimated from datasheet figures"** and never as measured battery life.
