# Medi-Match

A WPF desktop frontend (.NET Framework 4.7.2) that integrates with a Python-based scheduling engine to assign patients to doctors and beds using deterministic decision techniques).

## Overview
This project demonstrates a hospital scheduling workflow where a WPF UI prepares scheduling inputs and launches a Python scheduler located at `Backend/PythonScripts/scheduler.py`. The scheduler performs fuzzy scoring, rule-based specialty matching, and heuristic assignment to produce assignment results and metrics.

## Key Features
- WPF-based UI (`MainWindow`, `LandingWindow`, `AboutWindow`) to prepare and run schedules.  
- Python scheduler that:
  - Normalizes urgency using fuzzy scoring
  - Matches patient diseases to specialties via rules
  - Uses a weighted heuristic scoring function and greedy assignment with simple load balancing
  - Emits `Results/output.json` and `Results/metrics.csv`; optionally creates `Results/convergence.png` if `matplotlib` is installed
- Integration contract: UI waits for exact success line printed by the scheduler:  
  `SUCCESS — ALL FILES SAVED!`

## Architecture & File Contract
- Frontend: WPF (.NET Framework 4.7.2). The UI creates `Backend/PythonScripts/input.json`, launches the Python process, and reads `Results/output.json`.
- Backend: `Backend/PythonScripts/scheduler.py`:
  - Reads `input.json` from the same folder as the script.
  - Writes results into the `Results` folder at the project root.
- Important files:
  - `Backend/PythonScripts/scheduler.py` — scheduler engine
  - `Backend/PythonScripts/input.json` — input contract (created by UI or manual test)
  - `Results/output.json` — scheduling result consumed by UI
  - `Results/metrics.csv` — run statistics
  - `Results/convergence.png` — optional visualization

## AI Techniques & Algorithms Used
This project does NOT use machine learning or deep learning. It uses deterministic decision techniques:

1. Fuzzy logic (soft scoring)  
   - `calculate_fuzzy_score` in `scheduler.py` — normalizes urgency (1..10) into a fuzzy score.

2. Rule-based / expert system  
   - `SPECIALTY_CONDITIONS` in `scheduler.py` — explicit disease → specialty rules and referral logic.

3. Heuristic multi-criteria scoring + greedy assignment  
   - Per-patient scoring function (perfect-match bonus + load balancing + urgency weight) and greedy assignment using `doctor_patient_count`.

These are deterministic, interpretable methods (no model training, no inference frameworks).

## Requirements
- Visual Studio 2022  
- .NET Framework 4.7.2 (project target)  
- Python 3.8+ (ensure `python` or `python3` is on PATH)  
- Python packages: `numpy`; `matplotlib` optional for the convergence chart

Install Python packages:
pip install numpy matplotlib

If you don’t want the chart, `numpy` alone is sufficient:
pip install numpy


## Run / Debug Instructions

From Visual Studio:
1. Open solution in Visual Studio 2022.
2. Ensure WPF project is startup project.
3. Build via __Build > Build Solution__.
4. Start app via __Debug > Start Debugging__ or __Debug > Start Without Debugging__.
5. Use the UI action to run scheduling — the UI will write `Backend/PythonScripts/input.json`, run the scheduler, then read `Results/output.json`.

Run the scheduler manually (for testing):
cd Backend/PythonScripts python scheduler.py


The UI expects the scheduler to print the exact completion string:
`SUCCESS — ALL FILES SAVED!`

## Sample `input.json`
Place this in `Backend/PythonScripts/input.json` for manual testing or let the UI generate it:

Backend/PythonScripts/input.json { "Doctors": 3, "Patients": 6, "Beds": 4, "Urgency": [7, 4, 9, 3, 6, 8], "DoctorDetails": [ {"Name": "Dr. Ali", "Specialty": "Cardiology"}, {"Name": "Dr. Fahad", "Specialty": "Neurology"}, {"Name": "Dr. Amna", "Specialty": "Pediatrics"} ], "PatientDetails": [ {"Name": "Sara", "Disease": "Heart Attack", "Age": 63}, {"Name": "Anfal", "Disease": "Migraine", "Age": 28}, {"Name": "Sidra", "Disease": "Fever", "Age": 2}, {"Name": "Fatima", "Disease": "Fracture", "Age": 40}, {"Name": "Umer", "Disease": "Hypertension", "Age": 70}, {"Name": "Saad", "Disease": "Asthma", "Age": 12} ] }


## Troubleshooting
- "Could not read input.json": ensure `input.json` exists next to `scheduler.py` in `Backend/PythonScripts`.
- Missing Python packages: run `pip install numpy matplotlib`.
- UI never shows success: run `scheduler.py` manually to inspect stderr/stdout; the scheduler prints debug messages and the final success line.
- Permission/IO issues: ensure the app and Python have write access to the project `Results` folder.
