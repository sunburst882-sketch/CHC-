# 1. 导入依赖库（不变）
import streamlit as st
import folium
from folium.plugins import MarkerCluster  # 聚合标记，避免重叠
import pandas as pd

# 2. 加载并处理新数据（核心适配：仅3列数据）
# 读取新CSV文件（需与文件实际名称一致）
df = pd.read_csv("ruilin_location_data.csv")

# 给每个地点配置经纬度（必须包含所有“地点”列的名称，否则标记不显示）
location_coords = {
    "北京": [39.9042, 116.4074],
    "苏州": [31.2993, 120.6195],
    "济南": [36.6512, 117.1200],
    "南京": [32.0603, 118.7969],
    "湖州": [30.8672, 120.0934],
    "杭州": [30.2741, 120.1551],
    "扬州": [32.3932, 119.4989]
    # 若新增地点，需在这里补充坐标，格式："地点名": [纬度, 经度]
}

# 将经纬度匹配到数据中（新数据无变化，仅匹配“地点”列）
df["纬度"] = df["地点"].map(lambda x: location_coords[x][0])
df["经度"] = df["地点"].map(lambda x: location_coords[x][1])

# 3. 搭建Streamlit网页界面（适配新数据：突出“提及次数”和“活动类型”）
# 设置网页标题（体现新数据核心）
st.title("《儒林外史》地点提及与活动可视化")
st.subheader("核心数据：地点被提及次数 + 涉及活动类型")
st.divider()  # 添加分隔线，优化界面

# 左侧筛选栏（新增“按提及次数筛选”，适配新数据）
with st.sidebar:
    st.header("筛选条件")

    # 筛选1：选择地点（多选，默认全选）
    selected_locations = st.multiselect(
        "1. 选择地点",
        options=df["地点"].unique(),  # 自动读取所有地点
        default=df["地点"].unique()
    )

    # 筛选2：按提及次数范围筛选（新增，量化筛选）
    min_count, max_count = st.slider(
        "2. 地点被提及次数范围",
        min_value=df["被提及次数"].min(),  # 最小次数（默认1）
        max_value=df["被提及次数"].max(),  # 最大次数（默认20）
        value=(df["被提及次数"].min(), df["被提及次数"].max())  # 默认全范围
    )

    # 筛选3：按活动类型关键词筛选（新增，支持模糊匹配）
    activity_keyword = st.text_input(
        "3. 活动类型关键词（可选，如“科举”“交往”）",
        placeholder="输入关键词后回车筛选"
    )

# 4. 按筛选条件过滤数据（核心适配新筛选逻辑）
# 基础筛选：地点 + 提及次数范围
filtered_df = df[
    (df["地点"].isin(selected_locations)) &
    (df["被提及次数"] >= min_count) &
    (df["被提及次数"] <= max_count)
    ]

# 额外筛选：活动类型关键词（若输入关键词则匹配）
if activity_keyword:
    # 模糊匹配“涉及活动类型”列（不区分大小写）
    filtered_df = filtered_df[
        filtered_df["涉及活动类型"].str.contains(activity_keyword, case=False, na=False)
    ]

# 5. 绘制适配新数据的交互式地图（突出“提及次数”）
# 创建地图（中心设为数据集中点，缩放级别8）
m = folium.Map(
    location=[df["纬度"].mean(), df["经度"].mean()],  # 自动计算中心坐标
    zoom_start=8,
    tiles="Stamen Watercolor",  # 水彩风格瓦片
    attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."  # 新增归属说明
)

# 标记聚合：避免多个地点标记重叠
marker_cluster = MarkerCluster().add_to(m)

# 给每个筛选后的地点添加标记（核心适配：显示“提及次数”和“活动类型”）
for _, row in filtered_df.iterrows():
    # 弹出框内容（重点展示“提及次数”，活动类型分行显示更清晰）
    # 将活动类型按逗号分割，用<br>换行
    activity_list = "<br> - ".join(row["涉及活动类型"].split(","))
    popup_content = f"""
    <strong>地点</strong>：{row["地点"]}<br>
    <strong>被提及次数</strong>：{row["被提及次数"]}次<br>
    <strong>涉及活动类型</strong>：<br> - {activity_list}
    """

    # 标记点配置（按“提及次数”调整大小：次数越多，图标越大）
    icon_size = (20 + row["被提及次数"] * 0.5, 20 + row["被提及次数"] * 0.5)  # 大小随次数变化
    folium.Marker(
        location=[row["纬度"], row["经度"]],  # 坐标
        tooltip=f"{row['地点']}（提及{row['被提及次数']}次）",  # 鼠标悬停提示
        popup=folium.Popup(popup_content, max_width=400),  # 弹出框（加宽显示更多内容）
        icon=folium.Icon(
            color="darkred",  # 图标颜色（古典风格）
            icon="book",  # 图标形状（书本，适配文学主题）
            size=icon_size  # 按次数调整大小
        )
    ).add_to(marker_cluster)

# 在Streamlit中显示地图（高度设为700px，更清晰）
st.subheader("地点可视化地图")
st.components.v1.html(m._repr_html_(), height=700)

# 6. 展示筛选后的新数据表格（适配3列格式，添加排序）
st.subheader("筛选后的数据明细")
# 按“被提及次数”降序排列，突出高频地点
display_df = filtered_df[["地点", "被提及次数", "涉及活动类型"]].sort_values("被提及次数", ascending=False)
st.dataframe(
    display_df,
    column_config={  # 美化表格：调整列名和格式
        "地点": st.column_config.TextColumn("地点名称"),
        "被提及次数": st.column_config.NumberColumn("被提及次数", format="%d次"),
        "涉及活动类型": st.column_config.TextColumn("涉及活动类型", width="large")
    },
    use_container_width=True  # 自适应宽度
)

# 7. 新增：数据统计卡片（量化展示新数据核心指标）
st.subheader("数据统计概览")
col1, col2, col3 = st.columns(3)
# 卡片1：筛选后地点数量
col1.metric(
    label="筛选后地点数",
    value=filtered_df["地点"].nunique()
)
# 卡片2：总提及次数
col2.metric(
    label="总提及次数",
    value=filtered_df["被提及次数"].sum()
)
# 卡片3：最高提及次数地点
if not filtered_df.empty:
    max_count_loc = filtered_df.loc[filtered_df["被提及次数"].idxmax(), "地点"]
    max_count = filtered_df["被提及次数"].max()
    col3.metric(
        label="最高提及次数地点",
        value=f"{max_count_loc}（{max_count}次）"
    )
else:
    col3.metric(label="最高提及次数地点", value="无数据")