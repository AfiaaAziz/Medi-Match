import json
import os
import random
import math
import numpy as np
import matplotlib.pyplot as plt
import sys

"""
Simple GA-based scheduler for hospital patient -> doctor assignment.
This module exposes run_ga(input_data, results_folder) which returns the schedule list
and writes output.json, convergence.png, metrics.csv similar to scheduler.py expectations.

Representation: individual is a list of length N_patients, each gene is doctor index (0..doctors-1) or -1 for referral.
Fitness: maximize specialty match and urgency handling, minimize load imbalance and referrals when avoidable.
"""


def fitness_fn(individual, patient_details, doctor_details, urgency_list, specialties_db, doctors):
    # compute fitness where higher is better
    score = 0.0
    doctor_load = [0] * doctors

    for i, assign in enumerate(individual):
        urgency = urgency_list[i]
        patient = patient_details[i] if i < len(patient_details) else {"Name": f"Patient {i+1}", "Disease": "Fever"}
        disease = patient.get("Disease", "Fever")

        if assign is None or assign < 0 or assign >= doctors:
            # referral: small penalty unless no matching doctor exists
            # check if disease exists in specialties_db
            disease_exists = any(disease in conds for conds in specialties_db.values())
            if disease_exists:
                score -= 20 * (urgency / 10.0)  # penalize referrals more for high urgency
            else:
                # no doctor possible -> small penalty
                score -= 5
            continue

        # assigned to a real doctor
        doctor_load[assign] += 1
        doc = doctor_details[assign] if assign < len(doctor_details) else {"Name": f"Dr. {assign+1}", "Specialty": "General"}
        doc_spec = doc.get("Specialty", "General")

        # specialty match bonus
        if doc_spec in specialties_db and disease in specialties_db[doc_spec]:
            score += 50  # big reward for perfect match
        else:
            # small reward if generalist
            if doc_spec == "General":
                score += 5
            else:
                # penalize mismatch proportional to urgency
                score -= 15 * (urgency / 10.0)

        # urgency handling: reward assigning high urgency to less-loaded or more-senior doctors
        # we approximate seniority by doctor index (lower index -> more senior)
        seniority_bonus = max(0, (3 - assign)) * (urgency / 10.0) * 5
        score += seniority_bonus

    # load balance penalty (high variance is bad)
    if doctors > 0:
        mean_load = sum(doctor_load) / doctors
        variance = sum((l - mean_load) ** 2 for l in doctor_load) / doctors
        score -= variance * 2.0

    return score


def random_individual(patients, doctors):
    # random assignment with some referrals allowed
    ind = []
    for i in range(patients):
        if random.random() < 0.08:
            ind.append(-1)
        else:
            ind.append(random.randrange(0, doctors))
    return ind


def mutate(ind, doctors, mutation_rate=0.05):
    for i in range(len(ind)):
        if random.random() < mutation_rate:
            if random.random() < 0.08:
                ind[i] = -1
            else:
                ind[i] = random.randrange(0, doctors)


def crossover(a, b):
    # two-point crossover
    n = len(a)
    if n < 2:
        return a[:], b[:]
    i = random.randrange(0, n)
    j = random.randrange(i, n)
    child1 = a[:i] + b[i:j] + a[j:]
    child2 = b[:i] + a[i:j] + b[j:]
    return child1, child2


