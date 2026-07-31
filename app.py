import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройки страницы
st.set_page_config(page_title="Product Health Dashboard", page_icon="📊", layout="wide")

# -------------------------------------------------------------
# Функция автоматической генерации синтетического датасета
# (Работает прямо в облаке Streamlit, если файла нет)
# -------------------------------------------------------------
def generate_synthetic_data():
    np.random.seed(42)
    n_students = 200
    student_ids = [f'STU_{1000 + i}' for i in range(1, n_students + 1)]
    modules = [f'MOD_0{i}' for i in range(1, 7)]

    comments_pool = [
        "", "", "", "", "", "",
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
            # 1. Core Pulse
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
            
            # 2. Legacy CSAT (1-5)
            base_mean = 4.5 if student_resilience == 'high' else (4.1 if student_resilience == 'medium' else 3.6)
            if cohesion == 'fragmented':
                base_mean -= 0.7
                
            legacy_speaker = int(np.clip(np.random.normal(base_mean, 0.6), 1, 5))
            legacy_platform = int(np.clip(np.random.normal(4.3, 0.6), 1, 5))
            legacy_homework = int(np.clip(np.random.normal(base_mean - 0.2, 0.8), 1, 5))
            legacy_materials = int(np.clip(np.random.normal(base_mean, 0.6), 1, 5))
            legacy_support = int(np.clip(np.random.normal(4.4, 0.7), 1, 5))
            
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

    return pd.DataFrame(data)

# Загрузка данных с автогенерацией
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('pulse_6_modules_clean.csv')
        # Проверяем, есть ли новые колонки, если нет — пересоздаем
        if 'legacy_speaker' not in df.columns:
            df = generate_synthetic_data()
    except FileNotFoundError:
        df = generate_synthetic_data()
    return df

df = load_data()

# Функция расчета процентов
def get_pct_data(data_df, score_col):
    grouped = data_df.groupby(['module_id', score_col]).size().reset_index(name='count')
    grouped['total'] = grouped.groupby('module_id')['count'].transform('sum')
    grouped['percentage'] = (grouped['count'] / grouped['total'] * 100).round(1)
    return grouped

if not df.empty:
    st.title("📊 Дашборд здоровья продукта (Hybrid MVP v1.0)")
    st.caption("Единый аналитический контур: Атомарный Пульс + Legacy CSAT + Closed-Loop")

    # Боковая панель
    st.sidebar.header("Фильтры")
    selected_modules = st.sidebar.multiselect(
        "Выберите модули:",
        options=df['module_id'].unique(),
        default=df['module_id'].unique()
    )
    filtered_df = df[df['module_id'].isin(selected_modules)]

    # Расчет Churn Risk
    df_sorted = df.sort_values(['student_id', 'module_id'])
    churn_alert_students = set()
    
    for student_id, group in df_sorted.groupby('student_id'):
        energies = group['energy_score'].tolist()
        cohesions = group['cohesion_score'].tolist()
        min_legacy = group[['legacy_speaker', 'legacy_homework', 'legacy_materials']].min(axis=1).tolist()
        
        for i in range(len(energies)):
            if i < len(energies) - 1 and energies[i] == 'depleted' and energies[i+1] == 'depleted':
                churn_alert_students.add(student_id)
            if cohesions[i] == 'fragmented' and min_legacy[i] <= 2:
                churn_alert_students.add(student_id)

    # 3 ВКЛАДКИ
    tab1, tab2, tab3 = st.tabs([
        "🟢 Вкладка 1: Пульс Здоровья (Core)", 
        "🟡 Вкладка 2: Legacy CSAT (Стейкхолдеры)", 
        "🔴 Вкладка 3: Closed-Loop & Вербатим"
    ])

    # ВКЛАДКА 1
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

    # ВКЛАДКА 2
    with tab2:
        st.subheader("Наследуемые оценки CSAT (Шкала 1–5)")
        st.caption("Раздел для мониторинга исторических показателей стейкхолдерами")

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

    # ВКЛАДКА 3
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
