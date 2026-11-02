# Project Dimension Mapping Table (DRAFT)

**Student:** Samuel Rohlupuia  
**Course:** Computer Organization and Architecture (COA)  
**Mini-Project:** Wearable Health-Monitoring ARM System  
**Dimensions Assigned:** **CT + RWE**  

> [!IMPORTANT]
> **Instructions for Samuel:** The exact course acronym definitions have not been invented or guessed. Please paste the official definitions of dimensions **CT** and **RWE** from your course evaluation rubric. Review the proposed mapping of how this system demonstrates both dimensions.

---

| Dimension | Full Name | Official Rubric Description | How Demonstrated in Project | Primary Modules & Verification | Student Confirmation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **CT** | `[PASTE FROM SYLLABUS]` | `[PASTE FROM SYLLABUS]` | **Decomposition & Algorithmic Rigor:**<br>1. Decomposition of raw analog sensor voltages into discrete 12-bit ADC integer codes.<br>2. Fixed-point mathematical mapping into Q15 signed fractional domain.<br>3. Exact 16-bit Thumb instruction modeling with formal register and flag state transitions.<br>4. Analytical modeling of cache address bit fields (tag, index, offset) and AMAT calculations.<br>5. Duty-cycle mathematical formulation of average current draw. | `sim/q15.py`<br>`sim/alu.py`<br>`sim/cache.py`<br>`tests/test_q15.py`<br>`tests/test_cache.py` | [ ] Pending Confirmation |
| **RWE** | `[PASTE FROM SYLLABUS]` | `[PASTE FROM SYLLABUS]` | **Real-World Engineering Application:**<br>1. Processing real clinical PPG waveforms from the PhysioNet BIDMC PPG and Respiration Dataset.<br>2. Adhering to hardware-standard serial protocols: UART 8-N-1 at 115200 baud and I2C at 100/400 kHz.<br>3. Real ARM Thumb instruction execution using the Unicorn Engine.<br>4. Modeling real microcontroller low-power modes (Run vs Stop 2) using manufacturer datasheet figures (STM32L476RG).<br>5. Industry-grade REST API and CI test automation. | `sim/pipeline.py`<br>`sim/uart.py`<br>`sim/i2c.py`<br>`sim/energy.py`<br>`backend/api.py` | [ ] Pending Confirmation |