def run_ga(input_data, results_folder, population_size=80, generations=120, mutation_rate=0.06, seed=None):
    # seed RNGs when requested for reproducible runs
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    doctors = int(input_data.get("Doctors", 3))
    patients = int(input_data.get("Patients", 6))
    beds = int(input_data.get("Beds", 4))
    urgency_list = [int(x) for x in input_data.get("Urgency", [5]*patients)]
    doctor_details = input_data.get("DoctorDetails", [])
    patient_details = input_data.get("PatientDetails", [])

    # speciality db (same as scheduler.py)
    SPECIALTY_CONDITIONS = {
        "Cardiology": ["Heart Attack", "Stroke", "Hypertension"],
        "Neurology": ["Stroke", "Migraine", "Epilepsy"],
        "Orthopedics": ["Fracture", "Broken Arm", "Arthritis"],
        "Pediatrics": ["Fever", "Infection", "Asthma"],
        "General": ["Fever", "Cold", "Infection", "Diabetes"],
        "Emergency": ["Heart Attack", "Stroke", "Fracture"]
    }

    # initialize population
    population = [random_individual(patients, doctors) for _ in range(population_size)]

    # seed with some heuristic-based individuals (greedy assignment)
    def heuristic_seed():
        ind = [-1] * patients
        doctor_load = [0] * doctors
        for i in range(patients):
            disease = patient_details[i].get("Disease", "Fever") if i < len(patient_details) else "Fever"
            best_doc = -1
            for d in range(doctors):
                doc_spec = doctor_details[d].get("Specialty", "General") if d < len(doctor_details) else "General"
                if doc_spec in SPECIALTY_CONDITIONS and disease in SPECIALTY_CONDITIONS[doc_spec]:
                    best_doc = d
                    break
            if best_doc >= 0:
                ind[i] = best_doc
                doctor_load[best_doc] += 1
            else:
                ind[i] = -1
        return ind

    for _ in range(min(6, population_size)):
        population.append(heuristic_seed())

    # evaluate
    fitnesses = [fitness_fn(ind, patient_details, doctor_details, urgency_list, SPECIALTY_CONDITIONS, doctors) for ind in population]

    best_fitness_history = []
    best_individual = None
    best_fit = -1e9

    for gen in range(generations):
        # selection (tournament)
        new_pop = []
        elites = sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)[:max(1, int(0.05 * population_size))]
        # keep elites
        for f, ind in elites:
            new_pop.append(ind[:])
            if f > best_fit:
                best_fit = f
                best_individual = ind[:]

        while len(new_pop) < population_size:
            # tournament
            contenders = random.sample(list(zip(fitnesses, population)), k=min(4, len(population)))
            parent_a = max(contenders, key=lambda x: x[0])[1]
            contenders = random.sample(list(zip(fitnesses, population)), k=min(4, len(population)))
            parent_b = max(contenders, key=lambda x: x[0])[1]

            # crossover
            child1, child2 = crossover(parent_a, parent_b)

            # mutate using provided mutation_rate
            mutate(child1, doctors, mutation_rate=mutation_rate)
            mutate(child2, doctors, mutation_rate=mutation_rate)

            new_pop.append(child1)
            if len(new_pop) < population_size:
                new_pop.append(child2)

        population = new_pop
        fitnesses = [fitness_fn(ind, patient_details, doctor_details, urgency_list, SPECIALTY_CONDITIONS, doctors) for ind in population]

        gen_best = max(fitnesses)
        best_fitness_history.append(gen_best)

        # simple early stopping
        if gen > 10 and abs(best_fitness_history[-1] - best_fitness_history[-2]) < 1e-6:
            break

    # build schedule from best_individual
    schedule = []
    if best_individual is None:
        best_individual = population[0]

    for i, assign in enumerate(best_individual):
        patient = patient_details[i] if i < len(patient_details) else {"Name": f"Patient {i+1}", "Disease": "Fever"}
        disease = patient.get("Disease", "Fever")
        if assign is None or assign < 0:
            schedule.append({
                "Patient": i+1,
                "PatientName": patient.get("Name", f"Patient {i+1}"),
                "Disease": disease,
                "Doctor": "-",
                "DoctorName": "Referral needed",
                "Specialty": "N/A",
                "SpecialtyMatch": "Referral",
                "Urgency": urgency_list[i] if i < len(urgency_list) else 5,
                "FuzzyScore": round(min(max((urgency_list[i]-1)/9.0, 0.0),1.0), 3) if i < len(urgency_list) else 0.5,
                "Bed": (i % beds) + 1 if beds > 0 else 1
            })
        else:
            doc = doctor_details[assign] if assign < len(doctor_details) else {"Name": f"Dr. {assign+1}", "Specialty": "General"}
            doc_spec = doc.get("Specialty", "General")
            match = "Perfect Match" if doc_spec in SPECIALTY_CONDITIONS and disease in SPECIALTY_CONDITIONS[doc_spec] else ("Generalist" if doc_spec=="General" else "Partial/No Match")
            schedule.append({
                "Patient": i+1,
                "PatientName": patient.get("Name", f"Patient {i+1}"),
                "Disease": disease,
                "Doctor": assign+1,
                "DoctorName": doc.get("Name", f"Dr. {assign+1}"),
                "Specialty": doc_spec,
                "SpecialtyMatch": match,
                "Urgency": urgency_list[i] if i < len(urgency_list) else 5,
                "FuzzyScore": round(min(max((urgency_list[i]-1)/9.0, 0.0),1.0), 3) if i < len(urgency_list) else 0.5,
                "Bed": (i % beds) + 1 if beds > 0 else 1
            })

    # save output
    output_json = os.path.join(results_folder, "output.json")
    with open(output_json, "w") as f:
        json.dump(schedule, f, indent=2)

    # plot convergence
    try:
        plt.figure(figsize=(8,4))
        plt.plot(range(1, len(best_fitness_history)+1), best_fitness_history, '-o')
        plt.title('GA Convergence')
        plt.xlabel('Generation')
        plt.ylabel('Best Fitness')
        plt.grid(True, alpha=0.3)
        conv_path = os.path.join(results_folder, 'convergence.png')
        plt.savefig(conv_path, dpi=150, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"DEBUG: Could not save GA convergence plot: {e}", file=sys.stderr)

    # save metrics
    metrics_file = os.path.join(results_folder, "metrics.csv")
    perfect_matches = sum(1 for item in schedule if item["SpecialtyMatch"] == "Perfect Match")
    referral_needed = sum(1 for item in schedule if item["SpecialtyMatch"] == "Referral")
    no_matches = sum(1 for item in schedule if item["SpecialtyMatch"] in ["Partial/No Match", "Referral"])
    no_doctor_assigned = sum(1 for item in schedule if item["Doctor"] == "-")

    try:
        with open(metrics_file, 'w') as f:
            f.write('Metric,Value\n')
            f.write('AI Technique,Genetic Algorithm (GA)\n')
            f.write('Status,Success\n')
            f.write(f'Total Doctors,{doctors}\n')
            f.write(f'Total Patients,{patients}\n')
            f.write(f'Total Beds,{beds}\n')
            f.write(f'Perfect Specialty Matches,{perfect_matches}\n')
            f.write(f'Referrals Needed,{referral_needed}\n')
            f.write(f'No Matches,{no_matches}\n')
            f.write(f'Patients without Doctor Assignment,{no_doctor_assigned}\n')
            f.write(f'Match Success Rate,{round((perfect_matches/patients)*100 if patients>0 else 0, 1)}%\n')
            f.write(f'Average Urgency,{round(sum(urgency_list)/len(urgency_list), 2) if len(urgency_list)>0 else 0}\n')
            f.write(f'Best Fitness,{round(max(best_fitness_history) if best_fitness_history else 0, 3)}\n')
            f.write(f'Generations Ran,{len(best_fitness_history)}\n')
    except Exception as e:
        print(f"DEBUG: Could not write GA metrics: {e}", file=sys.stderr)

    return schedule


if __name__ == '__main__':
    # allow standalone testing
    cur = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(cur, 'input.json')
    if not os.path.exists(input_file):
        print('No input.json found for GA test')
        sys.exit(0)
    with open(input_file) as f:
        data = json.load(f)
    run_ga(data, os.path.join(os.path.dirname(cur), 'Results'))
