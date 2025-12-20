import json
import os
import sys
import numpy as np

# GET THE EXACT FOLDER WHERE input.json IS
current_folder = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_folder, "input.json")

print(f"DEBUG: Looking for input.json at: {input_file}", file=sys.stderr)

# READ input.json
try:
    with open(input_file, "r") as f:
        data = json.load(f)
    print("DEBUG: Successfully read input.json", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Could not read input.json: {e}", file=sys.stderr)
    sys.exit(1)

# Extract data with fallbacks
doctors = int(data.get("Doctors", 3))
patients = int(data.get("Patients", 6))
beds = int(data.get("Beds", 4))
urgency_list = [int(x) for x in data.get("Urgency", [5,5,5,5,5,5])]

# Get doctor and patient details (optional)
doctor_details = data.get("DoctorDetails", [])
patient_details = data.get("PatientDetails", [])

# Fill missing details
while len(doctor_details) < doctors:
    doctor_details.append({"Name": f"Dr. {len(doctor_details)+1}", "Specialty": "General"})

while len(patient_details) < patients:
    patient_details.append({"Name": f"Patient {len(patient_details)+1}", "Disease": "Fever", "Age": 30})

print(f"DEBUG: Doctors={doctors}, Patients={patients}, Beds={beds}", file=sys.stderr)
print(f"DEBUG: Urgency list: {urgency_list}", file=sys.stderr)

# GO TO PROJECT ROOT TO SAVE RESULTS
project_root = os.path.dirname(os.path.dirname(current_folder))
results_folder = os.path.join(project_root, "Results")
os.makedirs(results_folder, exist_ok=True)

print(f"DEBUG: Results folder: {results_folder}", file=sys.stderr)

# Check input flag to decide whether to run GA
use_ga = False
try:
    use_ga = bool(data.get("UseGA", False))
except Exception:
    use_ga = False

if use_ga:
    try:
        import scheduler_ga
        # read GA hyperparameters if available
        pop = int(data.get('GAPopulation', 80))
        gens = int(data.get('GAGenerations', 120))
        mut = float(data.get('GAMutation', 0.06))
        seed = data.get('GASeed', None)

        # pass mutation rate through to GA so UI value takes effect
        ga_schedule = scheduler_ga.run_ga(data, results_folder, population_size=pop, generations=gens, mutation_rate=mut, seed=seed)
        if ga_schedule:
            # scheduler_ga handles saving outputs and metrics
            print("SUCCESS — ALL FILES SAVED!")
            sys.exit(0)
    except Exception as ge:
        print(f"DEBUG: GA run failed, falling back to heuristic scheduler: {ge}", file=sys.stderr)

# SIMPLE FUZZY LOGIC
def calculate_fuzzy_score(urgency):
    # Simple linear conversion: 1→0.1, 10→1.0
    return min(max((urgency - 1) / 9.0, 0.0), 1.0)

fuzzy_scores = [round(calculate_fuzzy_score(u), 3) for u in urgency_list]

# SPECIALTY MATCHING DATABASE
SPECIALTY_CONDITIONS = {
    "Cardiology": ["Heart Attack", "Stroke", "Hypertension"],
    "Neurology": ["Stroke", "Migraine", "Epilepsy"],
    "Orthopedics": ["Fracture", "Broken Arm", "Arthritis"],
    "Pediatrics": ["Fever", "Infection", "Asthma"],
    "General": ["Fever", "Cold", "Infection", "Diabetes"],
    "Emergency": ["Heart Attack", "Stroke", "Fracture"]
}

# SIMPLE SCHEDULING ALGORITHM
schedule = []
doctor_patient_count = [0] * doctors

for i in range(patients):
    patient = patient_details[i] if i < len(patient_details) else {"Name": f"Patient {i+1}", "Disease": "Fever"}
    patient_disease = patient.get("Disease", "Fever")
    
    # Find best doctor based on:
    # 1. Perfect specialty match only (no partial matches for assignment)
    # 2. Current load
    # 3. Urgency level
    
    best_doctor_idx = -1  # Initialize to -1 (no doctor)
    best_score = -1
    has_perfect_specialty_match = False
    required_specialty = None
    
    # First, check if the disease is in our specialty database
    disease_exists_in_system = False
    for specialty, conditions in SPECIALTY_CONDITIONS.items():
        if patient_disease in conditions:
            disease_exists_in_system = True
            required_specialty = specialty
            break
    
    # If disease is not in our system at all, no doctor can handle it
    if not disease_exists_in_system:
        schedule.append({
            "Patient": i + 1,
            "PatientName": patient.get("Name", f"Patient {i+1}"),
            "Disease": patient_disease,
            "Doctor": "-",
            "DoctorName": "No specialist available",
            "Specialty": "N/A",
            "SpecialtyMatch": "Disease not in system",
            "Urgency": urgency_list[i],
            "FuzzyScore": fuzzy_scores[i],
            "Bed": (i % beds) + 1 if beds > 0 else 1
        })
        continue
    
    # Look for a doctor with PERFECT specialty match
    for doc_idx in range(doctors):
        score = 0
        
        # Doctor info
        doctor = doctor_details[doc_idx] if doc_idx < len(doctor_details) else {"Name": f"Dr. {doc_idx+1}", "Specialty": "General"}
        doctor_specialty = doctor.get("Specialty", "General")
        
        # Check for PERFECT specialty match (doctor's specialty matches disease exactly)
        if doctor_specialty in SPECIALTY_CONDITIONS:
            if patient_disease in SPECIALTY_CONDITIONS[doctor_specialty]:
                # PERFECT MATCH - this doctor can treat this patient
                has_perfect_specialty_match = True
                
                # Start with perfect match bonus
                score += 40
                
                # 2. Load balancing (30 points max)
                current_load = doctor_patient_count[doc_idx]
                avg_load = patients / max(doctors, 1)
                if current_load < avg_load:
                    score += 30 * (1 - current_load/avg_load)
                
                # 3. Urgency matching (30 points max) - use fuzzy score (0..1) for smoother scaling
                f = fuzzy_scores[i] if i < len(fuzzy_scores) else min(max((urgency_list[i]-1)/9.0,0.0),1.0)
                if doc_idx == 0:  # Doctor 1 (most senior)
                    score += 30 * f
                elif doc_idx == 1:  # Doctor 2
                    score += 25 * f
                else:
                    score += 20 * f
                
                if score > best_score:
                    best_score = score
                    best_doctor_idx = doc_idx
    
    # Check if we found a perfect match doctor
    if has_perfect_specialty_match and best_doctor_idx != -1:
        # Assign patient to the best matching doctor
        doctor_patient_count[best_doctor_idx] += 1

        # Get doctor details
        doctor = doctor_details[best_doctor_idx] if best_doctor_idx < len(doctor_details) else {"Name": f"Dr. {best_doctor_idx+1}", "Specialty": "General"}

        schedule.append({
            "Patient": i + 1,
            "PatientName": patient.get("Name", f"Patient {i+1}"),
            "Disease": patient_disease,
            "Doctor": best_doctor_idx + 1,
            "DoctorName": doctor.get("Name", f"Dr. {best_doctor_idx+1}"),
            "Specialty": doctor.get("Specialty", "General"),
            "SpecialtyMatch": "Perfect Match",
            "Urgency": urgency_list[i],
            "FuzzyScore": fuzzy_scores[i],
            "Bed": (i % beds) + 1 if beds > 0 else 1
        })
        # record assignment (0-based index)
        assign_val = best_doctor_idx
    else:
        # No perfect match doctor found
        # Check if disease exists in system but no matching doctor
        if required_specialty:
            # Disease exists but no doctor with that specialty
            schedule.append({
                "Patient": i + 1,
                "PatientName": patient.get("Name", f"Patient {i+1}"),
                "Disease": patient_disease,
                "Doctor": "-",
                "DoctorName": "Referral needed",
                "Specialty": "N/A",
                "SpecialtyMatch": f"Refer to {required_specialty}",
                "Urgency": urgency_list[i],
                "FuzzyScore": fuzzy_scores[i],
                "Bed": (i % beds) + 1 if beds > 0 else 1
            })
        else:
            # Should not reach here due to earlier check, but just in case
            schedule.append({
                "Patient": i + 1,
                "PatientName": patient.get("Name", f"Patient {i+1}"),
                "Disease": patient_disease,
                "Doctor": "-",
                "DoctorName": "No specialist available",
                "Specialty": "N/A",
                "SpecialtyMatch": "No Match",
                "Urgency": urgency_list[i],
                "FuzzyScore": fuzzy_scores[i],
                "Bed": (i % beds) + 1 if beds > 0 else 1
            })
        assign_val = -1

    # append assignment to assignments list
    try:
        assignments.append(assign_val)
    except NameError:
        assignments = [assign_val]

# SAVE OUTPUT JSON
output_json = os.path.join(results_folder, "output.json")
with open(output_json, "w") as f:
    json.dump(schedule, f, indent=2)
print(f"DEBUG: Saved schedule to {output_json}", file=sys.stderr)

# CREATE REAL CONVERGENCE-LIKE GRAPH BASED ON ASSIGNMENT EVALUATION

# --- START OF GRAPH FIX ---
try:
    import matplotlib.pyplot as plt
    from datetime import datetime

    # 1. CALCULATE THE ACTUAL DATA FOR THE GRAPH
    per_patient_score = []
    # 'assignments' was created during the loop above
    assigns = assignments if 'assignments' in globals() else [-1] * len(schedule)
    
    for item in schedule:
        score = 0.0
        match_type = item.get('SpecialtyMatch', '')
        
        if match_type == 'Perfect Match':
            score = 1.0  # 100% quality for this patient
        elif 'Refer' in match_type:
            score = 0.3  # 30% quality (referral is okay but not ideal)
        else:
            score = 0.0  # 0% quality (no match)
            
        # Multiply by urgency so high urgency matches count for more
        urgency_weight = float(item.get('FuzzyScore', 0.5))
        per_patient_score.append(score * urgency_weight)

    # 2. CREATE THE RUNNING AVERAGE (The "Convergence" line)
    running_avg = []
    cumulative_sum = 0.0
    for idx, val in enumerate(per_patient_score, start=1):
        cumulative_sum += val
        # Calculate percentage: (actual / max possible) * 100
        running_avg.append((cumulative_sum / idx) * 100.0)

    # 3. PREPARE X and Y
    y = running_avg
    x = list(range(1, len(y) + 1))

    # 4. PLOT THE GRAPH
    plt.figure(figsize=(10, 6))
    
    # Add a timestamp to the title so you can prove it's new
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    plt.plot(x, y, color='#008080', linewidth=3, marker='o', markersize=8, label="Schedule Quality")
    plt.fill_between(x, y, color='#008080', alpha=0.1) # Makes it look professional

    plt.title(f'AI Optimization Quality over Time\n(Last Updated: {timestamp})', fontsize=14)
    plt.xlabel('Number of Patients Assigned')
    plt.ylabel('Match Success Rate (%)')
    plt.ylim(0, 105)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()

    # 5. SAVE THE FILE
    convergence_img = os.path.join(results_folder, 'convergence.png')
    
    # Ensure any old file is overwritten
    if os.path.exists(convergence_img):
        try:
            os.remove(convergence_img)
        except:
            pass

    plt.savefig(convergence_img, dpi=150)
    plt.close()

    print(f"DEBUG: Graph updated successfully at {timestamp}", file=sys.stderr)

except Exception as e:
    print(f"ERROR generating graph: {e}", file=sys.stderr)
# --- END OF GRAPH FIX ---

# CALCULATE STATISTICS
perfect_matches = sum(1 for item in schedule if item["SpecialtyMatch"] == "Perfect Match")
referral_needed = sum(1 for item in schedule if "Refer to" in item["SpecialtyMatch"])
no_matches = sum(1 for item in schedule if item["SpecialtyMatch"] in ["No Match", "Disease not in system"])
no_doctor_assigned = sum(1 for item in schedule if item["Doctor"] == "-")

# SAVE METRICS
metrics_file = os.path.join(results_folder, "metrics.csv")
with open(metrics_file, "w") as f:
    f.write("Metric,Value\n")
    f.write("AI Technique,Fuzzy Logic + Rule-Based Matching\n")
    f.write("Status,Success\n")
    f.write(f"Total Doctors,{doctors}\n")
    f.write(f"Total Patients,{patients}\n")
    f.write(f"Total Beds,{beds}\n")
    f.write(f"Perfect Specialty Matches,{perfect_matches}\n")
    f.write(f"Referrals Needed,{referral_needed}\n")
    f.write(f"No Matches,{no_matches}\n")
    f.write(f"Patients without Doctor Assignment,{no_doctor_assigned}\n")
    f.write(f"Match Success Rate,{round((perfect_matches/patients)*100, 1)}%\n")
    f.write(f"Average Urgency,{round(sum(urgency_list)/len(urgency_list), 2)}\n")
    f.write(f"Doctor Utilization,{round(sum(doctor_patient_count)/doctors, 1)} patients/doctor\n")

print(f"DEBUG: Saved metrics to {metrics_file}", file=sys.stderr)

# FINAL SUCCESS MESSAGE
print("=" * 50, file=sys.stderr)
print("SUCCESS: Hospital scheduling completed!", file=sys.stderr)
print(f"SUCCESS: {patients} patients processed", file=sys.stderr)
print(f"SUCCESS: {perfect_matches} perfect specialty matches (assigned to doctors)", file=sys.stderr)
print(f"SUCCESS: {referral_needed} patients need referral to other specialists", file=sys.stderr)
print(f"SUCCESS: {no_doctor_assigned} patients without direct doctor assignment", file=sys.stderr)
print("=" * 50, file=sys.stderr)

# IMPORTANT: This line is what C# looks for
print("SUCCESS — ALL FILES SAVED!")