# Frontend Application (Stub)

This folder is reserved for the interactive web frontend dashboard, to be created in a subsequent development phase.

## Architecture & Integration
- **Static File Serving:** When HTML/JS/CSS assets are built in this folder, the FastAPI backend in `backend/api.py` automatically mounts and serves them at the root URL: `http://localhost:8000/`.
- **API Contract:** The frontend will communicate directly with the REST endpoints documented in `docs/API.md`:
  - `GET /api/defaults`
  - `GET /api/records`
  - `POST /api/run`
  - `GET /api/verification`
- **Planned UI Dashboard Tabs:**
  1. *Tab 1: Number Representation* (12-bit ADC $\to$ Q15 fixed-point)
  2. *Tab 2: ALU & Decision Logic* (32-bit ALU status flags & alert branching)
  3. *Tab 3: ARM Core & Registers* (Thumb instruction stepping, R0-R7, Unicorn trace)
  4. *Tab 4: Cache Hierarchy* (Direct-mapped / set-associative address decomposition & AMAT)
  5. *Tab 5: Serial Interconnects* (UART 115200 baud & I2C 100/400 kHz bus utilisation)
  6. *Tab 6: System Energy & Overview* (Duty-cycle current draw, sleep modes, and datasheet savings)
