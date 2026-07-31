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
        st.error("Файл 'pulse_6_modules_clean.csv' не найден. Запустите make_data.py!")
        return pd.DataFrame()

df = load_data()

# Функция расчета процентов для stacked-диаграмм
def get_pct_data(data_df, score_col):
    grouped = data_df.groupby(['module_id', score_col]).size().reset_index(name='count')
    grouped['total'] = grouped.groupby('module_id')['count'].transform('sum')
    grouped['percentage'] = (grouped['count'] / grouped['total'] * 100).round(1)
    return grouped

if not df.empty:
    st.title("📊 Дашборд здоровья продукта (Hybrid MVP v1.0)")
    st.caption("Единый аналитический контур: Атомарный Пульс + Legacy CSAT + Closed-Loop")

    # Боковая панель с глобальным фильтром модулей
    st.sidebar.header("Фильтры")
    selected_modules = st.sidebar.multiselect(
        "Выберите модули:",
        options=df['module_id'].unique(),
        default=df['module_id'].unique()
    )
    filtered_df = df[df['module_id'].isin(selected_modules)]

    # Вычисление Churn Risk (Правило 1: 2x depleted | Правило 2: fragmented + legacy <= 2)
    df_sorted = df.sort_values(['student_id', 'module_id'])
    churn_alert_students = set()
    
    for student_id, group in df_sorted.groupby('student_id'):
        energies = group['energy_score'].tolist()
        cohesions = group['cohesion_score'].tolist()
        
        # Проверка наследуемых оценок для правила 2
        min_legacy = group[['legacy_speaker', 'legacy_homework', 'legacy_materials']].min(axis=1).tolist()
        
        for i in range(len(energies)):
            # Правило 1: Истощение 2 раза подряд
            if i < len(energies) - 1 and energies[i] == 'depleted' and energies[i+1] == 'depleted':
                churn_alert_students.add(student_id)
            # Правило 2: Разрыв связности + низкая оценка legacy
            if cohesions[i] == 'fragmented' and min_legacy[i] <= 2:
                churn_alert_students.add(student_id)

    # СОЗДАЕМ 3 ВКЛАДКИ СОГЛАСНО ТЗ
    tab1, tab2, tab3 = st.tabs([
        "🟢 Вкладка 1: Пульс Здоровья (Core)", 
        "🟡 Вкладка 2: Legacy CSAT (Стейкхолдеры)", 
        "🔴 Вкладка 3: Closed-Loop & Вербатим"
    ])

    # ==========================================
    # ВКЛАДКА 1: ПУЛЬС ЗДОРОВЬЯ ПРОДУКТА
    # ==========================================
    with tab1:
        st.subheader("Ключевые опережающие индикаторы (Leading Indicators)")
        c1, c2, c3, c4 = st.columns(4)
        
        total = len(filtered_df)
        rushed = (len(filtered_df[filtered_df['pacing_score'] == 'rushed']) / total * 100) if total > 0 else 0
        fragmented = (len(filtered_df[filtered_df['cohesion_score'] == 'fragmented']) / total * 100) if total > 0 else 0
        depleted = (len(filtered_df[filtered_df['energy_score'] == 'depleted']) / total * 100) if total > 0 else 0

        c1.metric("1. Ритм: Спешка (Rushed)", f"{rushed:.1f}%", "🔴 Alert (>25%)" if rushed > 25 else "🟢 Норма", delta_color="inverse")
        c2.metric("2. Логика: Дефицит (Fragmented)", f"{fragmented:.1f}%", "🔴 Alert (>15%)" if fragmented > 15 else "🟢 Норма", delta_color="inverse")
        c3.metric("3. Ресурс: Истощение (Depleted)", f"{depleted:.1f}%", "Уровень усталости")
        c4.metric("Risk Alerts (Отток)", f"{len(churn_alert_students)} чел.", "Требуют контакта", delta_color="off")

        st.markdown("---")
        st.subheader("Распределение 3 атомарных сигналов по модулям (%)")
        col_q1, col_q2, col_q3 = st.columns(3)

        with col_q1:
            st.markdown("**1. Ритм и Темп (Pacing)**")
            p_data = get_pct_data(filtered_df, 'pacing_score')
            fig_p = px.bar(
                p_data, x='module_id', y='percentage', color='pacing_score',
                color_discrete_map={'rushed': '#EF553B', 'optimal': '#00CC96', 'slow': '#AB63FA'},
                labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'pacing_score': 'Ответ'},
                hover_data={'count': True, 'percentage': ':.1f%'}
            )
            fig_p.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig_p, use_container_width=True)

        with col_q2:
            st.markdown("**2. Связность и Логика (Cohesion)**")
            c_data = get_pct_data(filtered_df, 'cohesion_score')
            fig_c = px.bar(
                c_data, x='module_id', y='percentage', color='cohesion_score',
                color_discrete_map={'clear': '#00CC96', 'confused': '#FFA15A', 'fragmented': '#EF553B'},
                labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'cohesion_score': 'Ответ'},
                hover_data={'count': True, 'percentage': ':.1f%'}
            )
            fig_c.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig_c, use_container_width=True)

        with col_q3:
            st.markdown("**3. Состояние ресурса (Energy)**")
            e_data = get_pct_data(filtered_df, 'energy_score')
            fig_e = px.bar(
                e_data, x='module_id', y='percentage', color='energy_score',
                color_discrete_map={'high': '#00CC96', 'moderate': '#FFA15A', 'depleted': '#EF553B'},
                labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'energy_score': 'Ответ'},
                hover_data={'count': True, 'percentage': ':.1f%'}
            )
            fig_e.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig_e, use_container_width=True)

    # ==========================================
    # ВКЛАДКА 2: LEGACY CSAT & ДЕТАЛИЗАЦИЯ
    # ==========================================
    with tab2:
        st.subheader("Наследуемые оценки CSAT (Шкала 1–5)")
        st.caption("Раздел для мониторинга исторических показателей стейкхолдерами")

        # Кросс-анализ / Фильтр по сегментам
        segment_filter = st.radio(
            "Срез когорты для анализа средних оценок:",
            ["Все студенты", "Только с историей спешки (Rushed)", "Только в состоянии истощения (Depleted)"],
            horizontal=True
        )

        df_legacy = filtered_df.copy()
        if segment_filter == "Только с историей спешки (Rushed)":
            df_legacy = df_legacy[df_legacy['pacing_score'] == 'rushed']
        elif segment_filter == "Только в состоянии истощения (Depleted)":
            df_legacy = df_legacy[df_legacy['energy_score'] == 'depleted']

        legacy_cols = ['legacy_speaker', 'legacy_platform', 'legacy_homework', 'legacy_materials', 'legacy_support']
        legacy_names = {'legacy_speaker': 'Спикер', 'legacy_platform': 'Платформа', 
                        'legacy_homework': 'ДЗ', 'legacy_materials': 'Материалы', 'legacy_support': 'Поддержка'}
        
        avg_scores = df_legacy.groupby('module_id')[legacy_cols].mean().round(2).rename(columns=legacy_names)

        col_tbl, col_chart = st.columns([4, 6])
        
        with col_tbl:
            st.markdown("**Таблица средних баллов по модулям**")
            st.dataframe(avg_scores, use_container_width=True)

        with col_chart:
            st.markdown("**Тренды CSAT от модуля к модулю**")
            avg_scores_reset = avg_scores.reset_index().melt(id_vars='module_id', var_name='Показатель', value_name='Средний балл')
            fig_trend = px.line(
                avg_scores_reset, x='module_id', y='Средний балл', color='Показатель',
                markers=True, title="Динамика средних оценок 1-5"
            )
            fig_trend.update_yaxes(range=[1, 5])
            st.plotly_chart(fig_trend, use_container_width=True)

    # ==========================================
    # ВКЛАДКА 3: CLOSED-LOOP & ВЕРБАТИМ
    # ==========================================
    with tab3:
        st.subheader("🚨 Рабочее место тьютора / Службы заботы")
        
        col_risk, col_verb = st.columns([5, 5])

        with col_risk:
            st.markdown("**Реестр алертов Churn Risk**")
            st.caption("Студенты, сработавшие по Правилу 1 (2x Depleted) или Правилу 2 (Fragmented + CSAT <= 2):")
            
            churn_records = df[df['student_id'].isin(churn_alert_students)][
                ['student_id', 'module_id', 'energy_score', 'cohesion_score', 'legacy_homework']
            ]
            st.dataframe(churn_records.sort_values(['student_id', 'module_id']), use_container_width=True, height=400)

        with col_verb:
            st.markdown("**Лента текстовых отзывов (Open Verbatim)**")
            show_non_empty = st.checkbox("Показывать только заполненные отзывы", value=True)
            
            comments_df = filtered_df[['student_id', 'module_id', 'energy_score', 'open_feedback_text']]
            if show_non_empty:
                comments_df = comments_df[comments_df['open_feedback_text'].str.strip() != ""]
                
            st.dataframe(comments_df.sort_values('module_id', ascending=False), use_container_width=True, height=400)
