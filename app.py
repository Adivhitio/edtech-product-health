import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Дашборд: Пульс Модуля & CSAT", page_icon="📊", layout="wide"
)


# Загрузка или автоматическая генерация данных в памяти
@st.cache_data
def load_data():
  try:
    return pd.read_csv("pulse_multi_course_data.csv")
  except FileNotFoundError:
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
            p_rushed = min(
                0.6, 0.15 + difficulty_bias + np.random.uniform(0, 0.08)
            )
            p_slow = 0.10
            p_opt = max(0.2, 1.0 - p_rushed - p_slow)
            pacing = np.random.choice(
                ["rushed", "optimal", "slow"], p=[p_rushed, p_opt, p_slow]
            )

            # Cohesion
            p_frag = min(
                0.4, 0.08 + difficulty_bias + np.random.uniform(0, 0.06)
            )
            p_conf = min(0.5, 0.20 + difficulty_bias)
            p_clear = max(0.2, 1.0 - p_frag - p_conf)
            cohesion = np.random.choice(
                ["clear", "confused", "fragmented"],
                p=[p_clear, p_conf, p_frag],
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
    return pd.DataFrame(rows)


df_raw = load_data()

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
    help="Выберите несколько потоков для межпоточного анализа тренда",
)

if not selected_cohorts:
  st.warning("Пожалуйста, выберите хотя бы один поток в сайдбаре.")
  st.stop()

# Фильтрация по выбранным когортам
df = course_df[course_df["cohort"].isin(selected_cohorts)]

all_modules = sorted(df["module_id"].unique())
selected_modules = st.sidebar.multiselect(
    "Фильтр модулей:", options=all_modules, default=all_modules
)

df_filtered = df[df["module_id"].isin(selected_modules)]

# Заголовок
st.title(f"📊 Аналитика здоровья продукта: {selected_course}")
st.caption(
    f"Выбрано потоков: **{len(selected_cohorts)}** | Ответов в выборке:"
    f" **{len(df_filtered)}**"
)

# Три целевые вкладки
tab1, tab2, tab3 = st.tabs([
    "🟢 1. Пульс здоровья (MHI)",
    "🟡 2. Legacy CSAT & Детализация",
    "🔴 3. Closed-Loop & Вербатим",
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

  st.markdown("##### 📌 Распределение ответов по модулям")
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
        "Ритм и спешка (Pacing)",
    )
    st.plotly_chart(fig_pacing, use_container_width=True)

  with c2:
    fig_cohesion = build_stacked_chart(
        df_filtered,
        "cohesion_score",
        ["fragmented", "confused", "clear"],
        {"fragmented": "#D32F2F", "confused": "#FBC02D", "clear": "#388E3C"},
        "Связность и логика (Cohesion)",
    )
    st.plotly_chart(fig_cohesion, use_container_width=True)

  with c3:
    fig_energy = build_stacked_chart(
        df_filtered,
        "energy_score",
        ["depleted", "moderate", "high"],
        {"depleted": "#D32F2F", "moderate": "#FBC02D", "high": "#388E3C"},
        "Ресурс и энергия (Energy)",
    )
    st.plotly_chart(fig_energy, use_container_width=True)

  if len(selected_cohorts) > 1:
    st.divider()
    st.markdown("##### 📈 Межпоточный тренд: Доля алертов по когортам")
    cohort_trend = (
        df.groupby("cohort")
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
# ВКЛАДКА 2: LEGACY CSAT & ДЕТАЛИЗАЦИЯ
# ==========================================
with tab2:
  st.subheader("Унаследованные метрики (1–5) и структурный анализ")

  legacy_map = {
      "legacy_speaker": "Спикер / Эксперт",
      "legacy_hw": "Домашние задания / Практика",
      "legacy_platform": "Удобство платформы (LMS)",
      "legacy_support": "Служба поддержки / Сопровождение",
  }

  summary_rows = []
  for col, name in legacy_map.items():
    s = df_filtered[col]
    top2 = (s >= 4).mean() * 100
    bot2 = (s <= 2).mean() * 100
    mean_val = s.mean()
    med_val = s.median()
    summary_rows.append({
        "Показатель": name,
        "Top-2 Box (4–5)": f"{top2:.1f}%",
        "Bottom-2 Box (1–2)": f"{bot2:.1f}%",
        "Среднее (1–5)": f"{mean_val:.2f}",
        "Медиана": f"{med_val:.1f}",
        "Статус": (
            "🔴 Критично"
            if bot2 > 15
            else ("🟡 Требует внимания" if top2 < 75 else "🟢 Норма")
        ),
    })

  st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

  st.divider()

  st.markdown("##### 🔍 Фокусный Deep-Dive по конкретному вопросу")
  focus_col_name = st.selectbox(
      "Выберите параметр для детального анализа распределения:",
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
    st.markdown(f"**Pivot-таблица по модулям ({focus_col_name}):**")
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
      | (df_filtered["legacy_hw"] <= 2)
  )

  df_alerts = df_filtered[churn_condition][
      [
          "cohort",
          "student_id",
          "module_id",
          "energy_score",
          "pacing_score",
          "cohesion_score",
          "legacy_hw",
          "open_feedback",
      ]
  ].copy()

  st.markdown(
      f"##### 🚨 Реестр студентов в зоне высокого риска оттока ({len(df_alerts)} чел.)"
  )
  st.caption(
      "Критерий алерта: Сильное истощение (depleted) + спешка / дефицит логики /"
      " низкая оценка практики."
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
                "legacy_hw": "Оценка ДЗ",
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
      placeholder="Например: звук, дедлайн, каша, практика...",
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
