import streamlit as st
import pandas as pd
import plotly.express as px

# Настройки страницы
st.set_page_config(page_title="Product Health Dashboard", page_icon="📊", layout="wide")

# Загрузка данных
@st.cache_data
def load_data():
    try:
        return pd.read_csv('pulse_6_modules_clean.csv')
    except FileNotFoundError:
        st.error("Файл 'pulse_6_modules_clean.csv' не найден.")
        return pd.DataFrame()

df = load_data()

# Функция для расчета процентного соотношения внутри каждого модуля
def get_pct_data(data_df, score_col):
    grouped = data_df.groupby(['module_id', score_col]).size().reset_index(name='count')
    grouped['total'] = grouped.groupby('module_id')['count'].transform('sum')
    grouped['percentage'] = (grouped['count'] / grouped['total'] * 100).round(1)
    return grouped

if not df.empty:
    st.title("📊 Дашборд здоровья продукта: «Пульс модуля»")
    st.caption("Анализ 3 ключевых сигналов (Ритм, Связность, Ресурс) по когорте из 200 студентов")

    # Боковая панель с фильтром
    st.sidebar.header("Фильтры")
    selected_modules = st.sidebar.multiselect(
        "Выберите модули:",
        options=df['module_id'].unique(),
        default=df['module_id'].unique()
    )
    filtered_df = df[df['module_id'].isin(selected_modules)]

    # 1. Метрики верхнего уровня (KPI)
    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    
    total = len(filtered_df)
    rushed = (len(filtered_df[filtered_df['pacing_score'] == 'rushed']) / total * 100) if total > 0 else 0
    fragmented = (len(filtered_df[filtered_df['cohesion_score'] == 'fragmented']) / total * 100) if total > 0 else 0
    depleted = (len(filtered_df[filtered_df['energy_score'] == 'depleted']) / total * 100) if total > 0 else 0

    # Расчет Churn Risk (2 раза depleted подряд)
    df_sorted = df.sort_values(['student_id', 'module_id'])
    churn_alert_students = set()
    for student_id, group in df_sorted.groupby('student_id'):
        energies = group['energy_score'].tolist()
        for i in range(len(energies) - 1):
            if energies[i] == 'depleted' and energies[i+1] == 'depleted':
                churn_alert_students.add(student_id)
                break

    c1.metric("1. Ритм: Спешка (Rushed)", f"{rushed:.1f}%", "🔴 Alert (>25%)" if rushed > 25 else "🟢 Норма", delta_color="inverse")
    c2.metric("2. Логика: Дефицит (Fragmented)", f"{fragmented:.1f}%", "🔴 Alert (>15%)" if fragmented > 15 else "🟢 Норма", delta_color="inverse")
    c3.metric("3. Ресурс: Истощение (Depleted)", f"{depleted:.1f}%", "Уровень усталости")
    c4.metric("Closed-Loop: Риск оттока", f"{len(churn_alert_students)} чел.", "2x Depleted подряд", delta_color="off")

    st.markdown("---")

    # 2. Графики по всем 3 вопросам (в процентах)
    st.subheader("📊 Распределение ответов по модулям (%)")
    col_q1, col_q2, col_q3 = st.columns(3)

    # Вопрос 1: Ритм
    with col_q1:
        st.markdown("**1. Ритм и Темп (Pacing)**")
        p_data = get_pct_data(filtered_df, 'pacing_score')
        fig_p = px.bar(
            p_data, x='module_id', y='percentage', color='pacing_score',
            color_discrete_map={'rushed': '#EF553B', 'optimal': '#00CC96', 'slow': '#AB63FA'},
            labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'pacing_score': 'Ответ', 'count': 'Студентов'},
            hover_data={'count': True, 'percentage': ':.1f%'}
        )
        fig_p.update_layout(yaxis_suffix="%")
        st.plotly_chart(fig_p, use_container_width=True)

    # Вопрос 2: Связность
    with col_q2:
        st.markdown("**2. Связность и Логика (Cohesion)**")
        c_data = get_pct_data(filtered_df, 'cohesion_score')
        fig_c = px.bar(
            c_data, x='module_id', y='percentage', color='cohesion_score',
            color_discrete_map={'clear': '#00CC96', 'confused': '#FFA15A', 'fragmented': '#EF553B'},
            labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'cohesion_score': 'Ответ', 'count': 'Студентов'},
            hover_data={'count': True, 'percentage': ':.1f%'}
        )
        fig_c.update_layout(yaxis_suffix="%")
        st.plotly_chart(fig_c, use_container_width=True)

    # Вопрос 3: Ресурс / Энергия
    with col_q3:
        st.markdown("**3. Состояние ресурса (Energy)**")
        e_data = get_pct_data(filtered_df, 'energy_score')
        fig_e = px.bar(
            e_data, x='module_id', y='percentage', color='energy_score',
            color_discrete_map={'high': '#00CC96', 'moderate': '#FFA15A', 'depleted': '#EF553B'},
            labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'energy_score': 'Ответ', 'count': 'Студентов'},
            hover_data={'count': True, 'percentage': ':.1f%'}
        )
        fig_e.update_layout(yaxis_suffix="%")
        st.plotly_chart(fig_e, use_container_width=True)

    st.markdown("---")

    # 3. Таблица для тьюторов
    st.subheader("🚨 Списочный алерт Churn Risk для Тьюторов")
    st.caption("Студенты, ответившие 'depleted' (истощение) 2 модуля подряд — требуют контакта:")
    
    churn_df = df[df['student_id'].isin(churn_alert_students)][['student_id', 'module_id', 'energy_score', 'pacing_score']]
    st.dataframe(churn_df.sort_values(['student_id', 'module_id']), use_container_width=True)
