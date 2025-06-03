import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh
import pytz

# 设置页面配置
st.set_page_config(
    page_title="Money Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stSlider [data-baseweb="slider"] {
        height: 10px;
    }
    .stSlider [data-baseweb="thumb"] {
        width: 20px;
        height: 20px;
    }
    .money-jar {
        position: relative;
        width: 100%;
        height: 300px;
        margin: 20px 0;
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    }
    .money-jar-fill {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(to top, #FFD700, #FFA500);
        transition: height 0.5s ease;
    }
    .money-jar-label {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2em;
        font-weight: bold;
        color: white;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.5);
        z-index: 10;
    }
    .stat-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        text-align: center;
    }
    .stat-value {
        font-size: 2.5em;
        font-weight: bold;
        margin: 10px 0;
    }
    .stat-label {
        font-size: 1em;
        color: #666;
    }
    .time-period {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #4361ee;
    }
    .language-selector {
        position: absolute;
        top: 0.5rem;
        right: 1rem;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# 初始化会话状态
if 'daily_salary' not in st.session_state:
    st.session_state.daily_salary = 250.0

if 'work_periods' not in st.session_state:
    # 默认工作时间段：上午9:00-12:00，下午14:00-18:00
    st.session_state.work_periods = [
        {"start_hour": 9, "start_minute": 0, "end_hour": 12, "end_minute": 0},
        {"start_hour": 14, "start_minute": 0, "end_hour": 18, "end_minute": 0}
    ]

if 'is_running' not in st.session_state:
    st.session_state.is_running = False

if 'start_time' not in st.session_state:
    st.session_state.start_time = None

if 'money_per_second' not in st.session_state:
    st.session_state.money_per_second = 0

if 'seconds_per_dollar' not in st.session_state:
    st.session_state.seconds_per_dollar = 0

if 'total_work_seconds' not in st.session_state:
    st.session_state.total_work_seconds = 0

# 添加时区设置
if 'timezone' not in st.session_state:
    st.session_state.timezone = 'Asia/Shanghai'  # 默认东八区

# 添加语言选择
if 'language' not in st.session_state:
    st.session_state.language = "zh"

# 语言文本字典
text = {
    "zh": {
        "title": "💰 Money Tracker",
        "subtitle": "实时追踪你的工作收入",
        "settings": "⚙️ 设置",
        "timezone_setting": "🌍 时区设置",
        "daily_salary": "日薪 ($)",
        "work_time_settings": "📅 工作时间设置",
        "work_time_desc": "使用滑动条设置每个工作时间段，可以添加多个时间段来表示不连续的工作时间（如午休）",
        "period": "时间段",
        "start_time": "开始时间",
        "end_time": "结束时间",
        "hours": "小时",
        "minutes": "分钟",
        "delete_period": "删除此时间段",
        "add_period": "➕ 添加时间段",
        "start_tracking": "🚀 开始追踪",
        "reset": "🔄 重置",
        "current_time": "📌 当前时间",
        "work_periods_today": "📊 今日工作时间段",
        "work_time": "工作时间",
        "non_work_time": "非工作时间",
        "status": "状态",
        "income_progress": "💰 今日收入进度",
        "progress": "收入进度",
        "detailed_stats": "📈 详细统计",
        "earned_amount": "已赚取金额",
        "time_per_dollar": "每赚$1所需时间",
        "progress_today": "今日进度",
        "seconds": "秒",
        "setup_prompt": "👈 请在左侧设置您的日薪和工作时间，然后点击'开始追踪'按钮开始记录您的收入。",
        "work_periods_preview": "📋 工作时间段预览",
        "total_work_time": "总工作时间",
        "realtime_info": "⏱️ 实时信息",
        "is_work_time": "✅ 当前是工作时间",
        "not_work_time": "⚠️ 当前不是工作时间",
        "work_time_details": "🗓️ 工作时间详情",
        "salary_info": "💵 薪资信息",
        "daily_salary_info": "日薪",
        "hourly_salary": "小时薪资",
        "minute_salary": "分钟薪资",
        "app_description": "📝 应用说明",
        "app_intro": "**Money Tracker** 帮助您实时追踪工作收入，让您更直观地了解自己的收入进度。",
        "features": "**特点**:",
        "feature_1": "- 支持设置多个工作时间段（考虑午休等情况）",
        "feature_2": "- 使用滑动条轻松调整工作时间（精确到分钟）",
        "feature_3": "- 实时计算已赚取金额（自动刷新）",
        "feature_4": "- 可视化显示收入进度",
        "feature_5": "- 详细统计信息",
        "feature_6": "- 支持时区设置",
        "how_to_use": "**使用方法**:",
        "step_1": "1. 在左侧设置您的时区和日薪",
        "step_2": "2. 使用滑动条设置工作时间段（精确到分钟）",
        "step_3": "3. 点击开始追踪按钮",
        "step_4": "4. 实时查看您的收入进度",
        "language": "🌐 语言"
    },
    "en": {
        "title": "💰 Money Tracker",
        "subtitle": "Track your work income in real-time",
        "settings": "⚙️ Settings",
        "timezone_setting": "🌍 Timezone Settings",
        "daily_salary": "Daily Salary ($)",
        "work_time_settings": "📅 Work Time Settings",
        "work_time_desc": "Use sliders to set each work period. You can add multiple periods to represent non-continuous work times (e.g., lunch break)",
        "period": "Period",
        "start_time": "Start Time",
        "end_time": "End Time",
        "hours": "hours",
        "minutes": "minutes",
        "delete_period": "Delete this period",
        "add_period": "➕ Add Period",
        "start_tracking": "🚀 Start Tracking",
        "reset": "🔄 Reset",
        "current_time": "📌 Current Time",
        "work_periods_today": "📊 Today's Work Periods",
        "work_time": "Work Time",
        "non_work_time": "Non-Work Time",
        "status": "Status",
        "income_progress": "💰 Today's Income Progress",
        "progress": "Progress",
        "detailed_stats": "📈 Detailed Statistics",
        "earned_amount": "Earned Amount",
        "time_per_dollar": "Time per $1",
        "progress_today": "Today's Progress",
        "seconds": "sec",
        "setup_prompt": "👈 Please set your timezone, daily salary and work periods on the left, then click 'Start Tracking' to begin recording your income.",
        "work_periods_preview": "📋 Work Periods Preview",
        "total_work_time": "Total Work Time",
        "realtime_info": "⏱️ Real-time Information",
        "is_work_time": "✅ Currently in Work Time",
        "not_work_time": "⚠️ Currently Not in Work Time",
        "work_time_details": "🗓️ Work Time Details",
        "salary_info": "💵 Salary Information",
        "daily_salary_info": "Daily Salary",
        "hourly_salary": "Hourly Rate",
        "minute_salary": "Minute Rate",
        "app_description": "📝 App Description",
        "app_intro": "**Money Tracker** helps you track your work income in real-time, giving you a visual understanding of your earning progress.",
        "features": "**Features**:",
        "feature_1": "- Support for multiple work periods (accounting for breaks)",
        "feature_2": "- Easy adjustment of work times using sliders (minute precision)",
        "feature_3": "- Real-time calculation of earned amount (auto-refresh)",
        "feature_4": "- Visual display of income progress",
        "feature_5": "- Detailed statistics",
        "feature_6": "- Timezone support",
        "how_to_use": "**How to Use**:",
        "step_1": "1. Set your timezone and daily salary on the left",
        "step_2": "2. Use sliders to set work periods (minute precision)",
        "step_3": "3. Click the 'Start Tracking' button",
        "step_4": "4. View your income progress in real-time",
        "language": "🌐 Language"
    }
}

# 获取当前语言的文本
def get_text(key):
    return text[st.session_state.language][key]

# 获取当前时区的时间
def get_current_time():
    tz = pytz.timezone(st.session_state.timezone)
    return datetime.now(tz)

# 计算工作总秒数
def calculate_work_seconds(periods):
    total_seconds = 0
    for period in periods:
        start_minutes = period["start_hour"] * 60 + period["start_minute"]
        end_minutes = period["end_hour"] * 60 + period["end_minute"]
        total_seconds += (end_minutes - start_minutes) * 60  # 分钟转秒
    return total_seconds

# 计算已赚取的金额
def calculate_earned_money():
    if not st.session_state.is_running:
        return 0.0
    
    now = get_current_time()
    elapsed_work_seconds = 0
    
    # 计算今天已经过去的工作时间
    for period in st.session_state.work_periods:
        start_hour, start_minute = period["start_hour"], period["start_minute"]
        end_hour, end_minute = period["end_hour"], period["end_minute"]
        
        # 转换为今天的日期时间
        period_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        period_end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        # 如果当前时间在这个时间段之前，跳过
        if now < period_start:
            continue
        
        # 如果当前时间在这个时间段内
        if period_start <= now < period_end:
            elapsed_work_seconds += (now - period_start).total_seconds()
        # 如果当前时间在这个时间段之后
        elif now >= period_end:
            elapsed_work_seconds += (period_end - period_start).total_seconds()
    
    return elapsed_work_seconds * st.session_state.money_per_second

# 开始追踪
def start_tracking():
    st.session_state.is_running = True
    current_time = get_current_time()
    st.session_state.start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 计算总工作秒数
    st.session_state.total_work_seconds = calculate_work_seconds(st.session_state.work_periods)
    
    # 计算每秒赚取的金额
    st.session_state.money_per_second = st.session_state.daily_salary / st.session_state.total_work_seconds
    
    # 计算赚取1美元所需的时间
    st.session_state.seconds_per_dollar = 1 / st.session_state.money_per_second

# 重置追踪
def reset_tracking():
    st.session_state.is_running = False
    st.session_state.start_time = None

# 添加工作时间段
def add_work_period():
    st.session_state.work_periods.append({"start_hour": 9, "start_minute": 0, "end_hour": 18, "end_minute": 0})

# 删除工作时间段
def remove_work_period(index):
    if len(st.session_state.work_periods) > 1:
        st.session_state.work_periods.pop(index)

# 切换语言
def switch_language():
    if st.session_state.language == "zh":
        st.session_state.language = "en"
    else:
        st.session_state.language = "zh"

# 自动刷新设置
if st.session_state.is_running:
    # 每5秒刷新一次页面
    count = st_autorefresh(interval=1000, limit=None, key="money_tracker_refresh")

# 语言选择器（放在页面顶部）
col_lang, col_title = st.columns([1, 10])
with col_lang:
    if st.button("🇨🇳 / 🇺🇸", help=get_text("language")):
        switch_language()
        st.rerun()

# 主页面
with col_title:
    st.title(get_text("title"))
    st.markdown(f"### {get_text('subtitle')}")

# 侧边栏设置
with st.sidebar:
    st.header(get_text("settings"))
    
    # 时区设置
    st.markdown(f"### {get_text('timezone_setting')}")
    timezone_options = {
        'Asia/Shanghai': '🇨🇳 中国标准时间 (UTC+8)',
        'America/New_York': '🇺🇸 美国东部时间 (UTC-5/-4)',
        'America/Los_Angeles': '🇺🇸 美国西部时间 (UTC-8/-7)',
        'Europe/London': '🇬🇧 英国时间 (UTC+0/+1)',
        'Europe/Paris': '🇫🇷 欧洲中部时间 (UTC+1/+2)',
        'Asia/Tokyo': '🇯🇵 日本标准时间 (UTC+9)',
        'Australia/Sydney': '🇦🇺 澳大利亚东部时间 (UTC+10/+11)'
    }
    
    selected_timezone = st.selectbox(
        "选择时区 / Select Timezone",
        options=list(timezone_options.keys()),
        index=list(timezone_options.keys()).index(st.session_state.timezone),
        format_func=lambda x: timezone_options[x],
        disabled=st.session_state.is_running
    )
    st.session_state.timezone = selected_timezone
    
    # 日薪设置
    st.session_state.daily_salary = st.number_input(
        get_text("daily_salary"),
        min_value=1.0,
        max_value=10000.0,
        value=st.session_state.daily_salary,
        step=10.0,
        format="%.2f",
        disabled=st.session_state.is_running
    )
    
    st.markdown(f"### {get_text('work_time_settings')}")
    st.markdown(get_text("work_time_desc"))
    
    # 工作时间段设置
    for i, period in enumerate(st.session_state.work_periods):
        with st.container():
            st.markdown(f"**{get_text('period')} {i+1}**")
            
            # 开始时间设置
            col1, col2 = st.columns(2)
            with col1:
                start_hour = st.slider(
                    f"{get_text('start_time')} - {get_text('hours')}",
                    min_value=0,
                    max_value=23,
                    value=period["start_hour"],
                    step=1,
                    disabled=st.session_state.is_running,
                    key=f"start_hour_{i}"
                )
            with col2:
                start_minute = st.slider(
                    f"{get_text('start_time')} - {get_text('minutes')}",
                    min_value=0,
                    max_value=59,
                    value=period["start_minute"],
                    step=1,
                    disabled=st.session_state.is_running,
                    key=f"start_minute_{i}"
                )
            
            # 结束时间设置
            col3, col4 = st.columns(2)
            with col3:
                end_hour = st.slider(
                    f"{get_text('end_time')} - {get_text('hours')}",
                    min_value=start_hour if start_minute < 59 else start_hour + 1,
                    max_value=23,
                    value=max(start_hour if start_minute < 59 else start_hour + 1, period["end_hour"]),
                    step=1,
                    disabled=st.session_state.is_running,
                    key=f"end_hour_{i}"
                )
            with col4:
                min_end_minute = 1 if end_hour == start_hour else 0
                end_minute = st.slider(
                    f"{get_text('end_time')} - {get_text('minutes')}",
                    min_value=min_end_minute,
                    max_value=59,
                    value=max(min_end_minute, period["end_minute"]),
                    step=1,
                    disabled=st.session_state.is_running,
                    key=f"end_minute_{i}"
                )
            
            # 更新时间段
            st.session_state.work_periods[i]["start_hour"] = start_hour
            st.session_state.work_periods[i]["start_minute"] = start_minute
            st.session_state.work_periods[i]["end_hour"] = end_hour
            st.session_state.work_periods[i]["end_minute"] = end_minute
            
            # 显示时间段
            start_time_str = f"{start_hour:02d}:{start_minute:02d}"
            end_time_str = f"{end_hour:02d}:{end_minute:02d}"
            duration_minutes = (end_hour * 60 + end_minute) - (start_hour * 60 + start_minute)
            duration_hours = duration_minutes // 60
            duration_mins = duration_minutes % 60
            
            st.markdown(f"🕒 {start_time_str} - {end_time_str} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})")
            
            # 删除按钮
            if not st.session_state.is_running and len(st.session_state.work_periods) > 1:
                if st.button(get_text("delete_period"), key=f"remove_{i}"):
                    remove_work_period(i)
                    st.rerun()
        
        st.markdown("---")
    
    # 添加时间段按钮
    if not st.session_state.is_running:
        if st.button(get_text("add_period")):
            add_work_period()
            st.rerun()
    
    # 开始/重置按钮
    if not st.session_state.is_running:
        if st.button(get_text("start_tracking"), use_container_width=True):
            start_tracking()
            st.rerun()
    else:
        if st.button(get_text("reset"), use_container_width=True):
            reset_tracking()
            st.rerun()

# 主内容区
col1, col2 = st.columns([2, 1])

with col1:
    # 当前时间和工作状态
    current_time = get_current_time().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"### {get_text('current_time')}: {current_time}")
    
    # 工作时间段可视化
    if st.session_state.is_running:
        st.markdown(f"### {get_text('work_periods_today')}")
        
        # 创建24小时时间轴（以分钟为单位）
        minutes_in_day = list(range(0, 24 * 60, 30))  # 每30分钟一个点
        is_work_minute = [False] * len(minutes_in_day)
        
        # 标记工作时间
        for period in st.session_state.work_periods:
            start_minutes = period["start_hour"] * 60 + period["start_minute"]
            end_minutes = period["end_hour"] * 60 + period["end_minute"]
            for i, minute in enumerate(minutes_in_day):
                if start_minutes <= minute < end_minutes:
                    is_work_minute[i] = True
        
        # 创建数据框
        df = pd.DataFrame({
            "minute": minutes_in_day,
            "hour": [m // 60 + (m % 60) / 60 for m in minutes_in_day],
            "is_work": is_work_minute,
            "status": [get_text("work_time") if w else get_text("non_work_time") for w in is_work_minute]
        })
        
        # 当前时间
        current_time_obj = get_current_time()
        current_minute = current_time_obj.hour * 60 + current_time_obj.minute
        current_hour_decimal = current_minute / 60
        
        # 创建图表
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('hour:Q', title=get_text('hours'), axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count():Q', title=None, axis=None),
            color=alt.Color('status:N', 
                          scale=alt.Scale(domain=[get_text('work_time'), get_text('non_work_time')],
                                         range=['#4361ee', '#e9ecef']),
                          legend=alt.Legend(title=get_text("status"))),
            tooltip=['hour:Q', 'status:N']
        ).properties(
            width=600,
            height=100
        )
        
        # 添加当前时间指示器
        current_time_indicator = alt.Chart(pd.DataFrame({'hour': [current_hour_decimal]})).mark_rule(
            color='red',
            strokeWidth=2
        ).encode(
            x='hour:Q'
        )
        
        st.altair_chart(chart + current_time_indicator, use_container_width=True)
        
        # 计算已赚取的金额
        earned_money = calculate_earned_money()
        progress = (earned_money / st.session_state.daily_salary) * 100
        
        # 存钱罐效果
        st.markdown(f"### {get_text('income_progress')}")
        
        # 使用Plotly创建更漂亮的存钱罐效果
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=progress,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': get_text("progress"), 'font': {'size': 24}},
            delta={'reference': 0, 'increasing': {'color': "#4361ee"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "#FFD700"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 25], 'color': '#f8f9fa'},
                    {'range': [25, 50], 'color': '#e9ecef'},
                    {'range': [50, 75], 'color': '#dee2e6'},
                    {'range': [75, 100], 'color': '#ced4da'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 100
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=50, b=20),
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 统计信息
        st.markdown(f"### {get_text('detailed_stats')}")
        stats_cols = st.columns(3)
        
        with stats_cols[0]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{get_text('earned_amount')}</div>
                <div class="stat-value" style="color: #FF5722;">$%.2f</div>
            </div>
            """ % earned_money, unsafe_allow_html=True)
        
        with stats_cols[1]:
            minutes = int(st.session_state.seconds_per_dollar // 60)
            seconds = int(st.session_state.seconds_per_dollar % 60)
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{get_text('time_per_dollar')}</div>
                <div class="stat-value" style="color: #2196F3;">{minutes}{get_text('minutes')}{seconds}{get_text('seconds')}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_cols[2]:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">{get_text('progress_today')}</div>
                <div class="stat-value" style="color: #4CAF50;">%.2f%%</div>
            </div>
            """ % progress, unsafe_allow_html=True)
    else:
        # 未开始追踪时的提示
        st.info(get_text("setup_prompt"))
        
        # 工作时间段预览
        st.markdown(f"### {get_text('work_periods_preview')}")
        for i, period in enumerate(st.session_state.work_periods):
            start_time_str = f"{period['start_hour']:02d}:{period['start_minute']:02d}"
            end_time_str = f"{period['end_hour']:02d}:{period['end_minute']:02d}"
            duration_minutes = (period['end_hour'] * 60 + period['end_minute']) - (period['start_hour'] * 60 + period['start_minute'])
            duration_hours = duration_minutes // 60
            duration_mins = duration_minutes % 60
            
            st.markdown(f"""
            <div class="time-period">
                <h4>{get_text('period')} {i+1}</h4>
                <p>🕒 {start_time_str} - {end_time_str} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 计算总工作时间
        total_minutes = sum((period["end_hour"] * 60 + period["end_minute"]) - (period["start_hour"] * 60 + period["start_minute"]) for period in st.session_state.work_periods)
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        st.markdown(f"**{get_text('total_work_time')}**: {total_hours}{get_text('hours')}{total_mins}{get_text('minutes')}")

with col2:
    # 右侧信息面板
    if st.session_state.is_running:
        # 实时更新部分
        st.markdown(f"### {get_text('realtime_info')}")
        
        # 检查当前是否在工作时间
        now = get_current_time()
        current_minute = now.hour * 60 + now.minute
        is_currently_working = False
        
        for period in st.session_state.work_periods:
            start_minutes = period["start_hour"] * 60 + period["start_minute"]
            end_minutes = period["end_hour"] * 60 + period["end_minute"]
            if start_minutes <= current_minute < end_minutes:
                is_currently_working = True
                break
        
        if is_currently_working:
            st.success(get_text("is_work_time"))
        else:
            st.warning(get_text("not_work_time"))
        
        # 显示工作时间详情
        st.markdown(f"### {get_text('work_time_details')}")
        for i, period in enumerate(st.session_state.work_periods):
            start_time_str = f"{period['start_hour']:02d}:{period['start_minute']:02d}"
            end_time_str = f"{period['end_hour']:02d}:{period['end_minute']:02d}"
            duration_minutes = (period['end_hour'] * 60 + period['end_minute']) - (period['start_hour'] * 60 + period['start_minute'])
            duration_hours = duration_minutes // 60
            duration_mins = duration_minutes % 60
            
            st.markdown(f"""
            <div class="time-period">
                <h4>{get_text('period')} {i+1}</h4>
                <p>🕒 {start_time_str} - {end_time_str} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 计算总工作时间
        total_minutes = sum((period["end_hour"] * 60 + period["end_minute"]) - (period["start_hour"] * 60 + period["start_minute"]) for period in st.session_state.work_periods)
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        st.markdown(f"**{get_text('total_work_time')}**: {total_hours}{get_text('hours')}{total_mins}{get_text('minutes')}")
        
        # 显示日薪信息
        st.markdown(f"### {get_text('salary_info')}")
        st.markdown(f"**{get_text('daily_salary_info')}**: ${st.session_state.daily_salary:.2f}")
        if total_minutes > 0:
            st.markdown(f"**{get_text('hourly_salary')}**: ${st.session_state.daily_salary / (total_minutes / 60):.2f}/{get_text('hours')}")
            st.markdown(f"**{get_text('minute_salary')}**: ${st.session_state.daily_salary / total_minutes:.4f}/{get_text('minutes')}")
    else:
        # 应用说明
        st.markdown(f"### {get_text('app_description')}")
        st.markdown(f"""
        {get_text('app_intro')}
        
        {get_text('features')}
        {get_text('feature_1')}
        {get_text('feature_2')}
        {get_text('feature_3')}
        {get_text('feature_4')}
        {get_text('feature_5')}
        {get_text('feature_6')}
        
        {get_text('how_to_use')}
        {get_text('step_1')}
        {get_text('step_2')}
        {get_text('step_3')}
        {get_text('step_4')}
        """)