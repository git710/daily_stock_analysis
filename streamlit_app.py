"""
===================================
A股自选股智能分析系统 - Web 界面
===================================

基于 Streamlit 的可视化展示平台
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date, timedelta
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from storage import get_db, DatabaseManager
from config import get_config
from analyzer import STOCK_NAME_MAP

# 页面配置
st.set_page_config(
    page_title="A股智能分析仪表盘",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
    }
    .positive { color: #00ff88; }
    .negative { color: #ff4757; }
    .neutral { color: #ffa502; }
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        margin: 5px;
    }
    .status-buy { background: #00ff88; color: #000; }
    .status-hold { background: #ffa502; color: #000; }
    .status-sell { background: #ff4757; color: #fff; }
    h1 { color: #667eea; }
    h2 { color: #764ba2; }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)  # 缓存5分钟
def load_stock_data(code: str, days: int = 30):
    """加载股票历史数据（带缓存）"""
    try:
        db = get_db()
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        data = db.get_data_range(code, start_date, end_date)

        if not data:
            return None

        # 转换为 DataFrame
        df_data = []
        for item in data:
            df_data.append(item.to_dict())

        df = pd.DataFrame(df_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')

        return df
    except Exception as e:
        st.error(f"加载数据失败: {e}")
        return None


@st.cache_data(ttl=60)  # 缓存1分钟
def get_latest_analysis(code: str):
    """获取最新分析结果（从日志解析）"""
    log_dir = Path(__file__).parent / "logs"
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"stock_analysis_{today_str}.log"

    if not log_file.exists():
        return None

    # 简单的日志解析（实际可以优化为更健壮的解析）
    try:
        content = log_file.read_text(encoding='utf-8')

        # 查找该股票的分析结果
        lines = content.split('\n')
        result = {}

        for i, line in enumerate(lines):
            if f"[{code}]" in line:
                # 提取关键信息
                if "分析完成" in line:
                    # 格式: [601899] 分析完成: 观望, 评分 68
                    parts = line.split(':')
                    if len(parts) >= 2:
                        result['advice'] = parts[1].split(',')[0].strip()
                        if '评分' in line:
                            result['score'] = line.split('评分')[-1].strip()

                # 提取实时行情
                if "实时行情" in line:
                    # [601899] 紫金矿业 实时行情: 价格=38.5, 量比=1.43, 换手率=2.07%
                    result['realtime'] = line.split(':')[-1].strip()

        return result if result else None
    except Exception:
        return None


def create_kline_chart(df: pd.DataFrame, stock_name: str):
    """创建K线图"""
    if df.empty:
        return None

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.7, 0.3],
        subplot_titles=(f'{stock_name} K线图', '成交量')
    )

    # K线
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='K线'
        ), row=1, col=1
    )

    # MA均线
    if 'ma5' in df.columns and df['ma5'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['ma5'],
                mode='lines', name='MA5',
                line=dict(color='#ffa502', width=2)
            ), row=1, col=1
        )

    if 'ma10' in df.columns and df['ma10'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['ma10'],
                mode='lines', name='MA10',
                line=dict(color='#3742fa', width=2)
            ), row=1, col=1
        )

    if 'ma20' in df.columns and df['ma20'].notna().any():
        fig.add_trace(
            go.Scatter(
                x=df['date'], y=df['ma20'],
                mode='lines', name='MA20',
                line=dict(color='#ff6b81', width=2)
            ), row=1, col=1
        )

    # 成交量
    if 'volume' in df.columns:
        fig.add_trace(
            go.Bar(
                x=df['date'], y=df['volume'],
                name='成交量',
                marker_color='#667eea'
            ), row=2, col=1
        )

    fig.update_layout(
        height=600,
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#1e1e1e',
        font=dict(color='#e0e0e0')
    )

    return fig


def show_dashboard(df: pd.DataFrame, realtime_info: dict = None):
    """显示仪表盘概览"""
    if df is None or df.empty:
        st.warning("暂无数据")
        return

    latest = df.iloc[-1]

    # 创建指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        price = latest['close']
        st.metric(
            label="当前价格",
            value=f"{price:.2f} 元",
            delta=f"{latest.get('pct_chg', 0):.2f}%" if 'pct_chg' in latest else None
        )

    with col2:
        volume_ratio = realtime_info.get('volume_ratio', 'N/A') if realtime_info else 'N/A'
        st.metric(label="量比", value=volume_ratio)

    with col3:
        turnover = realtime_info.get('turnover_rate', 'N/A') if realtime_info else 'N/A'
        st.metric(label="换手率", value=f"{turnover}%" if turnover != 'N/A' else "N/A")

    with col4:
        ma_status = "多头" if (latest.get('ma5', 0) > latest.get('ma10', 0) > latest.get('ma20', 0)) else "震荡"
        st.metric(label="均线状态", value=ma_status)

    # 筹码分布（如果有）
    if realtime_info and 'chip_status' in realtime_info:
        st.info(f"🎯 筹码状态: {realtime_info['chip_status']}")


def show_ai_analysis(analysis_result: dict):
    """显示AI分析结果"""
    if not analysis_result:
        st.info("暂无AI分析结果，请先运行分析程序")
        return

    st.markdown("### 🤖 AI 分析结果")

    # 操作建议
    advice = analysis_result.get('advice', 'N/A')
    score = analysis_result.get('score', 'N/A')

    # 根据建议显示不同样式
    if '买入' in advice or '看多' in advice:
        badge_class = "status-buy"
    elif '卖出' in advice or '看空' in advice:
        badge_class = "status-sell"
    else:
        badge_class = "status-hold"

    st.markdown(f"""
    <div style="padding: 20px; background: #2d3748; border-radius: 10px; margin: 10px 0;">
        <h3 style="margin: 0;">操作建议: <span class="status-badge {badge_class}">{advice}</span></h3>
        <p style="margin: 10px 0; font-size: 18px;">AI 评分: <strong>{score}</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # 实时行情信息
    if analysis_result.get('realtime'):
        st.markdown("#### 📊 实时行情")
        st.code(analysis_result['realtime'])


