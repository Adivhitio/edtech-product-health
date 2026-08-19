import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Дашборд: Пульс Модуля & Пилотный Эксперимент",
    page_icon="📊",
    layout="wide",
)


# Загрузка данных или генерация в памяти
@st.cache_data
def load_data():
  try:
    return pd.read_csv("pulse_multi_course_data.csv")
  except FileNotFoundError:
    np.random.seed(42)
    courses = {
        "DATA_ANALYTICS": {
            "name": "Аналитик данных (Upskill)",
            "modules": 5,
            "cohorts": ["DA-Pilot-01", "DA-Pilot-02", "DA-Pilot-03"],
        },
        "PROD_MGMT_UP": {
            "name": "Продуктовый менеджмент (Upskill)",
            "modules": 4,
            "cohorts": ["PM-Pilot-01", "PM-Pilot-02"],
        },
        "PY_DEV_UP": {
            "name": "Python для разработки (Upskill)",
            "modules": 5,
            "cohorts": ["PY-Pilot-01", "PY-Pilot-02"],
        },
    }

    sample_comments = {
        "positive": [
            "Всё отлично, материал структурирован и понятен.",
            "Очень понравилась практика на реальных данных!",
            "Лектор круто объясняет сложные темы.",
            "Супер модуль, всё разложилось по полочкам.",
            "Куратор ответил за 5 минут, очень помог с кодом!",
        ],
        "pacing": [
            "Не успевал за дедлайнами, слишком много информации.",
            (
                "Очень плотный график, нужно больше времени на выполнение"
                " заданий."
            ),
            "Хотелось бы чуть больше времени на закрепление материала.",
        ],
        "cohesion": [
            "Сложно связать теорию 2-го урока с практическим заданием.",
            "В ДЗ требуют то, чего не было в видео-лекциях.",
            "Каша в голове после 3-го урока, не хватило сквозного примера.",
        ],
        "energy": [
            "Сильно устал под конец модуля, еле сдал.",
            "Выгораю, совмещать с работой очень тяжело.",
            "Нужен небольшой перерыв перед следующим блоком.",
        ],
        "materials": [
            "В лонгриде к уроку 4 опечатка в формуле/коде.",
            "Скринкасты записаны с плохим микрофоном, тихо слышно.",
            "Хотелось бы больше текстовых шпаргалок к видео-лекциям.",
        ],
        "tasks": [
            "В квизе некорректно сформулирован 3-й вопрос.",
            "Тесты падают из-за несовместимости версий библиотек.",
            "Критерии проверки самостоятельного задания размыты.",
        ],
        "support": [
            "Координатор долго не отвечал на вопрос по доступу к платформе.",
            "Аспирант проверял ДЗ 4 дня вместо положенных двух.",
            "Хотелось бы более подробной обратной связи от проверяющего.",
        ],
        "platform": [
            "Видео-плеер периодически сбрасывает скорость воспроизведения.",
            "В мобильной версии сайта неудобно проходить тесты.",
        ],
    }

    rows = []
    for c_key, c_info in courses.items():
      for cohort in c_info["cohorts"]:
        cohort_pop_size = 120
        num_respondents = int(cohort_pop_size * np.random.uniform(0.80, 0.94))
        student_ids = [
            f"{c_key[:3]}_{cohort.replace('-', '')}_{i:03d}"
            for i in range(1, num_respondents + 1)
        ]

        for mod_num in range(1, c_info["modules"] + 1):
          mod_id = f"MOD_{mod_num:02d}"
          difficulty_bias = 0.15 if mod_num in [2, 3] else 0.0
          fatigue_bias = 0.05 * mod_num

          for s_id in student_ids:
            # Генерация шума/прокликов (Speedrunners ~10%)
            is_speedrunner = np.random.rand() < 0.10

            if is_speedrunner:
              noise_type = np.random.choice(
                  ["straight_5", "first_opt_conflict", "straight_1"],
                  p=[0.65, 0.25, 0.10],
              )
              if noise_type == "straight_5":
                pacing, cohesion, energy = "rushed", "clear", "high"
                scores = [5, 5, 5, 5, 5, 5]
              elif noise_type == "first_opt_conflict":
                pacing, cohesion, energy = "rushed", "fragmented", "depleted"
                scores = [5, 5, 5, 5, 5, 5]
              else:
                pacing, cohesion, energy = "rushed", "fragmented", "depleted"
                scores = [1, 1, 1, 1, 1, 1]
              comment = ""
            else:
              p_rushed = min(
                  0.55, 0.15 + difficulty_bias + np.random.uniform(0, 0.06)
              )
              p_slow = 0.10
              p_opt = max(0.2, 1.0 - p_rushed - p_slow)
              pacing = np.random.choice(
                  ["rushed", "optimal", "slow"], p=[p_rushed, p_opt, p_slow]
              )

              p_frag = min(
                  0.35, 0.08 + difficulty_bias + np.random.uniform(0, 0.05)
              )
              p_conf = min(0.45, 0.20 + difficulty_bias)
              p_clear = max(0.2, 1.0 - p_frag - p_conf)
              cohesion = np.random.choice(
                  ["clear", "confused", "fragmented"],
                  p=[p_clear, p_conf, p_frag],
              )

              p_dep = min(
                  0.50,
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

              base = (
                  4.4
                  - (0.5 if pacing == "rushed" else 0)
                  - (0.7 if cohesion == "fragmented" else 0)
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

              scores = [
                  gen_score(base + np.random.normal(0.1, 0.25)),
                  gen_score(base - (0.4 if cohesion != "clear" else 0)),
                  gen_score(base + np.random.normal(0.2, 0.3)),
                  gen_score(4.3 + np.random.normal(0, 0.35)),
                  gen_score(4.4 + np.random.normal(0, 0.3)),
                  gen_score(4.5 + np.random.normal(0, 0.2)),
              ]

              comment = ""
              if np.random.rand() < 0.25:
                if energy == "depleted":
                  comment = np.random.choice(sample_comments["energy"])
                elif pacing == "rushed":
                  comment = np.random.choice(sample_comments["pacing"])
                elif cohesion == "fragmented":
                  comment = np.random.choice(sample_comments["cohesion"])
                elif scores[1] <= 2:
                  comment = np.random.choice(sample_comments["tasks"])
                elif scores[0] <= 2:
                  comment = np.random.choice(sample_comments["materials"])
                elif scores[3] <= 2 or scores[4] <= 2:
                  comment = np.random.choice(sample_comments["support"])
                elif scores[5] <= 2:
                  comment = np.random.choice(sample_comments["platform"])
                else:
                  comment = np.random.choice(sample_comments["positive"])

            # Целевое событие: просрочка по ДЗ в след. модуле
            has_alert = (
                (pacing == "rushed")
                or (cohesion == "fragmented")
                or (energy == "depleted")
            )
            p_overdue = 0.38 if has_alert else 0.10
            has_overdue_next_mod = 1 if np.random.rand() < p_overdue else 0

            rows.append({
                "course_key": c_key,
                "course_name": c_info["name"],
                "cohort": cohort,
                "cohort_size_N": cohort_pop_size,
                "student_id": s_id,
                "module_id": mod_id,
                "pacing_score": pacing,
                "cohesion_score": cohesion,
                "energy_score": energy,
                "legacy_materials": scores[0],
                "legacy_tasks": scores[1],
                "legacy_experts": scores[2],
                "legacy_support_speed": scores[3],
                "legacy_support_care": scores[4],
                "legacy_platform": scores[5],
                "open_feedback": comment,
                "has_overdue_next_module": has_overdue_next_mod,
            })
    return pd.DataFrame(rows)


df_raw = load_data()

# Расчет признаков шума (Noise Classifier)
csi_cols = [
    "legacy_materials",
    "legacy_tasks",
    "legacy_experts",
    "legacy_support_speed",
    "legacy_support_care",
    "legacy_platform",
]
df_raw["i_straight"] = df_raw[csi_cols].std(axis=1) == 0
df_raw["i_first_option"] = (
    (df_raw["pacing_score"] == "rushed")
    & (df_raw["cohesion_score"] == "clear")
    & (df_raw["energy_score"] == "high")
)
df_raw["i_conflict"] = (
    (df_raw["energy_score"] == "depleted")
    | (df_raw["cohesion_score"] == "fragmented")
) & (df_raw[csi_cols] == 5).all(axis=1)
df_raw["s_noise"] = (
    df_raw["i_straight"].astype(int)
    + df_raw["i_first_option"].astype(int)
    + df_raw["i_conflict"].astype(int)
)
df_raw["is_garbage"] = df_raw["s_noise"] >= 2

# Сайдбар: Фильтры
st.sidebar.title("🎛 Фильтры анализа")

course_list = sorted(df_raw["course_name"].unique())
selected_course = st.sidebar.selectbox("Выберите курс:", course_list)

course_df = df_raw[df_raw["course_name"] == selected_course]
all_cohorts = sorted(course_df["cohort"].unique())

selected_cohorts = st.sidebar.multiselect(
    "Выберите потоки (когорты):",
    options=all_cohorts,
    default=all_cohorts,
    help="Выберите когорты пилотного запуска для межпоточного анализа",
)

if not selected_cohorts:
  st.warning("Пожалуйста, выберите хотя бы один поток в сайдбаре.")
  st.stop()

# Фильтрация по когортам
df_course = course_df[course_df["cohort"].isin(selected_cohorts)]
all_modules = sorted(df_course["module_id"].unique())
selected_modules = st.sidebar.multiselect(
    "Фильтр модулей:", options=all_modules, default=all_modules
)

df_base = df_course[df_course["module_id"].isin(selected_modules)]

# Переключатель очистки данных
data_clean_mode = st.sidebar.radio(
    "Фильтрация данных:",
    ["Все ответы (Raw)", "Только валидные (Clean, без шума)"],
    help="Исключает анкеты с подозрением на механический проклик (S noise >= 2)",
)

df_filtered = (
    df_base[~df_base["is_garbage"]]
    if data_clean_mode.startswith("Только валидные")
    else df_base
)

# Шапка
st.title(f"📊 Аналитика здоровья продукта: {selected_course}")
st.caption(
    f"Потоков: **{len(selected_cohorts)}** | Ответов: **{len(df_filtered)}**"
    f" (Исключено шума: **{len(df_base) - len(df_filtered)}** шт.)"
)

# Вкладки (4 шт.)
tab1, tab2, tab3, tab4 = st.tabs([
    "🟢 1. Пульс здоровья (MHI)",
    "🟡 2. Унаследованные метрики (CSI)",
    "🔴 3. Closed-Loop & Вербатим",
    "🔬 4. Валидация пилота (Эксперимент MVP)",
])

# ==========================================
# ВКЛАДКА 1: ПУЛЬС ЗДОРОВЬЯ (MHI)
# ==========================================
with tab1:
  st.subheader("Метрики состояния студентов (Module Health Index)")

  total_resp = len(df_filtered)
  pct_rushed = (
      (df_filtered["pacing_score"] == "rushed").sum() / total_resp * 100
      if total_resp
      else 0
  )
  pct_frag = (
      (df_filtered["cohesion_score"] == "fragmented").sum() / total_resp * 100
      if total_resp
      else 0
  )
  pct_depleted = (
      (df_filtered["energy_score"] == "depleted").sum() / total_resp * 100
      if total_resp
      else 0
  )

  clean_health = (
      (df_filtered["pacing_score"] != "rushed")
      & (df_filtered["cohesion_score"] != "fragmented")
      & (df_filtered["energy_score"] != "depleted")
  ).sum()
  mhi_rate = (clean_health / total_resp * 100) if total_resp else 0

  kpi1, kpi2, kpi3, kpi4 = st.columns(4)
  kpi1.metric(
      "MHI Rate (В норме)",
      f"{mhi_rate:.1f}%",
      delta="Цель > 75%",
      delta_color="normal" if mhi_rate >= 75 else "inverse",
  )
  kpi2.metric(
      "Pacing Alert (Спешка)",
      f"{pct_rushed:.1f}%",
      delta="Порог 25%",
      delta_color="inverse" if pct_rushed > 25 else "normal",
  )
  kpi3.metric(
      "Cohesion Deficit (Разрыв)",
      f"{pct_frag:.1f}%",
      delta="Порог 15%",
      delta_color="inverse" if pct_frag > 15 else "normal",
  )
  kpi4.metric(
      "Energy Depleted (Истощение)",
      f"{pct_depleted:.1f}%",
      delta="Порог 20%",
      delta_color="inverse" if pct_depleted > 20 else "normal",
  )

  st.divider()

  st.markdown("##### 📌 Распределение ответов по модулям (100% Stacked Bar)")
  c1, c2, c3 = st.columns(3)

  def build_stacked_chart(df_in, col, cat_order, color_map, title):
    ct = (
        pd.crosstab(df_in["module_id"], df_in[col], normalize="index") * 100
    ).reset_index()
    for cat in cat_order:
      if cat not in ct.columns:
        ct[cat] = 0.0
    melted = ct.melt(
        id_vars=["module_id"],
        value_vars=cat_order,
        var_name="Ответ",
        value_name="Процент",
    )
    fig = px.bar(
        melted,
        x="module_id",
        y="Процент",
        color="Ответ",
        color_discrete_map=color_map,
        category_orders={"Ответ": cat_order},
        title=title,
        text=melted["Процент"].apply(lambda v: f"{v:.0f}%" if v > 5 else ""),
    )
    fig.update_layout(
        barmode="stack",
        yaxis_title="%",
        xaxis_title="",
        legend_title="",
        height=340,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    return fig

  with c1:
    fig_pacing = build_stacked_chart(
        df_filtered,
        "pacing_score",
        ["slow", "optimal", "rushed"],
        {"rushed": "#D32F2F", "optimal": "#388E3C", "slow": "#FBC02D"},
        "Ритм и темп обучения (Pacing)",
    )
    st.plotly_chart(fig_pacing, use_container_width=True)

  with c2:
    fig_cohesion = build_stacked_chart(
        df_filtered,
        "cohesion_score",
        ["fragmented", "confused", "clear"],
        {"fragmented": "#D32F2F", "confused": "#FBC02D", "clear": "#388E3C"},
        "Логика и связность (Cohesion)",
    )
    st.plotly_chart(fig_cohesion, use_container_width=True)

  with c3:
    fig_energy = build_stacked_chart(
        df_filtered,
        "energy_score",
        ["depleted", "moderate", "high"],
        {"depleted": "#D32F2F", "moderate": "#FBC02D", "high": "#388E3C"},
        "Ресурс и запас сил (Energy)",
    )
    st.plotly_chart(fig_energy, use_container_width=True)

  if len(selected_cohorts) > 1:
    st.divider()
    st.markdown("##### 📈 Межпоточный тренд: Динамика алертов по когортам")
    cohort_trend = (
        df_filtered.groupby("cohort")
        .apply(
            lambda x: pd.Series({
                "Спешка (Rushed %)": (x["pacing_score"] == "rushed").mean()
                * 100,
                "Разрыв логики (Frag %)": (
                    x["cohesion_score"] == "fragmented"
                ).mean()
                * 100,
                "Истощение (Depleted %)": (
                    x["energy_score"] == "depleted"
                ).mean()
                * 100,
            }),
            include_groups=False,
        )
        .reset_index()
    )

    fig_trend = px.line(
        cohort_trend,
        x="cohort",
        y=[
            "Спешка (Rushed %)",
            "Разрыв логики (Frag %)",
            "Истощение (Depleted %)",
        ],
        markers=True,
        color_discrete_map={
            "Спешка (Rushed %)": "#F57C00",
            "Разрыв логики (Frag %)": "#D32F2F",
            "Истощение (Depleted %)": "#7B1FA2",
        },
    )
    fig_trend.update_layout(
        height=320,
        yaxis_title="%",
        xaxis_title="Когорта",
        legend_title="Метрика",
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ==========================================
# ВКЛАДКА 2: УНАСЛЕДОВАННЫЕ МЕТРИКИ (CSI)
# ==========================================
with tab2:
  st.subheader("Унаследованные метрики CSI (шкала 1–5)")
  st.caption(
      "Структурный анализ распределения: Top-2 Box (% довольных) и Bottom-2 Box"
      " (% недовольных)."
  )

  legacy_map = {
      "legacy_materials": (
          "Качество учебных материалов: лонгриды, видео-лекции, скринкасты"
      ),
      "legacy_tasks": (
          "Качество заданий: тесты, квизы, самостоятельные задания"
      ),
      "legacy_experts": "Работа экспертов / преподавателей в этом модуле",
      "legacy_support_speed": (
          "Скорость работы команды сопровождения: координатора, аспиранта"
      ),
      "legacy_support_care": (
          "Забота и поддержка команды сопровождения (эмпатия)"
      ),
      "legacy_platform": "Удобство сайта / платформы в рамках модуля",
  }

  summary_rows = []
  for col, name in legacy_map.items():
    s = df_filtered[col]
    top2 = (s >= 4).mean() * 100
    bot2 = (s <= 2).mean() * 100
    summary_rows.append({
        "Показатель (Вопрос)": name,
        "Top-2 Box (4–5)": f"{top2:.1f}%",
        "Bottom-2 Box (1–2)": f"{bot2:.1f}%",
        "Статус": (
            "🔴 Критично"
            if bot2 > 15
            else ("🟡 Требует внимания" if top2 < 75 else "🟢 Норма")
        ),
    })

  st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

  st.divider()

  st.markdown("##### 🔍 Фокусный Deep-Dive по конкретному вопросу CSI")
  focus_col_name = st.selectbox(
      "Выберите вопрос для детального анализа распределения оценок:",
      list(legacy_map.values()),
  )
  focus_col = [k for k, v in legacy_map.items() if v == focus_col_name][0]

  col_chart, col_pivot = st.columns([3, 2])

  with col_chart:
    ct_leg = (
        pd.crosstab(
            df_filtered["module_id"], df_filtered[focus_col], normalize="index"
        )
        * 100
    ).reset_index()
    for grade in [1, 2, 3, 4, 5]:
      if grade not in ct_leg.columns:
        ct_leg[grade] = 0.0
    melted_leg = ct_leg.melt(
        id_vars=["module_id"],
        value_vars=[1, 2, 3, 4, 5],
        var_name="Оценка",
        value_name="Доля",
    )
    grade_colors = {
        1: "#D32F2F",
        2: "#F57C00",
        3: "#FBC02D",
        4: "#689F38",
        5: "#2E7D32",
    }

    fig_leg = px.bar(
        melted_leg,
        x="module_id",
        y="Доля",
        color="Оценка",
        color_discrete_map=grade_colors,
        category_orders={"Оценка": [1, 2, 3, 4, 5]},
        title=f"Распределение оценок (1–5): {focus_col_name}",
        text=melted_leg["Доля"].apply(lambda v: f"{v:.0f}%" if v >= 6 else ""),
    )
    fig_leg.update_layout(
        barmode="stack",
        yaxis_title="%",
        xaxis_title="",
        height=360,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    st.plotly_chart(fig_leg, use_container_width=True)

  with col_pivot:
    st.markdown("**Pivot-таблица распределения по модулям (%):**")
    pivot_table = pd.pivot_table(
        df_filtered,
        index="module_id",
        columns=focus_col,
        aggfunc="size",
        fill_value=0,
    )
    pivot_pct = pivot_table.div(pivot_table.sum(axis=1), axis=0) * 100
    st.dataframe(pivot_pct.style.format("{:.1f}%"), use_container_width=True)

# ==========================================
# ВКЛАДКА 3: CLOSED-LOOP & ВЕРБАТИМ
# ==========================================
with tab3:
  st.subheader("Операционный контур реагирования (Closed-Loop)")

  churn_condition = (df_filtered["energy_score"] == "depleted") & (
      (df_filtered["pacing_score"] == "rushed")
      | (df_filtered["cohesion_score"] == "fragmented")
      | (df_filtered["legacy_tasks"] <= 2)
      | (df_filtered["legacy_materials"] <= 2)
  )

  df_alerts = df_filtered[churn_condition][
      [
          "cohort",
          "student_id",
          "module_id",
          "energy_score",
          "pacing_score",
          "cohesion_score",
          "legacy_tasks",
          "legacy_materials",
          "open_feedback",
      ]
  ].copy()

  st.markdown(
      f"##### 🚨 Реестр студентов в зоне высокого риска оттока ({len(df_alerts)} чел.)"
  )
  st.caption(
      "Критерий алерта: Истощение (depleted) в сочетании со спешкой, разрывом"
      " логики или критически низкой оценкой практики/материалов."
  )

  if not df_alerts.empty:
    st.dataframe(
        df_alerts.rename(
            columns={
                "cohort": "Поток",
                "student_id": "ID Студента",
                "module_id": "Модуль",
                "energy_score": "Ресурс",
                "pacing_score": "Ритм",
                "cohesion_score": "Связность",
                "legacy_tasks": "Оценка заданий",
                "legacy_materials": "Оценка теории",
                "open_feedback": "Комментарий",
            }
        ),
        use_container_width=True,
    )
  else:
    st.success("Критических алертов не обнаружено.")

  st.divider()

  st.markdown("##### 💬 Лента открытых комментариев")
  feedback_df = df_filtered[df_filtered["open_feedback"].str.len() > 0][
      [
          "cohort",
          "module_id",
          "student_id",
          "open_feedback",
          "energy_score",
          "pacing_score",
      ]
  ]

  search_term = st.text_input(
      "Поиск по ключевым словам в комментариях:",
      placeholder="Например: звук, опечатка, дедлайн, каша, плеер...",
  )
  if search_term:
    feedback_df = feedback_df[
        feedback_df["open_feedback"].str.contains(
            search_term, case=False, na=False
        )
    ]

  st.dataframe(
      feedback_df.rename(
          columns={
              "cohort": "Поток",
              "module_id": "Модуль",
              "student_id": "ID Студента",
              "open_feedback": "Текст отзыва",
              "energy_score": "Ресурс",
              "pacing_score": "Ритм",
          }
      ),
      use_container_width=True,
  )

# =========================================================================
# ВКЛАДКА 4: ВАЛИДАЦИЯ ПИЛОТА (ЭКСПЕРИМЕНТ MVP — ОПЦИОНАЛЬНЫЙ СЛОЙ)
# =========================================================================
with tab4:
  st.subheader("🔬 Мета-аналитика и валидация пилотного эксперимента")
  st.info(
      "ℹ️ **Опциональный аналитический слой (MVP):** Данная вкладка"
      " предназначена для CPO, лида аналитики и владельца продукта для"
      " подведения итогов пилотного запуска на 5 потоках. Оценивает надежность"
      " данных (GRR, MoE) и прогностическую ценность инструмента перед"
      " масштабированием на 100% курсов."
  )

  # Расчет параметров эксперимента по выборке df_base (до фильтрации)
  total_n_raw = len(df_base)
  garbage_n = df_base["is_garbage"].sum()
  grr_val = (garbage_n / total_n_raw * 100) if total_n_raw else 0.0

  # Чистый объем выборки (n) и генеральная совокупность (N)
  clean_df = df_base[~df_base["is_garbage"]]
  n_clean = len(clean_df)
  # Популяция = количество модулей * размер когорты
  n_mods = df_base["module_id"].nunique()
  n_cohorts = df_base["cohort"].nunique()
  N_pop = int(120 * n_mods * n_cohorts)

  # MoE формула
  Z = 1.96
  p = 0.5
  if n_clean > 0 and N_pop > n_clean:
    moe_val = (
        Z
        * np.sqrt((p * (1 - p)) / n_clean)
        * np.sqrt((N_pop - n_clean) / (N_pop - 1))
        * 100
    )
  elif n_clean > 0:
    moe_val = Z * np.sqrt((p * (1 - p)) / n_clean) * 100
  else:
    moe_val = 100.0

  # Относительный риск (RR overdue)
  alert_mask = (
      (clean_df["pacing_score"] == "rushed")
      | (clean_df["cohesion_score"] == "fragmented")
      | (clean_df["energy_score"] == "depleted")
  )
  alert_grp = clean_df[alert_mask]
  base_grp = clean_df[~alert_mask]

  risk_alert = (
      alert_grp["has_overdue_next_module"].mean() if len(alert_grp) > 0 else 0.0
  )
  risk_base = (
      base_grp["has_overdue_next_module"].mean() if len(base_grp) > 0 else 0.0
  )
  rr_val = (risk_alert / risk_base) if risk_base > 0 else 0.0

  # Итоговый вердикт (Decision Gate)
  is_grr_ok = grr_val < 15.0
  is_moe_ok = moe_val < 7.0
  is_rr_ok = rr_val >= 2.5

  if is_grr_ok and is_moe_ok and is_rr_ok:
    verdict_text = "🟢 УСПЕХ: Все критерии выполнены — готовность к масштабированию на 100% курсов"
    verdict_color = "success"
  elif grr_val > 30.0 or moe_val > 12.0 or rr_val < 1.5:
    verdict_text = (
        "🔴 ПРОВАЛ: Критические отклонения — требуется пересмотр концепции"
    )
    verdict_color = "error"
  else:
    verdict_text = (
        "🟡 ДОРАБОТКА: Требуются точечные UX-корректировки перед раскаткой"
    )
    verdict_color = "warning"

  if verdict_color == "success":
    st.success(f"### Итоговый вердикт эксперимента: {verdict_text}")
  elif verdict_color == "warning":
    st.warning(f"### Итоговый вердикт эксперимента: {verdict_text}")
  else:
    st.error(f"### Итоговый вердикт эксперимента: {verdict_text}")

  st.divider()

  # Карточки трех ключевых метрик эксперимента
  st.markdown("##### 📊 Ключевые показатели надежности и ценности пилота")
  ec1, ec2, ec3 = st.columns(3)

  ec1.metric(
      "1. Garbage Response Rate (GRR)",
      f"{grr_val:.1f}%",
      delta="Цель < 15% (Безопасность)",
      delta_color="normal" if grr_val < 15 else "inverse",
  )
  ec2.metric(
      "2. Margin of Error (MoE)",
      f"±{moe_val:.1f}%",
      delta="Цель < 7% (Достоверность)",
      delta_color="normal" if moe_val < 7 else "inverse",
  )
  ec3.metric(
      "3. Относительный риск долгов (RR)",
      f"{rr_val:.2f}x",
      delta="Цель ≥ 2.5x (Ценность MHI)",
      delta_color="normal" if rr_val >= 2.5 else "inverse",
  )

  st.divider()

  # Детализация метрик
  col_grr_detail, col_rr_detail = st.columns(2)

  with col_grr_detail:
    st.markdown("###### 🔍 Анализ структуры шума (Детекция прокликов)")
    noise_breakdown = pd.DataFrame({
        "Индикатор": [
            "Straightlining (Монотонные CSI 5-5-5 или 1-1-1)",
            "First-Option Bias (Только 1-е плашки MHI)",
            "Logic Conflict (Алерт MHI + CSI 5/5)",
        ],
        "Доля анкет (%)": [
            df_base["i_straight"].mean() * 100,
            df_base["i_first_option"].mean() * 100,
            df_base["i_conflict"].mean() * 100,
        ],
    })
    fig_noise = px.bar(
        noise_breakdown,
        x="Доля анкет (%)",
        y="Индикатор",
        orientation="h",
        text=noise_breakdown["Доля анкет (%)"].apply(lambda v: f"{v:.1f}%"),
        color="Индикатор",
        color_discrete_sequence=["#F57C00", "#D32F2F", "#7B1FA2"],
    )
    fig_noise.update_layout(
        showlegend=False, height=260, margin=dict(l=10, r=10, t=20, b=20)
    )
    st.plotly_chart(fig_noise, use_container_width=True)
    st.caption(
        f"Всего отфильтровано как мусор ($S_{{noise}} \ge 2$): **{garbage_n}**"
        f" из **{total_n_raw}** анкет ({grr_val:.1f}%)."
    )

  with col_rr_detail:
    st.markdown("###### 🎯 Прогностическая сила MHI: Доля должников по группам")
    risk_compare = pd.DataFrame({
        "Группа студентов": [
            "Группа алертов MHI (Спешка/Разрыв/Истощение)",
            "Базовая группа (MHI в норме)",
        ],
        "Доля должников в след. модуле (%)": [
            risk_alert * 100,
            risk_base * 100,
        ],
    })
    fig_rr = px.bar(
        risk_compare,
        x="Группа студентов",
        y="Доля должников в след. модуле (%)",
        text=risk_compare["Доля должников в след. модуле (%)"].apply(
            lambda v: f"{v:.1f}%"
        ),
        color="Группа студентов",
        color_discrete_map={
            "Группа алертов MHI (Спешка/Разрыв/Истощение)": "#D32F2F",
            "Базовая группа (MHI в норме)": "#388E3C",
        },
    )
    fig_rr.update_layout(
        showlegend=False, height=260, margin=dict(l=10, r=10, t=20, b=20)
    )
    st.plotly_chart(fig_rr, use_container_width=True)
    st.caption(
        f"Студенты с алертом MHI получают долги в **{rr_val:.1f} раза чаще**"
        " базовой группы."
    )

  st.divider()

  # Справочная матрица решений
  st.markdown("###### 📋 Регламент принятия решений по масштабированию пилота")
  st.table(
      pd.DataFrame({
          "Сценарий": ["🟢 Успех", "🟡 Доработка", "🔴 Провал"],
          "Безопасность (GRR)": ["GRR < 15%", "GRR 15–30%", "GRR > 30%"],
          "Достоверность (MoE)": ["MoE < 7%", "MoE 7–12%", "MoE > 12%"],
          "Ценность (RR overdue)": ["RR ≥ 2.5", "RR 2.0–2.5", "RR < 1.5"],
          "Управленческое решение": [
              "Масштабирование на 100% курсов, отключение старого CSAT",
              "UX-полировка интерфейса, случайная ротация плашек",
              "Снятие блокирующего экрана, переход к сэмплированию",
          ],
      })
  )
