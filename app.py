# -------------- 模块1：导入需要的工具 --------------
import streamlit as st  # 用于搭建网页
import folium  # 用于画地图
from folium.plugins import MarkerCluster  # 用于聚合标记点
import pandas as pd  # 用于处理表格数据

# -------------- 模块2：加载并处理数据 --------------
# 加载自己的CSV数据（确保CSV文件和app.py在同一个文件夹中）
# 如果你的CSV文件名不是ruilin_data.csv，这里要修改
df = pd.read_csv("ruilin_data.csv")

# 给每个地点添加经纬度（关键！地图需要坐标才能定位）
# 如果你有其他地点，按格式补充（纬度在前，经度在后）
location_coords = {
    "北京": [39.9042, 116.4074],  # 更精确的坐标
    "苏州": [31.2993, 120.6195],
    "济南": [36.6512, 117.1200],
    "南京": [32.0603, 118.7969],
    "湖州": [30.8672, 120.0934],
    "杭州": [30.2741, 120.1551],
    "扬州": [32.3932, 119.4989]
    # 补充其他地点，例如："上海": [31.2304, 121.4737]
}

# 将经纬度添加到表格中（自动匹配“地点”列）
df["纬度"] = df["地点"].map(lambda x: location_coords[x][0])  # 提取纬度
df["经度"] = df["地点"].map(lambda x: location_coords[x][1])  # 提取经度

# -------------- 模块3：创建Streamlit网页界面 --------------
# 设置网页标题
st.title("《儒林外史》地理活动可视化地图")
st.write("可通过左侧筛选条件查看不同章节、地点的人物活动")

# 左侧筛选栏
st.sidebar.header("筛选条件")
# 章节筛选（默认显示全部，可多选）
selected_chapter = st.sidebar.multiselect(
    "选择章节",
    options=df["章节"].unique(),  # 自动获取所有章节
    default=df["章节"].unique()  # 默认选中全部
)
# 地点筛选
selected_location = st.sidebar.multiselect(
    "选择地点",
    options=df["地点"].unique(),
    default=df["地点"].unique()
)
# 活动类型筛选
selected_activity = st.sidebar.multiselect(
    "选择活动类型",
    options=df["活动类型"].unique(),
    default=df["活动类型"].unique()
)

# 根据筛选条件过滤数据
filtered_df = df[
    (df["章节"].isin(selected_chapter)) &
    (df["地点"].isin(selected_location)) &
    (df["活动类型"].isin(selected_activity))
]

# -------------- 模块4：绘制交互式地图 --------------
# 创建地图（中心设为中国东部，缩放级别8）
m = folium.Map(
    location=[32.0, 118.0],  # 中心坐标（大致在南京附近）
    zoom_start=8,
    tiles="CartoDB positron"  # 浅色底图，清晰显示标记
)

# 创建标记点聚合（避免大量标记重叠）
marker_cluster = MarkerCluster().add_to(m)

# 给每个筛选后的条目添加标记
for idx, row in filtered_df.iterrows():
    # 标记点弹出框内容（点击标记显示的信息）
    popup_text = f"""
    <strong>章节</strong>：{row['章节']}<br>
    <strong>地点</strong>：{row['地点']}<br>
    <strong>人物</strong>：{row['人物']}<br>
    <strong>活动类型</strong>：{row['活动类型']}<br>
    <strong>原文摘要</strong>：{row['原文摘要']}
    """
    # 添加标记到地图
    folium.Marker(
        location=[row["纬度"], row["经度"]],  # 坐标
        tooltip=row["地点"],  # 鼠标悬停显示地点
        popup=folium.Popup(popup_text, max_width=300),  # 弹出框
        icon=folium.Icon(color="blue")  # 标记颜色（可改：red/green/orange等）
    ).add_to(marker_cluster)

# 在Streamlit中显示地图
st.components.v1.html(m._repr_html_(), height=600)  # 高度600像素

# -------------- 模块5：显示筛选后的数据表格（可选） --------------
st.subheader("筛选后的数据明细")
st.dataframe(filtered_df)  # 显示表格