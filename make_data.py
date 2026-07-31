import pandas as pd
import numpy as np

np.random.seed(42)

n_students = 200
student_ids = [f'STU_{1000 + i}' for i in range(1, n_students + 1)]
modules = [f'MOD_0{i}' for i in range(1, 7)]

# Пул вербатимов (открытых текстов)
comments_pool = [
    "", "", "", "", "", "",  # Не все студенты оставляют комментарий
    "Очень понравился практический разбор в этом модуле!",
    "Слишком много теории, не успеваю за дедлайнами.",
    "Не хватило разбора типовых ошибок в домашнем задании.",
    "Спикер отлично объясняет сложные темы, спасибо!",
    "Трудные практические кейсы, долго разбирался с тренажером.",
    "Платформа иногда зависала при отправке решений.",
    "Тьютор оперативно помог в чате, очень ценно."
]

data = []

for student in student_ids:
    student_resilience = np.random.choice(['high', 'medium', 'low'], p=[0.3, 0.5, 0.2])
    
    for mod_idx, mod in enumerate(modules):
        # 1. Core Pulse (3 вопроса)
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
        
        # 2. Legacy CSAT (5 вопросов по шкале 1-5)
        base_mean = 4.5 if student_resilience == 'high' else (4.1 if student_resilience == 'medium' else 3.6)
        if cohesion == 'fragmented':
            base_mean -= 0.7
            
        legacy_speaker = int(np.clip(np.random.normal(base_mean, 0.6), 1, 5))
        legacy_platform = int(np.clip(np.random.normal(4.3, 0.6), 1, 5))
        legacy_homework = int(np.clip(np.random.normal(base_mean - 0.2, 0.8), 1, 5))
        legacy_materials = int(np.clip(np.random.normal(base_mean, 0.6), 1, 5))
        legacy_support = int(np.clip(np.random.normal(4.4, 0.7), 1, 5))
        
        # 3. Open Feedback (Открытый вопрос)
        open_text = np.random.choice(comments_pool)
        
        data.append({
            'student_id': student,
            'module_id': mod,
            'pacing_score': pacing,
            'cohesion_score': cohesion,
            'energy_score': energy,
            'legacy_speaker': legacy_speaker,
            'legacy_platform': legacy_platform,
            'legacy_homework': legacy_homework,
            'legacy_materials': legacy_materials,
            'legacy_support': legacy_support,
            'open_feedback_text': open_text
        })

df = pd.DataFrame(data)
df.to_csv('pulse_6_modules_clean.csv', index=False)
print("✅ Данные сгенерированы! Файл pulse_6_modules_clean.csv обновлен.")
