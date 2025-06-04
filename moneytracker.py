import streamlit as st
import time
from datetime import datetime, timedelta, time as dt_time
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
    .time-input-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4361ee;
    }
    .time-preset-btn {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 5px;
        padding: 5px 10px;
        margin: 2px;
        cursor: pointer;
        font-size: 12px;
    }
    .time-preset-btn:hover {
        background-color: #2196f3;
        color: white;
    }
    .timeline-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .timeline-hour {
        display: inline-block;
        width: 30px;
        height: 20px;
        margin: 1px;
        text-align: center;
        font-size: 10px;
        border-radius: 3px;
        cursor: pointer;
    }
    .timeline-work {
        background-color: #4caf50;
        color: white;
    }
    .timeline-break {
        background-color: #f5f5f5;
        color: #666;
    }
    .timeline-selected {
        background-color: #2196f3;
        color: white;
        border: 2px solid #1976d2;
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
    st.session_state.daily_salary = 300.0

if 'work_periods' not in st.session_state:
    # 默认工作时间段：上午9:00-12:00，下午14:00-18:00
    st.session_state.work_periods = [
        {"start_time": dt_time(9, 0), "end_time": dt_time(12, 0)},
        {"start_time": dt_time(14, 0), "end_time": dt_time(18, 0)}
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

# 预设工作时间模板
WORK_TIME_PRESETS = {
    "zh": {
        "标准工作日 (9-18)": [(dt_time(9, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(18, 0))],
        "早班 (8-17)": [(dt_time(8, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(17, 0))],
        "晚班 (10-19)": [(dt_time(10, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(19, 0))],
        "弹性工作 (9-17)": [(dt_time(9, 0), dt_time(12, 0)), (dt_time(14, 0), dt_time(17, 0))],
        "连续工作 (9-18)": [(dt_time(9, 0), dt_time(18, 0))],
        "半天工作 (9-13)": [(dt_time(9, 0), dt_time(13, 0))],
        "自定义": []
    },
    "en": {
        "Standard (9-18)": [(dt_time(9, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(18, 0))],
        "Early Shift (8-17)": [(dt_time(8, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(17, 0))],
        "Late Shift (10-19)": [(dt_time(10, 0), dt_time(12, 0)), (dt_time(13, 0), dt_time(19, 0))],
        "Flexible (9-17)": [(dt_time(9, 0), dt_time(12, 0)), (dt_time(14, 0), dt_time(17, 0))],
        "Continuous (9-18)": [(dt_time(9, 0), dt_time(18, 0))],
        "Half Day (9-13)": [(dt_time(9, 0), dt_time(13, 0))],
        "Custom": []
    }
}

# 语言文本字典
text = {
    "zh": {
        "title": "💰 Money Tracker",
        "subtitle": "实时追踪你的工作收入",
        "settings": "⚙️ 设置",
        "timezone_setting": "🌍 时区设置",
        "daily_salary": "日薪 ($)",
        "work_time_settings": "📅 工作时间设置",
        "work_time_desc": "选择预设模板或自定义工作时间段",
        "preset_templates": "📋 预设模板",
        "custom_periods": "🛠️ 自定义时间段",
        "period": "时间段",
        "start_time": "开始时间",
        "end_time": "结束时间",
        "add_period": "➕ 添加时间段",
        "delete_period": "🗑️ 删除",
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
        "minutes": "分钟",
        "seconds": "秒",
        "hours": "小时",
        "setup_prompt": "👈 请在左侧设置您的时区、日薪和工作时间，然后点击'开始追踪'按钮开始记录您的收入。",
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
        "feature_1": "- 支持预设工作时间模板，一键设置",
        "feature_2": "- 直观的时间输入和可视化时间轴",
        "feature_3": "- 实时计算已赚取金额（自动刷新）",
        "feature_4": "- 可视化显示收入进度",
        "feature_5": "- 详细统计信息",
        "feature_6": "- 支持时区设置",
        "how_to_use": "**使用方法**:",
        "step_1": "1. 选择预设工作时间模板或自定义",
        "step_2": "2. 设置您的时区和日薪",
        "step_3": "3. 点击开始追踪按钮",
        "step_4": "4. 实时查看您的收入进度",
        "language": "🌐 语言",
        "time_format_error": "⚠️ 时间格式错误，请使用 HH:MM 格式（如：09:30）",
        "time_range_error": "⚠️ 结束时间必须晚于开始时间",
        "visual_timeline": "📊 可视化时间轴"
    },
    "en": {
        "title": "💰 Money Tracker",
        "subtitle": "Track your work income in real-time",
        "settings": "⚙️ Settings",
        "timezone_setting": "🌍 Timezone Settings",
        "daily_salary": "Daily Salary ($)",
        "work_time_settings": "📅 Work Time Settings",
        "work_time_desc": "Choose preset templates or customize work periods",
        "preset_templates": "📋 Preset Templates",
        "custom_periods": "🛠️ Custom Periods",
        "period": "Period",
        "start_time": "Start Time",
        "end_time": "End Time",
        "add_period": "➕ Add Period",
        "delete_period": "🗑️ Delete",
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
        "minutes": "min",
        "seconds": "sec",
        "hours": "hours",
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
        "feature_1": "- Preset work time templates for quick setup",
        "feature_2": "- Intuitive time input and visual timeline",
        "feature_3": "- Real-time calculation of earned amount (auto-refresh)",
        "feature_4": "- Visual display of income progress",
        "feature_5": "- Detailed statistics",
        "feature_6": "- Timezone support",
        "how_to_use": "**How to Use**:",
        "step_1": "1. Choose preset work time template or customize",
        "step_2": "2. Set your timezone and daily salary",
        "step_3": "3. Click the 'Start Tracking' button",
        "step_4": "4. View your income progress in real-time",
        "language": "🌐 Language",
        "time_format_error": "⚠️ Invalid time format, please use HH:MM format (e.g., 09:30)",
        "time_range_error": "⚠️ End time must be later than start time",
        "visual_timeline": "📊 Visual Timeline"
    }
}

# 获取当前语言的文本
def get_text(key):
    return text[st.session_state.language][key]

# 获取当前时区的时间
def get_current_time():
    tz = pytz.timezone(st.session_state.timezone)
    return datetime.now(tz)

# 时间对象转换为分钟数
def time_to_minutes(time_obj):
    if time_obj is None:
        return None
    return time_obj.hour * 60 + time_obj.minute

# 分钟数转换为时间字符串
def minutes_to_time_str(minutes):
    hour = minutes // 60
    minute = minutes % 60
    return f"{hour:02d}:{minute:02d}"

# 计算工作总秒数
def calculate_work_seconds(periods):
    total_seconds = 0
    for period in periods:
        start_minutes = time_to_minutes(period["start_time"])
        end_minutes = time_to_minutes(period["end_time"])
        if start_minutes is not None and end_minutes is not None:
            total_seconds += (end_minutes - start_minutes) * 60
    return total_seconds

# 计算已赚取的金额
def calculate_earned_money():
    if not st.session_state.is_running:
        return 0.0
    
    now = get_current_time()
    elapsed_work_seconds = 0
    
    for period in st.session_state.work_periods:
        start_minutes = time_to_minutes(period["start_time"])
        end_minutes = time_to_minutes(period["end_time"])
        
        if start_minutes is None or end_minutes is None:
            continue
            
        start_hour, start_minute = start_minutes // 60, start_minutes % 60
        end_hour, end_minute = end_minutes // 60, end_minutes % 60
        
        period_start = now.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        period_end = now.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        
        if now < period_start:
            continue
        
        if period_start <= now < period_end:
            elapsed_work_seconds += (now - period_start).total_seconds()
        elif now >= period_end:
            elapsed_work_seconds += (period_end - period_start).total_seconds()
    
    return elapsed_work_seconds * st.session_state.money_per_second

# 开始追踪
def start_tracking():
    st.session_state.is_running = True
    current_time = get_current_time()
    st.session_state.start_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    st.session_state.total_work_seconds = calculate_work_seconds(st.session_state.work_periods)
    
    if st.session_state.total_work_seconds > 0:
        st.session_state.money_per_second = st.session_state.daily_salary / st.session_state.total_work_seconds
        st.session_state.seconds_per_dollar = 1 / st.session_state.money_per_second

# 重置追踪
def reset_tracking():
    st.session_state.is_running = False
    st.session_state.start_time = None

# 应用预设模板
def apply_preset_template(template_name):
    presets = WORK_TIME_PRESETS[st.session_state.language]
    if template_name in presets and presets[template_name]:
        st.session_state.work_periods = [
            {"start_time": start, "end_time": end} 
            for start, end in presets[template_name]
        ]

# 添加工作时间段
def add_work_period():
    st.session_state.work_periods.append({"start_time": dt_time(9, 0), "end_time": dt_time(18, 0)})

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

# 生成可视化时间轴
def generate_timeline_html():
    html = '<div class="timeline-container">'
    html += f'<h4>{get_text("visual_timeline")}</h4>'
    html += '<div style="display: flex; flex-wrap: wrap; gap: 2px;">'
    
    # 创建24小时的时间块
    for hour in range(24):
        is_work_hour = False
        for period in st.session_state.work_periods:
            start_minutes = time_to_minutes(period["start_time"])
            end_minutes = time_to_minutes(period["end_time"])
            if start_minutes is not None and end_minutes is not None:
                if start_minutes <= hour * 60 < end_minutes:
                    is_work_hour = True
                    break
        
        css_class = "timeline-work" if is_work_hour else "timeline-break"
        html += f'<div class="timeline-hour {css_class}" title="{hour:02d}:00">{hour:02d}</div>'
    
    html += '</div></div>'
    return html

# 自动刷新设置
if st.session_state.is_running:
    count = st_autorefresh(interval=5000, limit=None, key="money_tracker_refresh")

# 语言选择器
col_lang, col_title = st.columns([1, 10])
with col_lang:
    if st.button("🇨🇳 / 🇺🇸", help=get_text("language")):
        switch_language()
        st.rerun()

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
    
    # 预设模板选择
    if not st.session_state.is_running:
        st.markdown(f"#### {get_text('preset_templates')}")
        presets = WORK_TIME_PRESETS[st.session_state.language]
        
        cols = st.columns(2)
        for i, (template_name, periods) in enumerate(presets.items()):
            col = cols[i % 2]
            if col.button(template_name, key=f"preset_{i}", use_container_width=True):
                if template_name != list(presets.keys())[-1]:  # 不是"自定义"
                    apply_preset_template(template_name)
                    st.rerun()
    
    # 自定义时间段设置
    st.markdown(f"#### {get_text('custom_periods')}")
    
    # 显示当前工作时间段的可视化
    if st.session_state.work_periods:
        st.markdown(generate_timeline_html(), unsafe_allow_html=True)
    
    # 时间段输入 - 使用st.time_input替换文本输入
    for i, period in enumerate(st.session_state.work_periods):
        with st.container():
            st.markdown(f"**{get_text('period')} {i+1}**")
            
            col1, col2, col3 = st.columns([3, 3, 1])
            
            with col1:
                # 使用st.time_input替换文本输入
                start_time = st.time_input(
                    get_text("start_time"),
                    value=period["start_time"],
                    disabled=st.session_state.is_running,
                    key=f"start_time_{i}",
                    step=timedelta(minutes=15)  # 15分钟间隔
                )
            
            with col2:
                # 使用st.time_input替换文本输入
                end_time = st.time_input(
                    get_text("end_time"),
                    value=period["end_time"],
                    disabled=st.session_state.is_running,
                    key=f"end_time_{i}",
                    step=timedelta(minutes=15)  # 15分钟间隔
                )
            
            with col3:
                if not st.session_state.is_running and len(st.session_state.work_periods) > 1:
                    if st.button("🗑️", key=f"remove_{i}", help=get_text("delete_period")):
                        remove_work_period(i)
                        st.rerun()
            
            # 验证时间范围
            if start_time >= end_time:
                st.error(get_text("time_range_error"))
            else:
                # 更新时间段
                st.session_state.work_periods[i]["start_time"] = start_time
                st.session_state.work_periods[i]["end_time"] = end_time
                
                # 显示时间段信息
                start_minutes = time_to_minutes(start_time)
                end_minutes = time_to_minutes(end_time)
                duration_minutes = end_minutes - start_minutes
                duration_hours = duration_minutes // 60
                duration_mins = duration_minutes % 60
                
                st.success(f"🕒 {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})")
        
        st.markdown("---")
    
    # 添加时间段按钮
    if not st.session_state.is_running:
        if st.button(get_text("add_period"), use_container_width=True):
            add_work_period()
            st.rerun()
    
    # 开始/重置按钮
    if not st.session_state.is_running:
        if st.button(get_text("start_tracking"), use_container_width=True, type="primary"):
            # 验证所有时间段
            valid = True
            for period in st.session_state.work_periods:
                if period["start_time"] >= period["end_time"]:
                    valid = False
                    break
            
            if valid:
                start_tracking()
                st.rerun()
            else:
                st.error(get_text("time_range_error"))
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
    
    if st.session_state.is_running:
        st.markdown(f"### {get_text('work_periods_today')}")
        
        # 创建更详细的时间轴可视化
        minutes_in_day = list(range(0, 24 * 60, 15))  # 每15分钟一个点
        is_work_minute = [False] * len(minutes_in_day)
        
        for period in st.session_state.work_periods:
            start_minutes = time_to_minutes(period["start_time"])
            end_minutes = time_to_minutes(period["end_time"])
            if start_minutes is not None and end_minutes is not None:
                for i, minute in enumerate(minutes_in_day):
                    if start_minutes <= minute < end_minutes:
                        is_work_minute[i] = True
        
        df = pd.DataFrame({
            "minute": minutes_in_day,
            "hour": [m / 60 for m in minutes_in_day],
            "is_work": is_work_minute,
            "status": [get_text("work_time") if w else get_text("non_work_time") for w in is_work_minute]
        })
        
        current_time_obj = get_current_time()
        current_minute = current_time_obj.hour * 60 + current_time_obj.minute
        current_hour_decimal = current_minute / 60
        
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
        
        current_time_indicator = alt.Chart(pd.DataFrame({'hour': [current_hour_decimal]})).mark_rule(
            color='red',
            strokeWidth=2
        ).encode(
            x='hour:Q'
        )
        
        st.altair_chart(chart + current_time_indicator, use_container_width=True)
        
        # 计算已赚取的金额
        earned_money = calculate_earned_money()
        progress = (earned_money / st.session_state.daily_salary) * 100 if st.session_state.daily_salary > 0 else 0
        
        # 收入进度显示
        st.markdown(f"### {get_text('income_progress')}")
        
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
            if st.session_state.seconds_per_dollar > 0:
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
        st.info(get_text("setup_prompt"))
        
        # 工作时间段预览
        st.markdown(f"### {get_text('work_periods_preview')}")
        for i, period in enumerate(st.session_state.work_periods):
            start_minutes = time_to_minutes(period["start_time"])
            end_minutes = time_to_minutes(period["end_time"])
            if start_minutes is not None and end_minutes is not None:
                duration_minutes = end_minutes - start_minutes
                duration_hours = duration_minutes // 60
                duration_mins = duration_minutes % 60
                
                st.markdown(f"""
                <div class="time-period">
                    <h4>{get_text('period')} {i+1}</h4>
                    <p>🕒 {period['start_time'].strftime('%H:%M')} - {period['end_time'].strftime('%H:%M')} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 计算总工作时间
        total_minutes = sum(
            time_to_minutes(period["end_time"]) - time_to_minutes(period["start_time"])
            for period in st.session_state.work_periods
            if time_to_minutes(period["start_time"]) is not None and time_to_minutes(period["end_time"]) is not None
        )
        total_hours = total_minutes // 60
        total_mins = total_minutes % 60
        st.markdown(f"**{get_text('total_work_time')}**: {total_hours}{get_text('hours')}{total_mins}{get_text('minutes')}")

with col2:
    if st.session_state.is_running:
        st.markdown(f"### {get_text('realtime_info')}")
        
        # 检查当前是否在工作时间
        now = get_current_time()
        current_minute = now.hour * 60 + now.minute
        is_currently_working = False
        
        for period in st.session_state.work_periods:
            start_minutes = time_to_minutes(period["start_time"])
            end_minutes = time_to_minutes(period["end_time"])
            if start_minutes is not None and end_minutes is not None:
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
            start_minutes = time_to_minutes(period["start_time"])
            end_minutes = time_to_minutes(period["end_time"])
            if start_minutes is not None and end_minutes is not None:
                duration_minutes = end_minutes - start_minutes
                duration_hours = duration_minutes // 60
                duration_mins = duration_minutes % 60
                
                st.markdown(f"""
                <div class="time-period">
                    <h4>{get_text('period')} {i+1}</h4>
                    <p>🕒 {period['start_time'].strftime('%H:%M')} - {period['end_time'].strftime('%H:%M')} ({duration_hours}{get_text('hours')}{duration_mins}{get_text('minutes')})</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 显示薪资信息
        st.markdown(f"### {get_text('salary_info')}")
        total_minutes = sum(
            time_to_minutes(period["end_time"]) - time_to_minutes(period["start_time"])
            for period in st.session_state.work_periods
            if time_to_minutes(period["start_time"]) is not None and time_to_minutes(period["end_time"]) is not None
        )
        
        st.markdown(f"**{get_text('daily_salary_info')}**: ${st.session_state.daily_salary:.2f}")
        if total_minutes > 0:
            st.markdown(f"**{get_text('hourly_salary')}**: ${st.session_state.daily_salary / (total_minutes / 60):.2f}/{get_text('hours')}")
            st.markdown(f"**{get_text('minute_salary')}**: ${st.session_state.daily_salary / total_minutes:.4f}/{get_text('minutes')}")
    else:
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