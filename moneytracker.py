import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import altair as alt
import plotly.graph_objects as go

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
    # 默认工作时间段：上午9-12，下午14-18
    st.session_state.work_periods = [
        {"start": 9, "end": 12},
        {"start": 14, "end": 18}
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

# 添加语言选择
if 'language' not in st.session_state:
    st.session_state.language = "zh"

# 语言文本字典
text = {
    "zh": {
        "title": "💰 Money Tracker",
        "subtitle": "实时追踪你的工作收入",
        "settings": "⚙️ 设置",
        "daily_salary": "日薪 ($)",
        "work_time_settings": "📅 工作时间设置",
        "work_time_desc": "使用滑动条设置每个工作时间段，可以添加多个时间段来表示不连续的工作时间（如午休）",
        "period": "时间段",
        "start_time": "开始时间",
        "end_time": "结束时间",
        "hours": "小时",
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
        "minutes": "分",
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
        "feature_2": "- 使用滑动条轻松调整工作时间",
        "feature_3": "- 实时计算已赚取金额",
        "feature_4": "- 可视化显示收入进度",
        "feature_5": "- 详细统计信息",
        "how_to_use": "**使用方法**:",
        "step_1": "1. 在左侧设置您的日薪",
        "step_2": "2. 使用滑动条设置工作时间段",
        "step_3": "3. 点击开始追踪按钮",
        "step_4": "4. 实时查看您的收入进度",
        "language": "🌐 语言"
    },
    "en": {
        "title": "💰 Money Tracker",
        "subtitle": "Track your work income in real-time",
        "settings": "⚙️ Settings",
        "daily_salary": "Daily Salary ($)",
        "work_time_settings": "📅 Work Time Settings",
        "work_time_desc": "Use sliders to set each work period. You can add multiple periods to represent non-continuous work times (e.g., lunch break)",
        "period": "Period",
        "start_time": "Start Time",
        "end_time": "End Time",
        "hours": "hours",
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
        "minutes": "min",
        "seconds": "sec",
        "setup_prompt": "👈 Please set your daily salary and work periods on the left, then click 'Start Tracking' to begin recording your income.",
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
        "feature_2": "- Easy adjustment of work times using sliders",
        "feature_3": "- Real-time calculation of earned amount",
        "feature_4": "- Visual display of income progress",
        "feature_5": "- Detailed statistics",
        "how_to_use": "**How to Use**:",
        "step_1": "1. Set your daily salary on the left",
        "step_2": "2. Use sliders to set work periods",
        "step_3": "3. Click the 'Start Tracking' button",
        "step_4": "4. View your income progress in real-time",
        "language": "🌐 Language"
    }
}

# 获取当前语言的文本
def get_text(key):
    return text[st.session_state.language][key]

# 计算工作总秒数
def calculate_work_seconds(periods):
    total_seconds = 0
    for period in periods:
        total_seconds += (period["end"] - period["start"]) * 3600  # 小时转秒
    return total_seconds

# 计算已赚取的金额
def calculate_earned_money():
    if not st.session_state.is_running:
        return 0.0
    
    now = datetime.now()
    elapsed_work_seconds = 0
    
    # 计算今天已经过去的工作时间
    for period in st.session_state.work_periods:
        start_hour, end_hour = period["start"], period["end"]
        
        # 转换为今天的日期时间
        period_start = now.replace(hour=start_hour, minute=0, second=0, microsecond=0)
        period_end = now.replace(hour=end_hour, minute=0, second=0, microsecond=0)
        
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
    st.session_state.start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
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
    st.session_state.work_periods.append({"start": 9, "end": 18})

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
            cols = st.columns(2)
            
            # 使用滑动条设置开始和结束时间
            start_hour = cols[0].slider(
                f"{get_text('start_time')} {i+1}",
                min_value=0,
                max_value=23,
                value=period["start"],
                step=1,
                disabled=st.session_state.is_running,
                key=f"start_{i}"
            )
            
            end_hour = cols[1].slider(
                f"{get_text('end_time')} {i+1}",
                min_value=start_hour + 1,
                max_value=24,
                value=max(start_hour + 1, period["end"]),
                step=1,
                disabled=st.session_state.is_running,
                key=f"end_{i}"
            )
            
            # 更新时间段
            st.session_state.work_periods[i]["start"] = start_hour
            st.session_state.work_periods[i]["end"] = end_hour
            
            # 显示时间段
            st.markdown(f"🕒 {start_hour}:00 - {end_hour}:00 ({end_hour - start_hour} {get_text('hours')})")
            
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
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"### {get_text('current_time')}: {current_time}")
    
    # 工作时间段可视化
    if st.session_state.is_running:
        st.markdown(f"### {get_text('work_periods_today')}")
        
        # 创建24小时时间轴
        hours = list(range(24))
        is_work_hour = [False] * 24
        
        # 标记工作时间
        for period in st.session_state.work_periods:
            for h in range(period["start"], period["end"]):
                is_work_hour[h] = True
        
        # 创建数据框
        df = pd.DataFrame({
            "hour": hours,
            "is_work": is_work_hour,
            "status": [get_text("work_time") if w else get_text("non_work_time") for w in is_work_hour]
        })
        
        # 当前小时
        current_hour = datetime.now().hour
        
        # 创建图表
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X('hour:O', title=get_text('hours'), axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count():Q', title=None, axis=None),
            color=alt.Color('status:N', 
                          scale=alt.Scale(domain=[get_text('work_time'), get_text('non_work_time')],
                                         range=['#4361ee', '#e9ecef']),
                          legend=alt.Legend(title=get_text("status"))),
            tooltip=['hour:O', 'status:N']
        ).properties(
            width=600,
            height=100
        )
        
        # 添加当前时间指示器
        current_time_indicator = alt.Chart(pd.DataFrame({'hour': [current_hour]})).mark_rule(
            color='red',
            strokeWidth=2
        ).encode(
            x='hour:O'
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
            st.markdown(f"""
            <div class="time-period">
                <h4>{get_text('period')} {i+1}</h4>
                <p>🕒 {period["start"]}:00 - {period["end"]}:00 ({period["end"] - period["start"]} {get_text('hours')})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 计算总工作时间
        total_hours = sum(period["end"] - period["start"] for period in st.session_state.work_periods)
        st.markdown(f"**{get_text('total_work_time')}**: {total_hours} {get_text('hours')}")

with col2:
    # 右侧信息面板
    if st.session_state.is_running:
        # 实时更新部分
        st.markdown(f"### {get_text('realtime_info')}")
        
        # 检查当前是否在工作时间
        now = datetime.now()
        current_hour = now.hour
        is_currently_working = False
        
        for period in st.session_state.work_periods:
            if period["start"] <= current_hour < period["end"]:
                is_currently_working = True
                break
        
        if is_currently_working:
            st.success(get_text("is_work_time"))
        else:
            st.warning(get_text("not_work_time"))
        
        # 显示工作时间详情
        st.markdown(f"### {get_text('work_time_details')}")
        for i, period in enumerate(st.session_state.work_periods):
            st.markdown(f"""
            <div class="time-period">
                <h4>{get_text('period')} {i+1}</h4>
                <p>🕒 {period["start"]}:00 - {period["end"]}:00 ({period["end"] - period["start"]} {get_text('hours')})</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 计算总工作时间
        total_hours = sum(period["end"] - period["start"] for period in st.session_state.work_periods)
        st.markdown(f"**{get_text('total_work_time')}**: {total_hours} {get_text('hours')}")
        
        # 显示日薪信息
        st.markdown(f"### {get_text('salary_info')}")
        st.markdown(f"**{get_text('daily_salary_info')}**: ${st.session_state.daily_salary:.2f}")
        st.markdown(f"**{get_text('hourly_salary')}**: ${st.session_state.daily_salary / total_hours:.2f}/{get_text('hours')}")
        st.markdown(f"**{get_text('minute_salary')}**: ${st.session_state.daily_salary / (total_hours * 60):.4f}/{get_text('minutes')}")
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
        
        {get_text('how_to_use')}
        {get_text('step_1')}
        {get_text('step_2')}
        {get_text('step_3')}
        {get_text('step_4')}
        """)

# 自动刷新页面（每秒）
if st.session_state.is_running:
    st.markdown("""
    <script>
        setTimeout(function(){
            window.location.reload();
        }, 1000);
    </script>
    """, unsafe_allow_html=True)