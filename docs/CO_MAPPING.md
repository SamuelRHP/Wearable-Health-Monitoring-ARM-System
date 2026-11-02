# Course Outcomes (CO) Mapping Table (DRAFT)

**Student:** Samuel Rohlupuia  
**Course:** Computer Organization and Architecture (COA)  
**Project Title:** Wearable Health-Monitoring ARM System  

> [!IMPORTANT]
> **Instructions for Samuel:** In accordance with the project constraints, the description column below has not been guessed. Please copy and paste the exact text for Course Outcomes CO1 through CO6 from your university course syllabus. Review and confirm the proposed "Where Demonstrated" columns.

---

| Course Outcome | Official Syllabus Description | COA Concept Demonstrated | Implementation Module | Automated Test File | Proposed UI Tab (Frontend) | Student Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CO1** | `[PASTE FROM SYLLABUS]` | **Data Representation & Computer Arithmetic:** Fixed-point representation (Q15 / 1.15), two's complement arithmetic, 12-bit ADC quantization, saturating addition, and quantization error analysis. | `sim/q15.py` | `tests/test_q15.py` | *Tab 1: Number Representation* | [ ] Pending Confirmation |
| **CO2** | `[PASTE FROM SYLLABUS]` | **Arithmetic Logic Unit (ALU):** 32-bit ALU data path, condition flag generation ($N, Z, C, V$ in APSR), and condition evaluation driving branches (`CMP bpm, threshold` $\to$ `BGT`). | `sim/alu.py` | `tests/test_alu.py` | *Tab 2: ALU & Decision Logic* | [ ] Pending Confirmation |
| **CO3** | `[PASTE FROM SYLLABUS]` | **Instruction Set Architecture (ISA):** ARM Cortex-M Thumb-1/Thumb-2 instruction execution, register bank ($R0-R7$), program counter, machine code encoding, and hardware emulation. | `asm/moving_average.s`, `sim/arm_routine.py` | `tests/test_arm_routine.py` | *Tab 3: ARM Core & Registers* | [ ] Pending Confirmation |
| **CO4** | `[PASTE FROM SYLLABUS]` | **Memory Hierarchy & Caching:** Direct-mapped and set-associative cache design, spatial/temporal locality, 32-bit address decoding (tag/index/offset), and Average Memory Access Time (AMAT). | `sim/cache.py` | `tests/test_cache.py` | *Tab 4: Cache Hierarchy* | [ ] Pending Confirmation |
| **CO5** | `[PASTE FROM SYLLABUS]` | **Input/Output Organization & Serial Interconnects:** Bus timing, framing overhead, transmission latency, and bandwidth utilization on UART (8-N-1 telemetry) and I2C (synchronous sensor read). | `sim/uart.py`, `sim/i2c.py` | `tests/test_uart.py`, `tests/test_i2c.py` | *Tab 5: Serial Interconnects* | [ ] Pending Confirmation |
| **CO6** | `[PASTE FROM SYLLABUS]` | **Power-Aware Architecture & System Integration:** End-to-end physiological signal chain, processor duty-cycling, active vs sleep current modes, and energy optimization. | `sim/energy.py`, `sim/pipeline.py`, `sim/run.py` | `tests/test_energy.py`, `tests/test_pipeline.py` | *Tab 6: System Energy & Overview* | [ ] Pending Confirmation |
