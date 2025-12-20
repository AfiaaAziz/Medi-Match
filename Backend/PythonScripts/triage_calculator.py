import json
import sys
import os
import datetime

def calculate_urgency(symptoms, age, pain_level):
    """
    AI Rule-Based Urgency Calculator
    Returns urgency score 1-10
    """
    score = 0
    
    # Symptom weights (higher = more urgent)
    weights = {
        "chest_pain": 9,
        "difficulty_breathing": 8,
        "severe_bleeding": 9,
        "high_fever": 4,
        "head_injury": 7,
        "broken_bone": 6,
        "abdominal_pain": 5,
        "dizziness": 3,
        "unconscious": 10,
        "severe_burn": 8
    }
    
    # Add symptom scores
    for symptom in symptoms:
        score += weights.get(symptom, 2)
    
    # Age factor (extremes get higher score)
    if age < 5 or age > 65:
        score += 3
    elif age < 12 or age > 50:
        score += 1
    
    # Pain level (pain/2 added to score)
    score += pain_level / 2
    
    # Cap at 10, minimum 1
    score = min(10, max(1, score))
    
    return round(score, 1)

def get_priority(urgency_score):
    """Convert score to priority level"""
    if urgency_score >= 8:
        return "CRITICAL", "GO TO EMERGENCY ROOM NOW", "Emergency", "Immediate"
    elif urgency_score >= 6:
        return "HIGH", "Urgent Care Required Today", "Urgent", "Within 2 hours"
    elif urgency_score >= 4:
        return "MEDIUM", "Schedule Urgent Appointment", "Semi-Urgent", "4-6 hours"
    else:
        return "LOW", "Schedule Routine Appointment", "Routine", "24-48 hours"

def get_department(symptoms):
    """Determine department based on symptoms"""
    if "chest_pain" in symptoms or "difficulty_breathing" in symptoms:
        return "Cardiology"
    elif "head_injury" in symptoms or "unconscious" in symptoms:
        return "Neurology"
    elif "broken_bone" in symptoms:
        return "Orthopedics"
    elif "abdominal_pain" in symptoms:
        return "Gastroenterology"
    elif "severe_burn" in symptoms:
        return "Burn Unit"
    elif "high_fever" in symptoms:
        return "General Medicine"
    else:
        return "Emergency Department"
# Add this function above main()
def get_specialist(symptoms):
    """Recommend a specific specialist based on symptoms"""
    if "chest_pain" in symptoms:
        return "Cardiologist (Heart Specialist)"
    elif "difficulty_breathing" in symptoms:
        return "Pulmonologist (Lung Specialist)"
    elif "head_injury" in symptoms or "unconscious" in symptoms or "dizziness" in symptoms:
        return "Neurologist (Brain & Nerve Specialist)"
    elif "broken_bone" in symptoms:
        return "Orthopedic Surgeon (Bone Specialist)"
    elif "abdominal_pain" in symptoms:
        return "Gastroenterologist (Digestive Specialist)"
    elif "severe_burn" in symptoms:
        return "Burn Specialist / Plastic Surgeon"
    elif "severe_bleeding" in symptoms:
        return "Trauma Surgeon"
    elif "high_fever" in symptoms:
        return "Infectious Disease Specialist"
    else:
        return "General Practitioner"

# Inside main(), update the 'result' dictionary:
# Change the result block to include:
# "recommended_specialist": get_specialist(symptoms),
def main():
    if len(sys.argv) < 2:
        print('{"error": "No input file provided"}')
        return
    
    input_file = sys.argv[1]
    
    try:
        # Read patient data
        with open(input_file, 'r') as f:
            data = json.load(f)
        
        name = data.get('name', 'Unknown')
        age = data.get('age', 30)
        symptoms = data.get('symptoms', [])
        pain_level = data.get('pain_level', 5)
        
        # Calculate urgency
        urgency_score = calculate_urgency(symptoms, age, pain_level)
        
        # Get priority and action
        priority, action, dept_type, wait_time = get_priority(urgency_score)
        
        # Get department
        department = get_department(symptoms)
        
        # Main symptom for display
        main_symptom = symptoms[0].replace('_', ' ').title() if symptoms else "General"
        
       # Prepare result
        result = {
            "patient_name": name,
            "age": age,
            "symptoms": symptoms,
            "symptoms_count": len(symptoms),
            "main_symptom": main_symptom,
            "pain_level": pain_level,
            "urgency": urgency_score,
            "ai_score": round(urgency_score * 10, 1),
            "priority": priority,
            "action": action,
            "department": department,
            "recommended_specialist": get_specialist(symptoms), # ADD THIS LINE (No #)
            "dept_type": dept_type,
            "wait_time": wait_time,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "calculated"
        }
        # Print result for C#
        print(json.dumps(result))
        
        # Save to file
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(project_root, "triage_results.json")
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
            
        # Also save to PythonScripts folder for backup
        backup_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "triage_backup.json")
        with open(backup_file, 'w') as f:
            json.dump(result, f, indent=2)
            
    except Exception as e:
        error_result = {
            "error": str(e),
            "urgency": 5,
            "priority": "MEDIUM",
            "action": "See a doctor as soon as possible",
            "department": "General",
            "wait_time": "4-6 hours"
        }
        print(json.dumps(error_result))

if __name__ == "__main__":
    main()