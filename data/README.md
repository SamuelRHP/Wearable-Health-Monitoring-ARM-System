# PhysioNet BIDMC PPG and Respiration Dataset

## Dataset Metadata
- **Source Database:** BIDMC PPG and Respiration Dataset (version 1.0.0)
- **PhysioNet URL:** [https://physionet.org/content/bidmc/1.0.0/](https://physionet.org/content/bidmc/1.0.0/)
- **Licence:** Open Data Commons Attribution License v1.0 (ODC-By 1.0)
- **Origin:** Extracted from the MIMIC-II matched waveform database, acquired from intensive care patients at Beth Israel Deaconess Medical Center, Boston, MA.
- **Sampling Frequency ($f_s$):** 125 Hz
- **Signal Channels:**
  - `PLETH`: Photoplethysmogram (PPG) pulse signal
  - `RESP`: Respiration impedance signal
  - `V`: Lead II Electrocardiogram (ECG)

## Available Records
- `bidmc01`
- `bidmc02`
- `bidmc03` ... `bidmc53`

## Data Download Script
Run the helper script to download `bidmc01` locally:
```bash
python data/download_bidmc.py
```
*Note: In accordance with repository constraints, large raw data files (`.dat`, `.hea`) are ignored by `.gitignore` and are fetched on demand or substituted with the built-in synthetic signal generator for offline environments.*