def show_news_intelligence(stock_code: str):
    """显示情报搜索结果"""
    log_dir = Path(__file__).parent / "logs"
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"stock_analysis_{today_str}.log"

    if not log_file.exists():
        return

    content = log_file.read_text(encoding='utf-8')

    # 查找情报搜索部分
    lines = content.split('\n')
    intel_lines = []
    in_intel = False

    for line in lines:
        if f"[{stock_code}]" in line and "情报搜索" in line:
            in_intel = True
        elif in_intel and f"[{stock_code}]" in line and ("分析完成" in line or "开始处理" in line):
            break
        elif in_intel:
            intel_lines.append(line)

    if intel_lines:
        st.markdown("### 📰 情报中心")
        with st.expander("查看搜索日志", expanded=False):
            st.code('\n'.join(intel_lines[-10:]))


def show_market_review():
    """显示大盘复盘"""
    log_dir = Path(__file__).parent / "logs"
    today_str = datetime.now().strftime("%Y%m%d")
    log_file = log_dir / f"stock_analysis_{today_str}.log"

    if not log_file.exists():
        return

    content = log_file.read_text(encoding='utf-8')

    # 查找大盘复盘部分
    lines = content.split('\n')
    review_lines = []
    in_review = False

    for line in lines:
        if "开始大盘复盘分析" in line:
            in_review = True
        elif in_review and "大盘复盘分析完成" in line:
            review_lines.append(line)
            break
        elif in_review:
            review_lines.append(line)

    if review_lines:
        st.markdown("### 🏢 大盘复盘")

        # 提取关键数据
        market_data = {}
        for line in review_lines:
            if "涨:" in line and "跌:" in line:
                parts = line.split()
                for part in parts:
                    if "涨:" in part:
                        market_data['up'] = part.split(':')[1]
                    elif "跌:" in part:
                        market_data['down'] = part.split(':')[1]
                    elif "涨停:" in part:
                        market_data['limit_up'] = part.split(':')[1]
                    elif "跌停:" in part:
                        market_data['limit_down'] = part.split(':')[1]
                    elif "成交额:" in part:
                        market_data['amount'] = part.split(':')[1]

        if market_data:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("上涨", market_data.get('up', 'N/A'))
            with col2:
                st.metric("下跌", market_data.get('down', 'N/A'))
            with col3:
                st.metric("涨停", market_data.get('limit_up', 'N/A'))
            with col4:
                st.metric("跌停", market_data.get('limit_down', 'N/A'))

        with st.expander("详细复盘内容"):
            st.code('\n'.join(review_lines[-20:]))


def show_history(df: pd.DataFrame, stock_code: str):
    """显示历史数据表格"""
    if df is None or df.empty:
        return

    st.markdown("### 📋 历史数据")

    # 格式化显示
    display_df = df.copy()
    display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')

    # 数值格式化
    for col in ['open', 'high', 'low', 'close']:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)

    for col in ['volume', 'amount']:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")

    for col in ['ma5', 'ma10', 'ma20']:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)

    st.dataframe(display_df, use_container_width=True, height=400)


