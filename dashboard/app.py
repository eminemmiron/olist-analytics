import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Olist Analytics", layout="wide")
st.title("📦 Операционная аналитика Olist E-Commerce")

@st.cache_data
def load_data():
    df = pd.read_csv("data/mart_orders.csv")
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])
    df["order_estimated_delivery_date"] = pd.to_datetime(df["order_estimated_delivery_date"])
    df["month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    return df

df = load_data()
delivered = df[df["order_status"] == "delivered"].copy()

# --- Фильтры ---
st.sidebar.header("🔍 Фильтры")

# Фильтр по штату
all_states = sorted(delivered["customer_state"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect(
    "Штат покупателя",
    options=all_states,
    default=all_states
)

# Фильтр по категории
all_categories = sorted(delivered["category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Категория товара",
    options=all_categories,
    default=all_categories
)

# Фильтр по периоду
min_date = delivered["order_purchase_timestamp"].min().date()
max_date = delivered["order_purchase_timestamp"].max().date()
date_from, date_to = st.sidebar.date_input(
    "Период",
    value=[min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Применяем фильтры
delivered = delivered[
    (delivered["customer_state"].isin(selected_states)) &
    (delivered["category"].isin(selected_categories)) & 
    (delivered["order_purchase_timestamp"].dt.date >= date_from) &
    (delivered["order_purchase_timestamp"].dt.date <= date_to)
]

st.sidebar.markdown(f"**Заказов после фильтра:** {delivered['order_id'].nunique():,}")



# --- KPI ---
st.subheader("📊 Ключевые метрики")
total_revenue = delivered["total_value"].sum()
total_orders  = delivered["order_id"].nunique()
avg_check     = delivered["total_value"].mean()
avg_review    = delivered["review_score"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Выручка (BRL)",     f"{total_revenue:,.0f}")
col2.metric("Заказов",           f"{total_orders:,}")
col3.metric("Средний чек (BRL)", f"{avg_check:.1f}")
col4.metric("Средняя оценка",    f"{avg_review:.2f}")

# --- Выручка по месяцам ---
st.subheader("📈 Динамика выручки по месяцам")
monthly = (
    delivered.groupby("month")["total_value"]
    .sum().reset_index().sort_values("month")
)
fig1 = px.line(monthly, x="month", y="total_value",
               labels={"month": "Месяц", "total_value": "Выручка (BRL)"}, markers=True)
st.plotly_chart(fig1, use_container_width=True)

# --- Топ категорий ---
st.subheader("🏆 Топ-10 категорий")
top_cat = (
    delivered.groupby("category")["total_value"]
    .sum().sort_values(ascending=False).head(10).reset_index()
)
fig2 = px.bar(top_cat, x="total_value", y="category", orientation="h",
              labels={"total_value": "Выручка (BRL)", "category": "Категория"})
fig2.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig2, use_container_width=True)

# --- География ---
st.subheader("🗺 География продаж")
geo = (
    delivered.groupby("customer_state")["total_value"]
    .sum().sort_values(ascending=False).reset_index()
)
fig3 = px.bar(geo, x="customer_state", y="total_value",
              labels={"customer_state": "Штат", "total_value": "Выручка (BRL)"})
st.plotly_chart(fig3, use_container_width=True)

# --- Задержка доставки ---
st.subheader("🚚 Задержка доставки по штатам")
delivery = delivered[
    delivered["order_delivered_customer_date"].notna() &
    delivered["order_estimated_delivery_date"].notna()
].copy()
delivery["delay_days"] = (
    delivery["order_delivered_customer_date"] - delivery["order_estimated_delivery_date"]
).dt.days
region_delay = (
    delivery.groupby("customer_state")["delay_days"]
    .mean().reset_index().sort_values("delay_days", ascending=False)
)
fig4 = px.bar(region_delay, x="customer_state", y="delay_days",
              color="delay_days", color_continuous_scale="Greens_r",
              labels={"customer_state": "Штат", "delay_days": "Опережение графика (дни)"},
              title="Все штаты получают заказы раньше обещанного срока")
fig4.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig4, use_container_width=True)

# --- Оценки ---
st.subheader("⭐ Распределение оценок")
reviews = (
    delivered.dropna(subset=["review_score"])
    .groupby("review_score").size().reset_index(name="count")
)
fig5 = px.bar(reviews, x="review_score", y="count",
              color="review_score", color_continuous_scale="RdYlGn",
              labels={"review_score": "Оценка", "count": "Количество"})
fig5.update_layout(xaxis=dict(tickmode="linear", tick0=1, dtick=1),
                   coloraxis_showscale=False)
st.plotly_chart(fig5, use_container_width=True)

# --- RFM ---
st.subheader("👥 RFM-сегменты клиентов")
snapshot_date = df["order_purchase_timestamp"].max()
rfm = (
    delivered.groupby("customer_unique_id")
    .agg(
        recency  =("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary =("total_value", "sum")
    ).reset_index()
)
rfm["R_score"] = pd.qcut(rfm["recency"], q=3, labels=[3, 2, 1])
rfm["F_score"] = pd.qcut(rfm["frequency"].rank(method="first"), q=3, labels=[1, 2, 3])
rfm["M_score"] = pd.qcut(rfm["monetary"], q=3, labels=[1, 2, 3])

def segment(row):
    r, f, m = int(row["R_score"]), int(row["F_score"]), int(row["M_score"])
    if r == 3 and f == 3 and m == 3: return "👑 Чемпионы"
    elif r == 3 and f >= 2:          return "💚 Лояльные"
    elif r == 3 and f == 1:          return "🆕 Новые"
    elif r == 2 and f >= 2:          return "⚠️ Под угрозой"
    elif r == 1 and f >= 2:          return "😴 Спящие"
    else:                            return "❌ Потерянные"

rfm["segment"] = rfm.apply(segment, axis=1)
seg_counts = rfm["segment"].value_counts().reset_index()
seg_counts.columns = ["segment", "count"]

fig6 = px.pie(seg_counts, names="segment", values="count",
              title="Распределение клиентов по сегментам")
st.plotly_chart(fig6, use_container_width=True)


# --- Сезонность ---
st.subheader("📅 Анализ сезонности")

# Добавляем временные признаки
seasonal = delivered.copy()
seasonal["year"]  = seasonal["order_purchase_timestamp"].dt.year
seasonal["month_num"] = seasonal["order_purchase_timestamp"].dt.month
seasonal["month_name"] = seasonal["order_purchase_timestamp"].dt.strftime("%b")
seasonal["weekday"] = seasonal["order_purchase_timestamp"].dt.day_name()

# --- График 1: Продажи по месяцам (все годы вместе) ---
st.markdown("#### 🗓 Средняя выручка по месяцам года")
by_month = (
    seasonal.groupby("month_num")["total_value"]
    .sum().reset_index()
)
month_labels = {1:"Янв",2:"Фев",3:"Мар",4:"Апр",5:"Май",6:"Июн",
                7:"Июл",8:"Авг",9:"Сен",10:"Окт",11:"Ноя",12:"Дек"}
by_month["month_name"] = by_month["month_num"].map(month_labels)

fig7 = px.bar(
    by_month, x="month_name", y="total_value",
    labels={"month_name": "Месяц", "total_value": "Выручка (BRL)"},
    color="total_value", color_continuous_scale="Blues"
)
fig7.update_layout(coloraxis_showscale=False, xaxis={"categoryorder": "array",
                   "categoryarray": list(month_labels.values())})
st.plotly_chart(fig7, use_container_width=True)

# --- График 2: Топ категорий по сезонам ---
st.markdown("#### 🌦 Выручка топ-5 категорий по кварталам")
seasonal["quarter"] = seasonal["order_purchase_timestamp"].dt.quarter.map(
    {1:"Q1 (Янв-Мар)", 2:"Q2 (Апр-Июн)", 3:"Q3 (Июл-Сен)", 4:"Q4 (Окт-Дек)"}
)

top5_cats = (
    seasonal.groupby("category")["total_value"]
    .sum().sort_values(ascending=False).head(5).index.tolist()
)

seasonal_top = seasonal[seasonal["category"].isin(top5_cats)]
by_quarter = (
    seasonal_top.groupby(["quarter", "category"])["total_value"]
    .sum().reset_index()
)

fig8 = px.bar(
    by_quarter, x="quarter", y="total_value",
    color="category", barmode="group",
    labels={"quarter": "Квартал", "total_value": "Выручка (BRL)", "category": "Категория"}
)
st.plotly_chart(fig8, use_container_width=True)

# --- График 3: По дням недели ---
st.markdown("#### 📆 Активность покупателей по дням недели")
weekday_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
weekday_ru    = {"Monday":"Пн","Tuesday":"Вт","Wednesday":"Ср",
                 "Thursday":"Чт","Friday":"Пт","Saturday":"Сб","Sunday":"Вс"}

by_weekday = (
    seasonal.groupby("weekday")["order_id"]
    .nunique().reindex(weekday_order).reset_index()
)
by_weekday["weekday_ru"] = by_weekday["weekday"].map(weekday_ru)

fig9 = px.bar(
    by_weekday, x="weekday_ru", y="order_id",
    labels={"weekday_ru": "День недели", "order_id": "Количество заказов"},
    color="order_id", color_continuous_scale="Purples"
)
fig9.update_layout(coloraxis_showscale=False)
st.plotly_chart(fig9, use_container_width=True)