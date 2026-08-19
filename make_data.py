import numpy as np
import pandas as pd

np.random.seed(42)

courses = {
    "DATA_SCI": {
        "name": "Data Science с нуля",
        "modules": 6,
        "cohorts": ["DS-01 (Январь)", "DS-02 (Март)", "DS-03 (Май)"],
    },
    "PY_DEV": {
        "name": "Python-разработчик",
        "modules": 6,
        "cohorts": ["PY-05 (Февраль)", "PY-06 (Апрель)", "PY-07 (Июнь)"],
    },
    "PROD_MGMT": {
        "name": "Управление продуктом",
        "modules": 4,
        "cohorts": ["PM-10 (Январь)", "PM-11 (Апрель)"],
    },
}

sample_comments = {
    "positive": [
        "Всё отлично, материал структурирован.",
        "Очень понравилась практика на реальных данных!",
        "Лектор круто объясняет сложные алгоритмы.",
        "Супер модуль, всё разложилось по полочкам.",
    ],
    "pacing": [
        "Не успевал за дедлайнами, слишком много информации.",
        "Очень плотный график, нужно больше времени на ДЗ.",
        "Хотелось бы чуть больше времени на закрепление материала.",
    ],
    "cohesion": [
        "Сложно связать теорию 2-го урока с практическим заданием.",
        "В ДЗ требуют то, чего не было в лекциях.",
        "Каша в голове после 3-го урока, не хватило сквозного примера.",
    ],
    "energy": [
        "Сильно устал под конец модуля, еле сдал.",
        "Выгораю, совмещать с работой очень тяжело.",
        "Нужен небольшой перерыв перед следующим блоком.",
    ],
    "legacy": [
        "Звук на вебинаре хрипел.",
        "Тьютор проверял ДЗ более 4 дней.",
        "Плеер периодически зависает на мобильном.",
    ],
}

rows = []

for c_key, c_info in courses.items():
  for cohort in c_info["cohorts"]:
    num_students = 100
    student_ids = [
        f"{c_key[:3]}_{cohort.split()[0]}_{i:03d}"
        for i in range(1, num_students + 1)
    ]

    for mod_num in range(1, c_info["modules"] + 1):
      mod_id = f"MOD_{mod_num:02d}"
      difficulty_bias = 0.15 if mod_num in [3, 4] else 0.0
      fatigue_bias = 0.05 * mod_num

      for s_id in student_ids:
        # Pacing
        p_rushed = min(0.6, 0.15 + difficulty_bias + np.random.uniform(0, 0.08))
        p_slow = 0.10
        p_opt = max(0.2, 1.0 - p_rushed - p_slow)
        pacing = np.random.choice(
            ["rushed", "optimal", "slow"], p=[p_rushed, p_opt, p_slow]
        )

        # Cohesion
        p_frag = min(0.4, 0.08 + difficulty_bias + np.random.uniform(0, 0.06))
        p_conf = min(0.5, 0.20 + difficulty_bias)
        p_clear = max(0.2, 1.0 - p_frag - p_conf)
        cohesion = np.random.choice(
            ["clear", "confused", "fragmented"], p=[p_clear, p_conf, p_frag]
        )

        # Energy
        p_dep = min(
            0.55,
            0.10
            + fatigue_bias * 0.05
            + (0.15 if pacing == "rushed" else 0.0)
            + (0.10 if cohesion == "fragmented" else 0.0),
        )
        p_mod = 0.40
        p_high = max(0.1, 1.0 - p_dep - p_mod)
        energy = np.random.choice(
            ["high", "moderate", "depleted"], p=[p_high, p_mod, p_dep]
        )

        # Legacy ratings (1-5)
        base = (
            4.4
            - (0.6 if pacing == "rushed" else 0)
            - (0.8 if cohesion == "fragmented" else 0)
        )

        def gen_score(b_val):
          weights = [
              max(0.01, 1.0 - b_val / 2),
              max(0.02, 1.5 - b_val / 2.5),
              max(0.05, 2.0 - b_val / 3),
              max(0.1, b_val / 5),
              max(0.15, (b_val / 5) ** 2),
          ]
          w = np.array(weights)
          return int(np.random.choice([1, 2, 3, 4, 5], p=w / w.sum()))

        score_spk = gen_score(base + np.random.normal(0.2, 0.3))
        score_hw = gen_score(base - (0.3 if cohesion != "clear" else 0))
        score_plt = gen_score(4.5 + np.random.normal(0, 0.2))
        score_sup = gen_score(4.3 + np.random.normal(0, 0.3))

        # Verbatim
        comment = ""
        if np.random.rand() < 0.25:
          if energy == "depleted":
            comment = np.random.choice(sample_comments["energy"])
          elif pacing == "rushed":
            comment = np.random.choice(sample_comments["pacing"])
          elif cohesion == "fragmented":
            comment = np.random.choice(sample_comments["cohesion"])
          elif score_spk <= 2 or score_hw <= 2:
            comment = np.random.choice(sample_comments["legacy"])
          else:
            comment = np.random.choice(sample_comments["positive"])

        rows.append({
            "course_key": c_key,
            "course_name": c_info["name"],
            "cohort": cohort,
            "student_id": s_id,
            "module_id": mod_id,
            "pacing_score": pacing,
            "cohesion_score": cohesion,
            "energy_score": energy,
            "legacy_speaker": score_spk,
            "legacy_hw": score_hw,
            "legacy_platform": score_plt,
            "legacy_support": score_sup,
            "open_feedback": comment,
        })

df = pd.DataFrame(rows)
df.to_csv("pulse_multi_course_data.csv", index=False, encoding="utf-8-sig")
print(f"Датасет успешно создан: {len(df)} записей.")