def main():
    """主界面"""
    st.title("📈 A股自选股智能分析系统")

    # 侧边栏
    with st.sidebar:
        st.markdown("### 🛠️ 控制面板")

        # 股票选择
        config = get_config()
        default_stocks = config.stock_list if config.stock_list else ["601899", "518880", "159509"]

        selected_code = st.selectbox(
            "选择股票",
            default_stocks,
            format_func=lambda x: f"{x} - {STOCK_NAME_MAP.get(x, '股票')}"
        )

        # 日期范围
        days = st.slider("查看天数", 5, 120, 30)

        # 操作按钮
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        if st.button("📊 查看大盘复盘", use_container_width=True):
            st.session_state.show_market = True

        # 数据导出
        if st.button("💾 导出报告", use_container_width=True):
            log_dir = Path(__file__).parent / "logs"
            today_str = datetime.now().strftime("%Y%m%d")
            log_file = log_dir / f"stock_analysis_{today_str}.log"

            if log_file.exists():
                st.download_button(
                    "下载日志文件",
                    log_file.read_text(encoding='utf-8'),
                    f"stock_analysis_{today_str}.log",
                    "text/plain",
                    use_container_width=True
                )

        st.markdown("---")
        st.markdown("### 📊 系统状态")

        # 检查数据库
        try:
            db = get_db()
            db_path = Path(__file__).parent / "data" / "stock_analysis.db"
            if db_path.exists():
                size_mb = db_path.stat().st_size / 1024 / 1024
                st.success(f"数据库正常 ({size_mb:.2f} MB)")
            else:
                st.warning("数据库未创建")
        except:
            st.error("数据库连接失败")

        # 检查日志
        log_dir = Path(__file__).parent / "logs"
        today_str = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"stock_analysis_{today_str}.log"

        if log_file.exists():
            st.success("今日日志存在")
        else:
            st.info("暂无今日日志")

    # 主界面
    tab1, tab2, tab3, tab4 = st.tabs(["📊 仪表盘", "📈 K线图表", "🤖 AI分析", "📰 情报中心"])

    with tab1:
        st.markdown(f"### {selected_code} - {STOCK_NAME_MAP.get(selected_code, '股票')} 实时概览")

        # 加载数据
        df = load_stock_data(selected_code, days)

        # 获取实时信息（从日志）
        analysis_result = get_latest_analysis(selected_code)

        # 显示仪表盘
        if df is not None:
            show_dashboard(df, analysis_result)

            # 关键指标行
            col1, col2, col3 = st.columns(3)
            latest = df.iloc[-1]

            with col1:
                st.markdown("**📊 今日数据**")
                st.write(f"开盘: {latest.get('open', 'N/A')}")
                st.write(f"收盘: {latest.get('close', 'N/A')}")
                st.write(f"最高: {latest.get('high', 'N/A')}")
                st.write(f"最低: {latest.get('low', 'N/A')}")

            with col2:
                st.markdown("**📈 均线系统**")
                st.write(f"MA5: {latest.get('ma5', 'N/A')}")
                st.write(f"MA10: {latest.get('ma10', 'N/A')}")
                st.write(f"MA20: {latest.get('ma20', 'N/A')}")

                # 判断均线形态
                ma5, ma10, ma20 = latest.get('ma5', 0), latest.get('ma10', 0), latest.get('ma20', 0)
                if ma5 > ma10 > ma20:
                    st.success("✅ 多头排列")
                elif ma5 < ma10 < ma20:
                    st.error("❌ 空头排列")
                else:
                    st.warning("⚠️ 震荡整理")

            with col3:
                st.markdown("**💰 乖离率分析**")
                if 'close' in latest and 'ma5' in latest:
                    bias5 = (latest['close'] - latest['ma5']) / latest['ma5'] * 100 if latest['ma5'] else 0
                    bias10 = (latest['close'] - latest['ma10']) / latest['ma10'] * 100 if latest['ma10'] else 0

                    st.write(f"MA5乖离: {bias5:.2f}%")
                    st.write(f"MA10乖离: {bias10:.2f}%")

                    if abs(bias5) > 5:
                        st.error("⚠️ 乖离率过高，注意追高风险")
                    elif abs(bias5) < 2:
                        st.success("✅ 乖离率适中，可关注")
        else:
            st.warning("暂无数据，请先运行分析程序")

    with tab2:
        st.markdown(f"### {selected_code} K线图表")

        if df is not None and not df.empty:
            fig = create_kline_chart(df, STOCK_NAME_MAP.get(selected_code, selected_code))
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无图表数据")

    with tab3:
        st.markdown(f"### 🤖 AI 智能分析")

        if analysis_result:
            show_ai_analysis(analysis_result)
        else:
            st.info("暂无AI分析结果")

            st.markdown("""
            **💡 使用说明：**

            1. 首先运行主程序生成分析：
               ```bash
               python main.py
               ```

            2. 然后刷新此页面查看结果

            3. 分析内容包括：
               - 技术面分析（均线、乖离率、量能）
               - 筹码分布分析
               - 多维度情报搜索
               - AI 综合评估
            """)

    with tab4:
        st.markdown(f"### 📰 情报中心")

        if selected_code:
            show_news_intelligence(selected_code)

        st.markdown("---")

        # 大盘复盘（可选显示）
        if st.session_state.get('show_market', False):
            show_market_review()

        if st.button("隐藏大盘复盘" if st.session_state.get('show_market', False) else "显示大盘复盘"):
            st.session_state.show_market = not st.session_state.get('show_market', False)
            st.rerun()

    # 历史数据标签页（额外）
    with st.expander("📋 查看详细历史数据"):
        if df is not None:
            show_history(df, selected_code)


if __name__ == "__main__":
    # 初始化会话状态
    if 'show_market' not in st.session_state:
        st.session_state.show_market = False

    main()