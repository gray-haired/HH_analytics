import os
import sys
# Добавляем корневую директорию проекта в sys.path, чтобы можно было импортировать модули из src
# __file__ - это путь к app.py
# os.path.dirname(__file__) - это путь к dashboard/
# os.path.abspath(...) - это абсолютный путь
# os.path.join(..., '..') - это путь к корневой папке HH_analytics/
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_dir)

import streamlit as st
import clickhouse_connect
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from datetime import datetime, timedelta
from src.analytics.data_service import *


# настройка страницы
st.set_page_config(
                    page_title="HH Analytics Dashboard",
                    page_icon="📊", 
                    layout="wide",
                    initial_sidebar_state="expanded"
                )

# заголовок приложения
st.title("📊 HH Analytics - Мониторинг IT-вакансий")
st.markdown("""
**Реальная аналитическая система для отслеживания рынка труда IT-специалистов.**\n
Данные обновляются ежедневно из HH.ru и хранятся в ClickHouse Cloud.
""")

# ОСНОВНАЯ ФУНКЦИЯ

def main():
    
    # САЙДБАР С ФИЛЬТРАМИ И СТАТУСОМ
    
    with st.sidebar:
        st.header("Фильтры и настройки")
        
        # проверка подключения
        if st.button("Проверить подключение к БД"):
            success, message = test_connection()
            if success:
                st.success(f"База данных доступна. Вакансий: {message:,}")
            else:
                st.error(f"Ошибка подключения: {message}")
        
        st.markdown("---")

        # фильтр по периоду
        days_option = st.selectbox(
                                    "Период анализа",
                                    options=[30, 60, 90],
                                    index=2,  # 90 дней по умолчанию
                                    format_func=lambda x: f"{x} дней"
                                    )
        
        # Фильтр по городу
        st.subheader("Фильтр по городам")

        # ЗАГРУЗКА ДАННЫХ С УЧЕТОМ ФИЛЬТРОВ
    
    with st.spinner(f'Загрузка данных за {days_option} дней...'):
        df = load_vacancies_data(days_option)
    
    if df.empty:
        st.error("Не удалось загрузить данные. Проверьте подключение к базе.")
        return
    
    # обновление фильтра городов после загрузки данных
    with st.sidebar:
        city_options = ['Все города'] + sorted(df['city'].unique().tolist())
        selected_cities = st.multiselect(
                                            "Выберите города",
                                            options=city_options,
                                            default=['Все города']
                                        )
        
        # фильтр по опыту работы
        st.subheader("Фильтр по опыту")
        experience_options = ['Все'] + sorted(df['experience'].unique().tolist())
        selected_experience = st.multiselect(
                                                "Уровень опыта",
                                                options=experience_options,
                                                default=['Все']
                                            )

    # ПРИМЕНЕНИЕ ФИЛЬТРОВ К ДАННЫМ
    
    filtered_df = df.copy()
    
    # фильтр по городам
    if 'Все города' not in selected_cities and selected_cities:
        filtered_df = filtered_df[filtered_df['city'].isin(selected_cities)]
    
    # фильтр по опыту
    if 'Все' not in selected_experience and selected_experience:
        filtered_df = filtered_df[filtered_df['experience'].isin(selected_experience)]


    
    # КЛЮЧЕВЫЕ МЕТРИКИ С ПРАВИЛЬНОЙ ЛОГИКОЙ ЗАРПЛАТ
   
    st.success(f"Загружено {len(filtered_df):,} вакансий после фильтрации")
    
    # данные за предыдущий период для сравнения
    comparison_days = days_option
    with st.spinner('Загрузка данных для сравнения...'):
        comparison_df = load_vacancies_data(days_option * 2)
        cutoff_date = filtered_df['date'].max() - timedelta(days=days_option) if not filtered_df.empty else datetime.now()
        prev_period_df = comparison_df[comparison_df['date'] < cutoff_date] if not comparison_df.empty else pd.DataFrame()
    
    # фильтры к предыдущему периоду
    if not prev_period_df.empty:
        if 'Все города' not in selected_cities and selected_cities:
            prev_period_df = prev_period_df[prev_period_df['city'].isin(selected_cities)]
        if 'Все' not in selected_experience and selected_experience:
            prev_period_df = prev_period_df[prev_period_df['experience'].isin(selected_experience)]
    
    
    
    
    # применение к текущим данным
    current_total = len(filtered_df)
    current_with_salary = filtered_df.apply(has_salary, axis=1).sum()
    
    # применение к предыдущим данным
    prev_total = len(prev_period_df) if not prev_period_df.empty else 0
    prev_with_salary = prev_period_df.apply(has_salary, axis=1).sum() if not prev_period_df.empty else 0
    

    
    
    # серия с эффективными зарплатами
    current_salaries = filtered_df.apply(get_effective_salary, axis=1)
    current_salaries = current_salaries.dropna()
    current_median = current_salaries.median() if not current_salaries.empty else None
    
    prev_salaries = prev_period_df.apply(get_effective_salary, axis=1) if not prev_period_df.empty else pd.Series()
    prev_salaries = prev_salaries.dropna()
    prev_median = prev_salaries.median() if not prev_salaries.empty else None
    
    # РАСЧЕТ ПРОЦЕНТНЫХ ИЗМЕНЕНИЙ
    
    total_change = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
    salary_change = ((current_with_salary - prev_with_salary) / prev_with_salary * 100) if prev_with_salary > 0 else 0
    median_change = ((current_median - prev_median) / prev_median * 100) if prev_median and prev_median > 0 else 0
    
    # количество городов
    unique_cities = filtered_df['city'].nunique()
    prev_cities = prev_period_df['city'].nunique() if not prev_period_df.empty else 0
    cities_change = ((unique_cities - prev_cities) / prev_cities * 100) if prev_cities > 0 else 0
    
    # ОТОБРАЖЕНИЕ МЕТРИК
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Всего вакансий", 
            f"{current_total:,}",
            delta=f"{total_change:+.1f}%",
            help=f"По сравнению с предыдущими {days_option} днями"
        )
    
    with col2:
        salary_percent = (current_with_salary / current_total * 100) if current_total > 0 else 0
        st.metric(
            "Вакансий с зарплатой", 
            f"{current_with_salary:,}", 
            delta=f"{salary_change:+.1f}%",
            help=f"Указан salary_from ИЛИ salary_to. По сравнению с предыдущими {days_option} днями"
        )
        st.caption(f"{salary_percent:.1f}% от общего числа")
    
    with col3:
        median_display = f"{current_median:,.0f} ₽" if current_median is not None else "Н/Д"
        delta_display = f"{median_change:+.1f}%" if current_median is not None and prev_median else None
        
        st.metric(
            "Медианная зарплата", 
            median_display,
            delta=delta_display,
            help=f"Рассчитана по {len(current_salaries)} вакансиям с указанной зарплатой"
        )
        st.caption(f"На основе {len(current_salaries)} вакансий")
    
    with col4:
        st.metric(
            "Городов в выборке", 
            unique_cities,
            delta=f"{cities_change:+.1f}%",
            help=f"По сравнению с предыдущими {days_option} днями"
        )
    
    # дополнительная информация о данных
    st.info(f"""
    **О качестве данных:**
    - Вакансий с полной зарплатой (from и to): {filtered_df[filtered_df['salary_from'].notna() & filtered_df['salary_to'].notna()].shape[0]:,}
    - Вакансий только с нижней границей (from): {filtered_df[filtered_df['salary_from'].notna() & filtered_df['salary_to'].isna()].shape[0]:,}
    - Вакансий только с верхней границей (to): {filtered_df[filtered_df['salary_from'].isna() & filtered_df['salary_to'].notna()].shape[0]:,}
    """)


    # ВИЗУАЛИЗАЦИЯ 1: ДИНАМИКА ВАКАНСИЙ ПО НЕДЕЛЯМ
    st.subheader("Динамика вакансий по неделям")
    
    # группировка по неделям (начало недели - понедельник)
    filtered_df['week_start'] = filtered_df['date'].dt.to_period('W').dt.start_time
    weekly_trend = filtered_df.groupby('week_start').size().reset_index(name='count')
    
    if not weekly_trend.empty:
        fig1 = px.line(
                        weekly_trend, 
                        x='week_start', 
                        y='count',
                        title='',
                        labels={
                              'week_start': 'Неделя'
                            , 'count': 'Количество вакансий'
                            }
                      )
        
        fig1.update_layout(height=400)
        fig1.update_traces(line=dict(width=3), marker=dict(size=8))
        st.plotly_chart(fig1, width='stretch')
        
        # статистика по неделям
        col_week1, col_week2, col_week3 = st.columns(3)
        with col_week1:
            avg_weekly = weekly_trend['count'].mean()
            st.metric("Среднее за неделю", f"{avg_weekly:.0f} вакансий")
        with col_week2:
            max_week = weekly_trend['count'].max()
            st.metric("Максимум за неделю", f"{max_week:.0f} вакансий")
        with col_week3:
            total_weeks = len(weekly_trend)
            st.metric("Недель в анализе", total_weeks)
    else:
        st.warning("Нет данных для построения графика")

    # ВИЗУАЛИЗАЦИЯ 1.2: ДИНАМИКА МЕДИАННОЙ ЗАРПЛАТЫ ПО НЕДЕЛЯМ
    st.subheader("Динамика медианной зарплаты по неделям")

    # группировка по неделям с учетом зарплат
    daily_salary = filtered_df[filtered_df.apply(has_salary, axis=1)].copy()
    
    if not daily_salary.empty:
        daily_salary['effective_salary'] = daily_salary.apply(get_effective_salary, axis=1)
        daily_salary = daily_salary.dropna(subset=['effective_salary'])
        daily_salary['week_start'] = daily_salary['date'].dt.to_period('W').dt.start_time
        
        # группировка по неделям, учитывая только недели с минимум 5 вакансиями с зарплатой
        weekly_salary = (daily_salary
                            .groupby('week_start')
                            .agg({
                                'effective_salary': ['median', 'count'],
                                'date': 'count'  # общее количество вакансий за неделю
                                })
                            .reset_index()
                        )
        
        weekly_salary.columns = [
                                  'week_start'
                                , 'median_salary'
                                , 'salary_vacancies_count'
                                , 'total_vacancies_count'
                                ]
        weekly_salary = weekly_salary[weekly_salary['salary_vacancies_count'] >= 5]  # повышаем порог для недель
        
        if not weekly_salary.empty:
            # график с двумя осями Y
            fig_salary = make_subplots(
                                        specs=[[{"secondary_y": True}]],
                                        subplot_titles=("Медианная зарплата по неделям", "")
                                      )
            
            # основной график
            fig_salary.add_trace(
                go.Scatter(
                    x=weekly_salary['week_start'],
                    y=weekly_salary['median_salary'],
                    mode='lines+markers',
                    name='Медианная зарплата',
                    line=dict(color='#FF6B6B', width=3),
                    marker=dict(size=8)
                ),
                secondary_y=False
            )
            
            # вторичный график
            fig_salary.add_trace(
                go.Bar(
                    x=weekly_salary['week_start'],
                    y=weekly_salary['salary_vacancies_count'],
                    name='Вакансий с зарплатой',
                    opacity=0.3,
                    marker_color='#4ECDC4'
                ),
                secondary_y=True
            )
            
            # настройка осей и layout
            fig_salary.update_layout(
                height=500,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            fig_salary.update_yaxes(title_text="Медианная зарплата, ₽", secondary_y=False, tickformat=",")
            fig_salary.update_yaxes(title_text="Количество вакансий", secondary_y=True)
            fig_salary.update_xaxes(title_text="Неделя")
            
            st.plotly_chart(fig_salary, width='stretch')
            
            # статистика по графикам
            col_info1, col_info2, col_info3 = st.columns(3)
            
            with col_info1:
                avg_salary = weekly_salary['median_salary'].mean()
                st.metric("Средняя медианная зарплата", f"{avg_salary:,.0f} ₽")
            
            with col_info2:
                if len(weekly_salary) > 1:
                    salary_change = ((weekly_salary['median_salary'].iloc[-1] - weekly_salary['median_salary'].iloc[0]) / 
                                   weekly_salary['median_salary'].iloc[0] * 100)
                    st.metric("Изменение за период", f"{salary_change:+.1f}%")
                else:
                    st.metric("Изменение за период", "Н/Д")
            
            with col_info3:
                total_weeks = len(weekly_salary)
                st.metric("Недель с данными", total_weeks)
            
            st.caption(f"График показывает недели с минимум 5 вакансиями с указанной зарплатой. Всего недель с данными: {total_weeks}")
            
        else:
            st.warning("Недостаточно данных для построения графика зарплат. Нужны недели с минимум 5 вакансиями с указанной зарплатой.")
    else:
        st.warning("Нет данных о зарплатах за выбранный период.")
    
    # ВИЗУАЛИЗАЦИЯ 2: РАСПРЕДЕЛЕНИЕ ПО ОПЫТУ РАБОТЫ
   
    st.subheader("Распределение по опыту работы")
    
    col5, col6 = st.columns(2)
    
    with col5:
        # столбчатая диаграмма
        exp_dist = filtered_df['experience'].value_counts().reset_index()
        if not exp_dist.empty:
            fig2 = px.bar(
                            exp_dist, 
                            x='experience', 
                            y='count',
                            title='',
                            labels={'experience': 'Уровень опыта'
                                    , 'count': 'Количество'}
                        )
            st.plotly_chart(fig2, width='stretch')

    with col6:
        # круговая диаграмма
        if not exp_dist.empty:
            fig3 = px.pie(
                            exp_dist,
                            values='count',
                            names='experience',
                            title=''
                        )
            st.plotly_chart(fig3, width='stretch')


    # ВИЗУАЛИЗАЦИЯ 3: ГЕОГРАФИЧЕСКОЕ РАСПРЕДЕЛЕНИЕ

    st.subheader("Географическое распределение")
    
    city_dist = filtered_df['city'].value_counts().head(10).reset_index()
    if not city_dist.empty:
        fig4 = px.bar(
                        city_dist,
                        x='city',
                        y='count',
                        title='Топ-10 городов по количеству вакансий',
                        labels={'city': 'Город'
                            ,'count': 'Количество вакансий'}
                    )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, width='stretch')


    # ТАБЛИЦА С ДЕТАЛЬНЫМИ ДАННЫМИ
    
    st.subheader("Детальная информация о вакансиях")
    
    # только ключевые столбцы для таблицы
    display_df = filtered_df[[
                              'date'
                            , 'city'
                            , 'experience'
                            , 'company'
                            , 'salary_from'
                            , 'salary_to'
                            , 'query'
                            ]].copy()
    
    display_df['salary_from'] = display_df['salary_from'].apply(lambda x: f"{x:,.0f} ₽" if not pd.isna(x) else "Не указана")
    display_df['salary_to'] = display_df['salary_to'].apply(lambda x: f"{x:,.0f} ₽" if not pd.isna(x) else "Не указана")
    
    st.dataframe(
        display_df.head(50),
        width='stretch',
        height=400
    )
    
    # информация о последнем обновлении
    last_update = filtered_df['date'].max() if not filtered_df.empty else "Н/Д"
    st.caption(f"Данные актуальны на: {last_update.strftime('%d.%m.%Y') if not pd.isna(last_update) else 'Н/Д'}")


if __name__ == "__main__":
    main()
