# Reputable & Verified References

**Project:** Wearable Health-Monitoring ARM System  
**Author:** Samuel Rohlupuia  

> [!NOTE]
> All citations, datasheet figures, URLs, and reference manuals listed below have been verified. No unverified, fabricated, or assumed references are included.

---

## 1. Physiological Signals & Clinical Data
- **PhysioNet BIDMC PPG and Respiration Dataset:**
  - Pimentel, M. A., Johnson, A. E., Charlton, P. H., Birrenkott, D., Watkinson, P. J., Tarassenko, L., & Clifton, D. A. (2016). *Toward a robust estimation of respiratory rate from pulse oximeters*. IEEE Transactions on Biomedical Engineering, 64(8), 1914-1923.
  - PhysioNet Repository URL: [https://physionet.org/content/bidmc/1.0.0/](https://physionet.org/content/bidmc/1.0.0/)
  - License: Open Data Commons Attribution License v1.0 (ODC-By 1.0)
  - Sampling Rate: 125 Hz (Channels: `PLETH`, `RESP`, `V`).

## 2. Microarchitecture & ARM ISA
- **Arm Architecture Reference Manual ARMv7-M:**
  - Arm Limited. *ARMv7-M Architecture Reference Manual* (ARM DDI 0403E.e, Issue E.e).
  - URL: [https://developer.arm.com/documentation/ddi0403/latest/](https://developer.arm.com/documentation/ddi0403/latest/)
  - Covers Thumb-1 / Thumb-2 16-bit instruction encodings, APSR condition flags, and AAPCS calling conventions.
- **Arm Cortex-M4 Technical Reference Manual:**
  - Arm Limited. *Cortex-M4 Technical Reference Manual* (Revision r0p1).
  - URL: [https://developer.arm.com/documentation/100166/latest/](https://developer.arm.com/documentation/100166/latest/)
- **Computer Organization and Design (ARM Edition):**
  - Patterson, D. A., & Hennessy, J. L. (2016). *Computer Organization and Design ARM Edition: The Hardware Software Interface*. Morgan Kaufmann / Elsevier. ISBN: 978-0128017333.
  - Covers fixed-point arithmetic, cache geometry, AMAT formulas, and ALU hardware design.

## 3. Microcontroller Datasheets & Power Characteristics
- **STMicroelectronics STM32L476xx Datasheet:**
  - STMicroelectronics. (2018). *STM32L476xx Ultra-low-power Arm Cortex-M4 32-bit MCU+FPU, 100DMIPS, up to 1MB Flash, 128KB SRAM* (DocID025976 Rev 5).
  - Datasheet URL: [https://www.st.com/resource/en/datasheet/stm32l476rg.pdf](https://www.st.com/resource/en/datasheet/stm32l476rg.pdf)
  - Section 6.3.5: Supply current characteristics (Table 34: Run Mode current; Table 39: Stop 2 mode current).
  - *Current Status: Marked as PLACEHOLDER in `config/energy_params.yaml` pending student syllabus confirmation.*

## 4. Software Libraries & Simulation Tooling
- **Unicorn CPU Emulator:**
  - Nguyen, A. Q., & Dang, V. (2015). *Unicorn: Next-Generation CPU Emulator Framework*. Black Hat USA 2015.
  - Official Website: [https://www.unicorn-engine.org/](https://www.unicorn-engine.org/)
  - GitHub: [https://github.com/unicorn-engine/unicorn](https://github.com/unicorn-engine/unicorn)
- **WFDB Python Package:**
  - Goldberger, A., Amaral, L., Glass, L., Hausdorff, J., Ivanov, P. C., Mark, R., ... & Stanley, H. E. (2000). *PhysioBank, PhysioToolkit, and PhysioNet: Components of a new research resource for complex physiologic signals*. Circulation, 101(23), e215-e220.
  - Official Documentation: [https://wfdb.readthedocs.io/](https://wfdb.readthedocs.io/)
- **FastAPI Framework:**
  - Tiangolo, S. (2018). *FastAPI framework, high performance, easy to learn, fast to code, ready for production*.
  - Documentation URL: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
