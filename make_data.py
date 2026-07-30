import pandas as pd
import numpy as np

np.random.seed(42)

n_students = 200
student_ids = [f'STU_{1000 + i}' for i in range(1, n_students + 1)]
modules = [f'MOD_0{i}' for i in range(1, 7)]

data = []

for student in student_ids:
    student_resilience = np.random.choice(['high', 'medium', 'low'], p=[0.3, 0.5, 0.2])
    
    for mod_idx, mod in enumerate(modules):
        if mod in ['MOD_03', 'MOD_04']:
            pacing_p = [0.45, 0.50, 0.05] if student_resilience != 'low' else [0.65, 0.30, 0.05]
        else:
            pacing_p = [0.20, 0.75, 0.05]
            
        if mod in ['MOD_04', 'MOD_05']:
            cohesion_p = [0.60, 0.30, 0.10]
        else:
            cohesion_p = [0.80, 0.15, 0.05]
            
        if mod_idx >= 3:
            energy_p = [0.25, 0.45, 0.30] if student_resilience == 'low' else [0.40, 0.45, 0.15]
        else:
            energy_p = [0.65, 0.30, 0.05]
            
        pacing = np.random.choice(['rushed', 'optimal', 'slow'], p=pacing_p)
        cohesion = np.random.choice(['clear', 'confused', 'fragmented'], p=cohesion_p)
        energy = np.random.choice(['high', 'moderate', 'depleted'], p=energy_p)
        
        data.append({
            'student_id': student,
            'module_id': mod,
            'pacing_score': pacing,
            'cohesion_score': cohesion,
            'energy_score': energy
        })

df = pd.DataFrame(data)
df.to_csv('pulse_6_modules_clean.csv', index=False)
print("✅ Данные сгенерированы! Файл pulse_6_modules_clean.csv создан.")