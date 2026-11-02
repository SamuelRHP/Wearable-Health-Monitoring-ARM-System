# Open Action Items for Student Confirmation

**Student:** Samuel Rohlupuia  
**Mini-Project:** Wearable Health-Monitoring ARM System  
**Last Updated:** 2026-11-02  

---

The project adheres to a strict verifiable source policy: **NEVER invent course outcome wording, datasheet figures, or syllabus acronyms.**  
The following open items require input or confirmation from your course syllabus and instructor:

| Item # | Category | Description | Current Project Status | Action Required from Student |
| :--- | :--- | :--- | :--- | :--- |
| **OI-01** | **Syllabus COs** | Exact wording of Course Outcomes: **CO1, CO2, CO3, CO4, CO5, CO6**. | Draft mapping created in `docs/CO_MAPPING.md` with description columns marked `PASTE FROM SYLLABUS`. Proposed module and test mappings are prepared. | Paste the exact 1-to-2 sentence description for each CO from your university course syllabus into `docs/CO_MAPPING.md`. |
| **OI-02** | **Course Dimensions** | Exact definition of project dimensions **CT** and **RWE**. | Draft table created in `docs/DIMENSION.md` marked `PASTE FROM SYLLABUS`. (Likely stands for *Computational Thinking* and *Real-World Engineering* or *Real-World Experience*, but left unassumed). | Confirm the official terminology from your evaluation rubric and paste definitions into `docs/DIMENSION.md`. |
| **OI-03** | **Datasheet Figures** | Target microcontroller selection and power figures. | Set to **STMicroelectronics STM32L476RG** (DocID025976 Rev 5, Table 34 & 39) with values labeled `PLACEHOLDER: true` in `config/energy_params.yaml`. Active warnings appear in all reports and API responses. | Verify if your professor prefers a specific Cortex-M chip (e.g., STM32L476, nRF52832, or SAM L10). Once confirmed, update `config/energy_params.yaml` and set `is_placeholder: false`. |
| **OI-04** | **PhysioNet Record** | Selection of PhysioNet dataset and record. | Implemented using **BIDMC PPG and Respiration Dataset (`bidmc01`)**, sampled at 125 Hz under Open Data Commons Attribution License v1.0 (ODC-By 1.0). Includes high-fidelity synthetic fallback. | Confirm if `bidmc01` is accepted or if another record (e.g. `bidmc02` or MIMIC-II) is required. |
| **OI-05** | **Cache Parameters** | Cache capacity and line size preferences for academic presentation. | Configured as 4 KB direct-mapped cache with 16-byte lines ($AMAT = 1.01$ cycles vs 20.0 cycles un-cached). Set-associative option available (2-way, 4-way). | Confirm whether 4 KB direct-mapped is the exact baseline required for your evaluation viva. |
