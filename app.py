import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Дашборд: Пульс Модуля & CSAT", page_icon="📊", layout="wide"
)


# Загрузка данных
@st.cache_data
def load_data():
  return pd.read_csv("pulse_multi_course_data.csv")


df_raw = load_data()

# Сайдбар: Фильтры
st.sidebar.title("🎛 Фильтры анализа")

course_list = df_raw["course_name"].unique()
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

  # Расчет KPI
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

  # MHI Rate (% студентов без единого критического сигнала)
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

  # Графики 100% Stacked Bar по 3 вопросам
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

  # Межпоточный анализ тренда (если выбрано >1 когорты)
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

  # Сводная таблица Top-2 / Bottom-2 Box
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

  # Deep-Dive Селектор конкретного вопроса
  st.markdown("##### 🔍 Фокусный Deep-Dive по конкретному вопросу")
  focus_col_name = st.selectbox(
      "Выберите параметр для детального анализа распределения:",
      list(legacy_map.values()),
  )
  focus_col = [k for k, v in legacy_map.items() if v == focus_col_name][0]

  col_chart, col_pivot = st.columns([3, 2])

  with col_chart:
    # 100% Stacked Bar для оценок 1-5
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
        text=melted_leg["Доля"].apply(
            lambda v: f"{v:.0f}%" if v >= 6 else ""
        ),
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

  # Формирование списка Churn Risk
  churn_condition = (df_filtered["energy_score"] == "depleted") & (
      (df_filtered["pacing_score"] == "rushed")
      | (df_filtered["cohesion_score"] == "fragmented")
      | (df_filtered["legacy_hw"] <= 2)
  )

  df_alerts = df_filtered[churn_condition][
      ["cohort", "student_id", "module_id", "energy_score", "pacing_score", "cohesion_score", "legacy_hw", "open_feedback"]
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

  # Таблица открытых отзывов
  st.markdown("##### 💬 Лента открытых комментариев")
  feedback_df = df_filtered[
      df_filtered["open_feedback"].str.len() > 0
  ][["cohort", "module_id", "student_id", "open_feedback", "energy_score", "pacing_score"]]

  search_term = st.text_input(
      "Поиск по ключевым словам в комментариях:",
      placeholder="Например: звук, дедлайн, каша, практика...",
  )
  if search_term:
    feedback_df = feedback_df[
        feedback_df["open_feedback"].str.contains(search_term, case=False, na=False)
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
