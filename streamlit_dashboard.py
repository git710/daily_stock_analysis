"""
===================================
A股智能分析 - 高级仪表盘
===================================

增强版 Streamlit 界面，支持：
- 实时数据获取
- 交互式图表
- AI 分析可视化
- 大盘监控
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, date, timedelta
import sys
from pathlib import Path
import time

# 项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from storage import get_db
from config import get_config
from analyzer import STOCK_NAME_MAP
from data_provider.akshare_fetcher import AkshareFetcher

# 页面配置
st.set_page_config(
    page_title="A股智能分析仪表盘 Pro",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 样式
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #667eea; font-weight: bold; }
    .metric-card { padding: 15px; border-radius: 10px; margin: 10px 0; }
    .positive { color: #00ff88; }
    .negative { color: #ff4757; }
    .neutral { color: #ffa502; }
    .status-badge { padding: 5px 15px; border-radius: 20px; font-weight: bold; }
    .status-buy { background: #00ff88; color: #000; }
    .status-sell { background: #ff4757; color: #fff; }
    .status-hold { background: #ffa502; color: #000; }
    .info-box { background: #2d3748; padding: 15px; border-radius: 8px; margin: 10px 0; }
    .section-title { font-size: 1.5rem; color: #764ba2; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)


class StockDashboard:
    """股票仪表盘管理器"""

    def __init__(self):
        self.db = get_db()
        self.fetcher = AkshareFetcher()
        self.config = get_config()

    def get_stock_data(self, code: str, days: int = 60):
        """获取股票数据（缓存）"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            data = self.db.get_data_range(code, start_date, end_date)

            if data:
                df = pd.DataFrame([item.to_dict() for item in data])
                df['date'] = pd.to_datetime(df['date'])
                return df.sort_values('date')
        except Exception as e:
            st.error(f"数据获取失败: {e}")
        return None

    def get_realtime_quote(self, code: str):
        """实时行情（缓存）"""
        try:
            return self.fetcher.get_realtime_quote(code)
        except:
            return None

    def get_chip_distribution(self, code: str):
        """筹码分布（缓存）"""
        try:
            return self.fetcher.get_chip_distribution(code)
        except:
            return None

    def show_header(self, code: str, name: str):
        """显示头部信息"""
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="margin: 0; color: white;">{name} <small>({code})</small></h1>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.9);">A股智能分析系统 - 实时仪表盘</p>
        </div>
        """, unsafe_allow_html=True)

    def show_realtime_metrics(self, code: str):
        """实时指标卡片"""
        quote = self.get_realtime_quote(code)

        if not quote:
            st.warning("无法获取实时行情")
            return

        # 指标卡片
        cols = st.columns(5)

        with cols[0]:
            delta_color = "normal" if quote.pct_chg >= 0 else "inverse"
            st.metric(
                "当前价格",
                f"{quote.price:.2f}",
                f"{quote.pct_chg:.2f}%",
                delta_color=delta_color
            )

        with cols[1]:
            st.metric("量比", f"{quote.volume_ratio:.2f}")

        with cols[2]:
            st.metric("换手率", f"{quote.turnover_rate:.2f}%")

        with cols[3]:
            st.metric("PE", f"{quote.pe_ratio:.1f}" if quote.pe_ratio else "N/A")

        with cols[4]:
            st.metric("PB", f"{quote.pb_ratio:.1f}" if quote.pb_ratio else "N/A")

        # 60日涨幅
        if quote.change_60d:
            st.info(f"📊 60日涨幅: **{quote.change_60d:.2f}%**")

        return quote

    def show_kline_chart(self, df: pd.DataFrame, name: str):
        """K线图 + 均线 + 成交量"""
        if df is None or df.empty:
            return

        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=['K线 & 均线', 'MACD (模拟)', '成交量']
        )

        # K线
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='K线',
                increasing_line_color='#00ff88',
                decreasing_line_color='#ff4757'
            ), row=1, col=1
        )

        # MA均线
        for ma, color in [('ma5', '#ffa502'), ('ma10', '#3742fa'), ('ma20', '#ff6b81')]:
            if ma in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['date'], y=df[ma],
                        mode='lines', name=ma.upper(),
                        line=dict(color=color, width=2)
                    ), row=1, col=1
                )

        # MACD (模拟计算)
        if len(df) >= 26:
            exp12 = df['close'].ewm(span=12).mean()
            exp26 = df['close'].ewm(span=26).mean()
            macd = exp12 - exp26
            signal = macd.ewm(span=9).mean()

            fig.add_trace(
                go.Scatter(x=df['date'], y=macd, mode='lines', name='MACD', line=dict(color='#888')), row=2, col=1
            )
            fig.add_trace(
                go.Scatter(x=df['date'], y=signal, mode='lines', name='Signal', line=dict(color='#ddd')), row=2, col=1
            )

        # 成交量
        if 'volume' in df.columns:
            colors = ['#00ff88' if c >= o else '#ff4757' for c, o in zip(df['close'], df['open'])]
            fig.add_trace(
                go.Bar(x=df['date'], y=df['volume'], name='成交量', marker_color=colors), row=3, col=1
            )

        fig.update_layout(
            height=700,
            xaxis_rangeslider_visible=False,
            template='plotly_dark',
            paper_bgcolor='#1e1e1e',
            plot_bgcolor='#1e1e1e',
            font=dict(color='#e0e0e0'),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig, use_container_width=True)

    def show_chip_analysis(self, code: str, quote):
        """筹码分布分析"""
        chip = self.get_chip_distribution(code)

        if not chip:
            st.info("该股票暂无筹码分布数据")
            return

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("获利比例", f"{chip.profit_ratio:.1%}", delta="高" if chip.profit_ratio > 0.8 else "低")

        with col2:
            st.metric("平均成本", f"{chip.avg_cost:.2f}元")

        with col3:
            st.metric("90%集中度", f"{chip.concentration_90:.2f}%", delta="好" if chip.concentration_90 < 30 else "分散")

        # 筹码状态判断
        if quote:
            status = chip.get_chip_status(quote.price)
            status_emoji = {"": "❓", "": "⚠️", "": "✅"}[status] if status else "❓"

            st.markdown(f"""
            <div class="info-box">
                <strong>筹码状态分析 {status_emoji}</strong><br>
                当前价格: {quote.price:.2f} 元<br>
                平均成本: {chip.avg_cost:.2f} 元<br>
                获利盘: {chip.profit_ratio:.1%}<br>
                <em>提示: 获利比例过高可能面临回调压力</em>
            </div>
            """, unsafe_allow_html=True)

    def show_trend_analysis(self, df: pd.DataFrame):
        """趋势分析"""
        if df is None or len(df) < 20:
            return

        latest = df.iloc[-1]

        # 均线状态
        ma5, ma10, ma20 = latest.get('ma5', 0), latest.get('ma10', 0), latest.get('ma20', 0)
        close = latest.get('close', 0)

        st.markdown("#### 📈 趋势分析")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write("**均线排列**")
            if ma5 > ma10 > ma20 > 0:
                st.success("✅ 多头排列")
            elif ma5 < ma10 < ma20:
                st.error("❌ 空头排列")
            else:
                st.warning("⚠️ 震荡整理")

        with col2:
            st.write("**乖离率**")
            if ma5 > 0:
                bias5 = (close - ma5) / ma5 * 100
                bias10 = (close - ma10) / ma10 * 100

                bias5_color = "positive" if abs(bias5) < 3 else ("negative" if abs(bias5) > 5 else "neutral")
                bias10_color = "positive" if abs(bias10) < 5 else ("negative" if abs(bias10) > 8 else "neutral")

                st.markdown(f"MA5: <span class='{bias5_color}'>{bias5:.2f}%</span>", unsafe_allow_html=True)
                st.markdown(f"MA10: <span class='{bias10_color}'>{bias10:.2f}%</span>", unsafe_allow_html=True)

                if abs(bias5) > 5:
                    st.error("⚠️ 追高风险")
                elif abs(bias5) < 2:
                    st.success("✅ 买点机会")

        with col3:
            st.write("**量能分析**")
            if 'volume_ratio' in latest and pd.notna(latest['volume_ratio']):
                vr = latest['volume_ratio']
                if vr < 0.8:
                    st.write("📉 缩量")
                elif vr < 1.2:
                    st.write("➡️ 平量")
                else:
                    st.write("📈 放量")

    def show_ai_dashboard(self, code: str):
        """AI分析仪表盘"""
        st.markdown("---")
        st.markdown("### 🤖 AI 智能分析")

        # 从日志读取最近分析
        log_dir = Path(__file__).parent / "logs"
        today_str = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"stock_analysis_{today_str}.log"

        if not log_file.exists():
            st.info("暂无今日分析结果，请运行: `python main.py`")
            return

        # 简单解析
        content = log_file.read_text(encoding='utf-8')
        lines = content.split('\n')

        # 查找该股票的分析结果
        result_lines = []
        for line in lines:
            if f"[{code}]" in line:
                result_lines.append(line)

        if not result_lines:
            st.info("该股票今日暂无分析结果")
            return

        # 显示关键信息
        st.markdown("#### 最近分析摘要")

        for line in result_lines[-5:]:
            if "分析完成" in line:
                parts = line.split(':')
                if len(parts) >= 2:
                    advice = parts[1].strip()
                    score = line.split('评分')[-1].strip() if '评分' in line else "N/A"

                    badge_class = "status-buy" if "买入" in advice or "看多" in advice else "status-sell" if "卖出" in advice or "看空" in advice else "status-hold"

                    st.markdown(f"""
                    <div style="padding: 15px; background: #2d3748; border-radius: 8px; margin: 10px 0;">
                        <strong>操作建议:</strong> <span class="status-badge {badge_class}">{advice}</span><br>
                        <strong>AI评分:</strong> {score}
                    </div>
                    """, unsafe_allow_html=True)

            elif "实时行情" in line:
                st.code(line)

        # 显示完整日志
        with st.expander("查看完整分析日志"):
            st.code('\n'.join(result_lines[-10:]))

    def show_market_overview(self):
        """大盘概览"""
        st.markdown("---")
        st.markdown("### 🏢 大盘监控")

        log_dir = Path(__file__).parent / "logs"
        today_str = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"stock_analysis_{today_str}.log"

        if not log_file.exists():
            return

        content = log_file.read_text(encoding='utf-8')

        # 提取大盘数据
        if "涨:" in content and "跌:" in content:
            # 简单提取
            lines = content.split('\n')
            for line in lines:
                if "涨:" in line and "跌:" in line:
                    try:
                        parts = line.split()
                        data = {}
                        for part in parts:
                            if ":" in part:
                                key, value = part.split(":")
                                data[key] = value

                        if data:
                            col1, col2, col3, col4, col5 = st.columns(5)
                            with col1:
                                st.metric("上涨", data.get('涨', 'N/A'))
                            with col2:
                                st.metric("下跌", data.get('跌', 'N/A'))
                            with col3:
                                st.metric("涨停", data.get('涨停', 'N/A'))
                            with col4:
                                st.metric("跌停", data.get('跌停', 'N/A'))
                            with col5:
                                st.metric("成交额", data.get('成交额', 'N/A'))
                        break
                    except:
                        pass

        # 显示复盘内容
        with st.expander("查看大盘复盘详情"):
            lines = content.split('\n')
            review_start = False
            review_lines = []

            for line in lines:
                if "开始大盘复盘分析" in line:
                    review_start = True
                elif review_start:
                    if "大盘复盘分析完成" in line:
                        review_lines.append(line)
                        break
                    review_lines.append(line)

            if review_lines:
                st.code('\n'.join(review_lines[-20:]))

    def show_data_management(self):
        """数据管理"""
        st.markdown("---")
        st.markdown("### 📊 数据管理")

        col1, col2 = st.columns(2)

        with col1:
            # 数据库状态
            db_path = Path(__file__).parent / "data" / "stock_analysis.db"
            if db_path.exists():
                size_mb = db_path.stat().st_size / 1024 / 1024
                st.success(f"数据库大小: {size_mb:.2f} MB")

                # 显示最近记录
                try:
                    with self.db.get_session() as session:
                        from storage import StockDaily
                        result = session.execute(
                            "SELECT COUNT(*) as cnt, MAX(date) as last_date FROM stock_daily"
                        ).first()
                        if result:
                            st.write(f"记录总数: {result.cnt}")
                            st.write(f"最新日期: {result.last_date}")
                except:
                    pass

        with col2:
            # 日志文件
            log_dir = Path(__file__).parent / "logs"
            if log_dir.exists():
                log_files = list(log_dir.glob("stock_analysis_*.log"))
                if log_files:
                    latest_log = max(log_files, key=lambda x: x.stat().st_mtime)
                    st.success(f"日志文件: {latest_log.name}")

                    # 下载按钮
                    with open(latest_log, 'r', encoding='utf-8') as f:
                        content = f.read()
                        st.download_button(
                            "下载今日日志",
                            content,
                            latest_log.name,
                            "text/plain"
                        )

    def run(self):
        """运行仪表盘"""
        st.markdown('<p class="main-header">💹 A股智能分析仪表盘 Pro</p>', unsafe_allow_html=True)

        # 侧边栏
        with st.sidebar:
            st.markdown("### 🎛️ 控制面板")

            # 股票选择
            config = get_config()
            default_stocks = config.stock_list if config.stock_list else ["601899", "518880", "159509"]

            selected_code = st.selectbox(
                "选择股票",
                default_stocks,
                format_func=lambda x: f"{x} - {STOCK_NAME_MAP.get(x, '股票')}"
            )

            # 视图选择
            view_mode = st.radio(
                "视图模式",
                ["完整视图", "仅图表", "仅分析", "大盘监控"]
            )

            # 操作按钮
            if st.button("🔄 刷新数据", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

            if st.button("📊 运行分析", use_container_width=True):
                st.info("请在终端运行: `python main.py --stocks " + selected_code + "`")

            # 数据导出
            if st.button("💾 导出报告", use_container_width=True):
                log_dir = Path(__file__).parent / "logs"
                today_str = datetime.now().strftime("%Y%m%d")
                log_file = log_dir / f"stock_analysis_{today_str}.log"

                if log_file.exists():
                    st.download_button(
                        "下载日志",
                        log_file.read_text(encoding='utf-8'),
                        f"analysis_{today_str}.log",
                        use_container_width=True
                    )

            st.markdown("---")
            self.show_data_management()

        # 主内容
        name = STOCK_NAME_MAP.get(selected_code, selected_code)

        # 头部
        self.show_header(selected_code, name)

        # 根据视图模式显示内容
        if view_mode in ["完整视图", "仅图表"]:
            # 实时指标
            quote = self.show_realtime_metrics(selected_code)

            # 数据加载
            df = self.get_stock_data(selected_code, 60)

            if df is not None:
                # K线图
                st.markdown("#### 📈 K线分析")
                self.show_kline_chart(df, name)

                # 趋势分析
                if view_mode == "完整视图":
                    self.show_trend_analysis(df)

                    # 筹码分析
                    st.markdown("#### 🎯 筹码分析")
                    self.show_chip_analysis(selected_code, quote)
            else:
                st.warning("暂无历史数据，请先运行分析程序")

        if view_mode in ["完整视图", "仅分析"]:
            # AI分析
            self.show_ai_dashboard(selected_code)

        if view_mode in ["完整视图", "大盘监控"]:
            # 大盘监控
            self.show_market_overview()


def main():
    """主函数"""
    dashboard = StockDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()