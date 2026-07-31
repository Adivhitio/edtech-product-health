import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Настройки страницы
st.set_page_config(page_title="Product Health Dashboard", page_icon="📊", layout="wide")

# -------------------------------------------------------------
# Функция автоматической генерации синтетического датасета
# (Работает прямо в облаке Streamlit)
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
        if 'legacy_speaker' not in df.columns:
            df = generate_synthetic_data()
    except FileNotFoundError:
        df = generate_synthetic_data()
    return df

df = load_data()

# Функция расчета процентов для атомарных вопросов
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
        "🟡 Вкладка 2: Legacy CSAT & Структура", 
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
        st.subheader("🟡 Наследуемые оценки CSAT (Шкала 1–5): Распределения и Фокусный анализ")
        st.caption("Анализ структурного распределения (Top-2 Box, Bottom-2 Box) вместо слепого доверия среднему балу.")

        segment_filter = st.radio(
            "Срез когорты для анализа:",
            ["Все студенты", "Только с историей спешки (Rushed)", "Только в состоянии истощения (Depleted)"],
            horizontal=True
        )

        df_legacy = filtered_df.copy()
        if segment_filter == "Только с историей спешки (Rushed)":
            df_legacy = df_legacy[df_legacy['pacing_score'] == 'rushed']
        elif segment_filter == "Только в состоянии истощения (Depleted)":
            df_legacy = df_legacy[df_legacy['energy_score'] == 'depleted']

        legacy_cols_map = {
            'legacy_speaker': 'Спикер',
            'legacy_platform': 'Платформа', 
            'legacy_homework': 'Домашнее задание', 
            'legacy_materials': 'Материалы', 
            'legacy_support': 'Служба поддержки'
        }

        # 1. Общий структурный обзор по всем вопросам
        summary_rows = []
        for col_id, col_name in legacy_cols_map.items():
            if len(df_legacy) > 0:
                mean_val = df_legacy[col_id].mean()
                median_val = df_legacy[col_id].median()
                top2_pct = (df_legacy[col_id].isin([4, 5]).sum() / len(df_legacy)) * 100
                bot2_pct = (df_legacy[col_id].isin([1, 2]).sum() / len(df_legacy)) * 100
            else:
                mean_val, median_val, top2_pct, bot2_pct = 0, 0, 0, 0
                
            summary_rows.append({
                'Вопрос': col_name,
                'Средний балл': round(mean_val, 2),
                'Медиана': int(median_val) if len(df_legacy) > 0 else 0,
                'Top-2 Box (% оценок 4-5)': f"{top2_pct:.1f}%",
                'Bottom-2 Box (% оценок 1-2)': f"{bot2_pct:.1f}%"
            })
        
        summary_df = pd.DataFrame(summary_rows)

        st.markdown("### 1. Общий обзор унаследованных вопросов")
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("---")

        # 2. ФОКУСНЫЙ АНАЛИЗ ОТДЕЛЬНОГО ВОПРОСА
        st.markdown("### 2. 🔍 Фокусный анализ конкретного вопроса")
        selected_q_name = st.selectbox(
            "Выберите вопрос для детального разбора распределения оценок:",
            options=list(legacy_cols_map.values())
        )
        
        selected_q_id = [k for k, v in legacy_cols_map.items() if v == selected_q_name][0]

        q_module_data = []
        for mod_id in df_legacy['module_id'].unique():
            mod_sub = df_legacy[df_legacy['module_id'] == mod_id]
            tot = len(mod_sub)
            for score in [1, 2, 3, 4, 5]:
                sc_count = (mod_sub[selected_q_id] == score).sum()
                sc_pct = (sc_count / tot * 100) if tot > 0 else 0
                q_module_data.append({
                    'module_id': mod_id,
                    'score': str(score),
                    'count': sc_count,
                    'percentage': round(sc_pct, 1)
                })

        q_df = pd.DataFrame(q_module_data)

        col_f1, col_f2 = st.columns([6, 4])

        with col_f1:
            st.markdown(f"**Распределение всех оценок (1–5) по модулям: «{selected_q_name}»**")
            color_map_scores = {
                '1': '#D32F2F', # Красный
                '2': '#F57C00', # Оранжевый
                '3': '#FBC02D', # Желтый
                '4': '#388E3C', # Светло-зеленый
                '5': '#1B5E20'  # Темно-зеленый
            }
            fig_q_dist = px.bar(
                q_df, x='module_id', y='percentage', color='score',
                color_discrete_map=color_map_scores,
                labels={'module_id': 'Модуль', 'percentage': 'Доля (%)', 'score': 'Оценка'},
                hover_data={'count': True, 'percentage': ':.1f%'}
            )
            fig_q_dist.update_yaxes(ticksuffix="%")
            st.plotly_chart(fig_q_dist, use_container_width=True)

        with col_f2:
            st.markdown(f"**Доли оценок (%) по модулям: «{selected_q_name}»**")
            piv_table = q_df.pivot(index='module_id', columns='score', values='percentage').fillna(0)
            piv_table.columns = [f"Оценка {col} (%)" for col in piv_table.columns]
            st.dataframe(piv_table, use_container_width=True)

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
