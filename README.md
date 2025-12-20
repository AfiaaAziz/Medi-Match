## Medi-Match: AI-Driven Hospital Resource Optimization & Triage

Medi-Match is an advanced healthcare management platform that integrates a modern WPF (.NET) frontend with a powerful Python-based AI intelligence layer. The system solves the complex problem of hospital resource allocation and emergency patient prioritization using a combination of Evolutionary Computing, Fuzzy Logic, and Rule-Based Expert Systems.

## Group Members & IDs

Member 1 Afia Aziz - (ID: 231561 )

Member 2 Zumer Dhillun  - (ID: 231597 )

Member 3 Zoya Azad  - (ID: 231579 )

## Project Summary

In modern healthcare, manual scheduling of patients to specialists is inefficient and prone to human error. Medi-Match addresses this by automating the patient-to-doctor assignment process.

## Core Features:

AI Scheduler: Matches patients to doctors based on specialty, workload, and urgency.

Emergency Triage System: A clinical tool that assesses patient symptoms to calculate an urgency score (1-10) and recommends a specific specialist (e.g., Cardiologist for Chest Pain).

Optimization Engines: Offers two scheduling modes: a fast Heuristic Scheduler and a globally optimal Genetic Algorithm.

Data Visualization: Real-time generation of convergence graphs to track AI performance.

Professional Reporting: Automated HTML and Text clinical triage reports.

## AI Techniques Used & Justification
1. Fuzzy Logic (Urgency Normalization)

Implementation: The calculate_fuzzy_score function transforms discrete urgency levels (1-10) into a continuous fuzzy set [0,1].

Justification: Medical urgency is not binary. Fuzzy logic allows the system to handle the "shades of grey" in patient severity, ensuring smoother prioritization in the assignment matrix.

2. Genetic Algorithm (Evolutionary Optimization)

Implementation: Located in scheduler_ga.py. Uses Tournament Selection, Two-Point Crossover, and Mutation over 120 generations.

Justification: Hospital scheduling is an NP-Hard problem. GA explores the vast search space of possible combinations to find a global optimum that balances doctor utilization and specialty match quality.

3. Rule-Based Expert System (Clinical Mapping)

Implementation: Uses a comprehensive clinical knowledge base (SPECIALTY_CONDITIONS) to map diseases and symptoms to medical departments and specialists.

Justification: For medical safety, "Black Box" AI is dangerous. Rule-based systems provide transparent, auditable decision-making for specialist recommendations.

4. Heuristic Greedy Search

Implementation: A scoring-based heuristic that makes the locally optimal choice for rapid, real-time results when deep optimization is not required.

## Knowledge Representation
1. Semantic Network Diagram

The Semantic Network represents the ontological relationships between clinical symptoms, departments, and AI scheduling logic.

![alt text](Path/To/Your/semantic_network.png)


2. Frame-Based Representation

Frames are used to define the "Slots and Fillers" architecture of our medical entities (Patient, Doctor, Triage).

![alt text](Path/To/Your/frames_diagram.png)


## Setup & Run Instructions
Prerequisites

Visual Studio 2022 (with .NET Framework 4.7.2)

Python 3.8+ (Added to your System PATH)

# Required Python Libraries:
pip install numpy matplotlib

# Running the Project
1. Clone the Repository:
   
git clone https://github.com/YourUsername/Medi-Match.git

2. Open the Solution: Open the .sln file in Visual Studio.

3. Build: Clean and Rebuild the solution.

4. Run: Press F5 to launch the WPF application.

5. Operation:

- Navigate to Triage to assess an emergency patient and generate a report.

- Navigate to Scheduler to enter hospital resources and run the AI optimization.

- View the Graph page to see the AI's convergence performance.

## Project Structure

HospitalSchedulerUI/ - WPF Frontend source code (C# / XAML).

Backend/PythonScripts/ - AI Logic Engines:

scheduler.py: Main heuristic script.

scheduler_ga.py: Genetic Algorithm optimization.

triage_calculator.py: Emergency assessment logic.

Results/ - Output folder for output.json, metrics.csv, and convergence.png.

## Sample Result Contract

The system ensures reliability through a strict JSON contract.
Sample input.json:
{
  "Doctors": 3,
  "Patients": 5,
  "DoctorDetails": [
    { "Name": "Dr. Smith", "Specialty": "Cardiology" }
  ],
  "Urgency": [9, 4, 2, 8, 5]
}

## License

This project was developed as part of the Artificial Intelligence Course. Distributed for educational purposes.
