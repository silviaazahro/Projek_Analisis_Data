import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import plotly.express as px

# Load dataset
dataset = pd.read_csv("https://raw.githubusercontent.com/silviaazahro/Projek_Analisis_Data/refs/heads/main/dataset_cleaned.csv")

# Konversi ke datetime
columns_to_convert = ["order_purchase_timestamp", "order_delivered_customer_date"]
for col in columns_to_convert:
    dataset[col] = pd.to_datetime(dataset[col])

# Tambahan kolom untuk analisis
dataset["day_of_week"] = dataset["order_purchase_timestamp"].dt.day_name()
dataset["month"] = dataset["order_purchase_timestamp"].dt.to_period("M")
dataset["delivery_time"] = (dataset["order_delivered_customer_date"] - dataset["order_purchase_timestamp"]).dt.days

# Sidebar menu
st.sidebar.title("📊 Dashboard Analisis Data")
menu = st.sidebar.selectbox("Pilih Analisis", [
    "Pola Transaksi", "Waktu Pengiriman vs Review Score", "Kategori Produk", "RFM Analysis"
])

# 1️⃣ Pola Transaksi
if menu == "Pola Transaksi":
    st.title("📅 Pola Jumlah Transaksi")
    st.subheader("Jumlah Transaksi per Hari dalam Seminggu")
    day_counts = dataset["day_of_week"].value_counts().reset_index()
    day_counts.columns = ["Hari", "Jumlah Transaksi"]
    fig = px.bar(day_counts, x="Hari", y="Jumlah Transaksi", 
                 title="Jumlah Transaksi per Hari")
    st.plotly_chart(fig)

    st.subheader("Jumlah Transaksi per Bulan")
    monthly_orders = dataset.groupby("month")["order_id"].count().reset_index()
    monthly_orders["month"] = monthly_orders["month"].astype(str)
    fig = px.line(monthly_orders, x="month", y="order_id", markers=True, title="Jumlah Transaksi per Bulan")
    st.plotly_chart(fig)

# 2️⃣ Hubungan Waktu Pengiriman dengan Review Score
elif menu == "Waktu Pengiriman vs Review Score":
    st.title("🚚 Waktu Pengiriman vs Review Score")
    bins = [0, 5, 10, 15, 20, 30, 60, dataset["delivery_time"].max()]
    labels = ["0-5", "6-10", "11-15", "16-20", "21-30", "31-60", "60+"]
    dataset["delivery_time_range"] = pd.cut(dataset["delivery_time"], bins=bins, labels=labels, include_lowest=True)
    
    review_data = dataset.groupby("delivery_time_range")["review_score"].mean().reset_index()
    fig = px.bar(review_data, x="delivery_time_range", y="review_score", title="Waktu Pengiriman vs Review Score")
    st.plotly_chart(fig)

# 3️⃣ Produk dalam Kategori yang Paling Sering Dibeli
elif menu == "Kategori Produk":
    st.title("🛍️ Kategori Produk yang Paling Sering Dibeli")
    product_counts = dataset["product_category_name"].value_counts().head(10).reset_index()
    product_counts.columns = ["Kategori", "Jumlah Pembelian"]
    fig = px.bar(product_counts, x="Kategori", y="Jumlah Pembelian", 
                 title="Kategori Produk yang Paling Sering Dibeli")
    st.plotly_chart(fig)

    product_prices = dataset.groupby("product_category_name")["price"].mean().sort_values(ascending=False).head(10).reset_index()
    fig = px.bar(product_prices, x="price", y="product_category_name", orientation='h',
                 title="Harga Rata-rata per Kategori Produk")
    st.plotly_chart(fig)

# 4️⃣  RFM Analysis
elif menu == "RFM Analysis":
    st.title("📈 RFM Analysis - Segmentasi Pelanggan")
    reference_date = dataset["order_purchase_timestamp"].max()
    rfm = dataset.groupby("customer_unique_id").agg({
        "order_purchase_timestamp": lambda x: (reference_date - x.max()).days,  # Recency
        "order_id": "count",  # Frequency
        "price": "sum"  # Monetary
    }).reset_index()
    rfm.columns = ["customer_id", "Recency", "Frequency", "Monetary"]
    
    st.subheader("Distribusi Recency")
    fig = px.histogram(rfm, x="Recency", nbins=20, title="Distribusi Recency")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Distribusi Frequency")
    fig = px.histogram(rfm, x="Frequency", nbins=20, title="Distribusi Frequency")
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Distribusi Monetary")
    fig = px.histogram(rfm, x="Monetary", nbins=20, title="Distribusi Monetary")
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.info("🔹 Dibuat dengan Streamlit untuk analisis data interaktif")
