import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    # Membaca data dengan penanganan format yang benar
    df = pd.read_csv('Financials.csv')
    
    # Membersihkan nama kolom
    df.columns = df.columns.str.strip()
    
    # Menghapus spasi ekstra dari nilai string
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    # Mengkonversi kolom numerik dengan membersihkan format currency
    numeric_cols = ['Units Sold', 'Manufacturing Price', 'Sale Price', 'Gross Sales', 
                   'Discounts', 'Sales', 'COGS', 'Profit']
    
    for col in numeric_cols:
        if col in df.columns:
            # Menghapus simbol currency dan koma, lalu konversi ke numeric
            df[col] = df[col].astype(str).str.replace('$', '').str.replace(',', '').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Konversi kolom tanggal
    df['Date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
    
    # Membuat kolom Year-Month untuk filtering
    df['Year-Month'] = df['Date'].dt.to_period('M').astype(str)
    
    return df

# Memuat data
df = load_data()

# Sidebar untuk filter
st.sidebar.header("Filter Data")

# Filter Segment
segment_options = ['All'] + list(df['Segment'].unique())
selected_segment = st.sidebar.selectbox("Pilih Segment", segment_options)

# Filter Country
country_options = ['All'] + list(df['Country'].unique())
selected_country = st.sidebar.selectbox("Pilih Negara", country_options)

# Filter Product
product_options = ['All'] + list(df['Product'].unique())
selected_product = st.sidebar.selectbox("Pilih Produk", product_options)

# Filter Discount Band
discount_options = ['All'] + list(df['Discount Band'].unique())
selected_discount = st.sidebar.selectbox("Pilih Diskon", discount_options)

# Filter Tanggal
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
selected_date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [min_date, max_date])

# Tombol Apply Filter
apply_filter = st.sidebar.button("Terapkan Filter")

# Menerapkan filter
filtered_df = df.copy()

if apply_filter or True:  # Auto-apply filter saat pertama kali load
    if selected_segment != 'All':
        filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]
    
    if selected_country != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country]
    
    if selected_product != 'All':
        filtered_df = filtered_df[filtered_df['Product'] == selected_product]
    
    if selected_discount != 'All':
        filtered_df = filtered_df[filtered_df['Discount Band'] == selected_discount]
    
    # Filter tanggal
    start_date = pd.to_datetime(selected_date_range[0])
    end_date = pd.to_datetime(selected_date_range[1])
    filtered_df = filtered_df[(filtered_df['Date'] >= start_date) & (filtered_df['Date'] <= end_date)]

# Header Dashboard
st.title("💰 Financial Dashboard")
st.markdown("---")

# Metrics Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric("Total Penjualan", f"${total_sales:,.2f}")

with col2:
    total_profit = filtered_df['Profit'].sum()
    st.metric("Total Profit", f"${total_profit:,.2f}")

with col3:
    total_units = filtered_df['Units Sold'].sum()
    st.metric("Total Unit Terjual", f"{total_units:,.0f}")

with col4:
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

st.markdown("---")

# Tab untuk visualisasi
tab1, tab2, tab3, tab4 = st.tabs(["📊 Penjualan", "📈 Trend", "🌍 Regional", "📋 Detail Data"])

with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        # Penjualan per Produk
        sales_by_product = filtered_df.groupby('Product')['Sales'].sum().reset_index()
        fig_product_sales = px.bar(
            sales_by_product, 
            x='Product', 
            y='Sales',
            title="Total Penjualan per Produk",
            color='Product',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_product_sales.update_layout(xaxis_title="Produk", yaxis_title="Penjualan ($)")
        st.plotly_chart(fig_product_sales, use_container_width=True)
    
    with col2:
        # Profit per Segment
        profit_by_segment = filtered_df.groupby('Segment')['Profit'].sum().reset_index()
        fig_segment_profit = px.pie(
            profit_by_segment, 
            values='Profit', 
            names='Segment',
            title="Profit per Segment",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_segment_profit.update_layout(showlegend=True)
        st.plotly_chart(fig_segment_profit, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        # Penjualan per Negara
        sales_by_country = filtered_df.groupby('Country')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
        fig_country_sales = px.bar(
            sales_by_country.head(10), 
            x='Sales', 
            y='Country',
            title="Top 10 Negara berdasarkan Penjualan",
            orientation='h',
            color='Sales',
            color_continuous_scale='Blues'
        )
        fig_country_sales.update_layout(xaxis_title="Penjualan ($)", yaxis_title="Negara")
        st.plotly_chart(fig_country_sales, use_container_width=True)
    
    with col4:
        # Diskon vs Profit
        discount_profit = filtered_df.groupby('Discount Band')['Profit'].sum().reset_index()
        fig_discount_profit = px.bar(
            discount_profit, 
            x='Discount Band', 
            y='Profit',
            title="Profit berdasarkan Kategori Diskon",
            color='Discount Band',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_discount_profit.update_layout(xaxis_title="Kategori Diskon", yaxis_title="Profit ($)")
        st.plotly_chart(fig_discount_profit, use_container_width=True)

with tab2:
    # Trend Penjualan per Bulan
    monthly_sales = filtered_df.groupby('Year-Month')['Sales'].sum().reset_index()
    monthly_sales['Date'] = pd.to_datetime(monthly_sales['Year-Month'])
    monthly_sales = monthly_sales.sort_values('Date')
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly_sales['Date'], 
        y=monthly_sales['Sales'],
        mode='lines+markers',
        name='Penjualan',
        line=dict(color='blue', width=3)
    ))
    
    fig_trend.update_layout(
        title="Trend Penjualan Bulanan",
        xaxis_title="Tanggal",
        yaxis_title="Penjualan ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Profit Trend
    monthly_profit = filtered_df.groupby('Year-Month')['Profit'].sum().reset_index()
    monthly_profit['Date'] = pd.to_datetime(monthly_profit['Year-Month'])
    monthly_profit = monthly_profit.sort_values('Date')
    
    fig_profit_trend = go.Figure()
    fig_profit_trend.add_trace(go.Scatter(
        x=monthly_profit['Date'], 
        y=monthly_profit['Profit'],
        mode='lines+markers',
        name='Profit',
        line=dict(color='green', width=3)
    ))
    
    fig_profit_trend.update_layout(
        title="Trend Profit Bulanan",
        xaxis_title="Tanggal",
        yaxis_title="Profit ($)",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_profit_trend, use_container_width=True)
    
    # Units Sold Trend
    monthly_units = filtered_df.groupby('Year-Month')['Units Sold'].sum().reset_index()
    monthly_units['Date'] = pd.to_datetime(monthly_units['Year-Month'])
    monthly_units = monthly_units.sort_values('Date')
    
    fig_units_trend = go.Figure()
    fig_units_trend.add_trace(go.Scatter(
        x=monthly_units['Date'], 
        y=monthly_units['Units Sold'],
        mode='lines+markers',
        name='Unit Terjual',
        line=dict(color='orange', width=3)
    ))
    
    fig_units_trend.update_layout(
        title="Trend Unit Terjual Bulanan",
        xaxis_title="Tanggal",
        yaxis_title="Unit Terjual",
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_units_trend, use_container_width=True)

with tab3:
    # Analisis Regional
    col1, col2 = st.columns(2)
    
    with col1:
        # Penjualan per Negara (Map)
        country_sales = filtered_df.groupby('Country')['Sales'].sum().reset_index()
        
        # Membuat mapping negara ke kode negara untuk peta
        country_mapping = {
            'Canada': 'CAN',
            'Germany': 'DEU',
            'France': 'FRA',
            'Mexico': 'MEX',
            'United States of America': 'USA'
        }
        
        country_sales['Country_Code'] = country_sales['Country'].map(country_mapping)
        
        fig_map = px.choropleth(
            country_sales,
            locations="Country_Code",
            color="Sales",
            hover_name="Country",
            color_continuous_scale=px.colors.sequential.Plasma,
            title="Penjualan per Negara"
        )
        
        fig_map.update_layout(geo=dict(showframe=False, showcoastlines=True))
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col2:
        # Segment Performance per Negara
        segment_country = filtered_df.groupby(['Country', 'Segment'])['Sales'].sum().reset_index()
        fig_segment_country = px.bar(
            segment_country,
            x='Country',
            y='Sales',
            color='Segment',
            title="Performa Segment per Negara",
            barmode='group'
        )
        fig_segment_country.update_layout(xaxis_title="Negara", yaxis_title="Penjualan ($)")
        st.plotly_chart(fig_segment_country, use_container_width=True)
    
    # Product Performance per Negara
    product_country = filtered_df.groupby(['Country', 'Product'])['Sales'].sum().reset_index()
    fig_product_country = px.bar(
        product_country,
        x='Country',
        y='Sales',
        color='Product',
        title="Performa Produk per Negara",
        barmode='group'
    )
    fig_product_country.update_layout(xaxis_title="Negara", yaxis_title="Penjualan ($)")
    st.plotly_chart(fig_product_country, use_container_width=True)

with tab4:
    # Tabel Detail Data
    st.subheader("Detail Data Finansial")
    
    # Menampilkan statistik dasar
    st.write("Statistik Dasar:")
    st.write(filtered_df.describe())
    
    # Tabel data dengan opsi sorting
    st.write("Data Transaksi:")
    
    # Selectbox untuk memilih kolom sorting
    sort_column = st.selectbox("Pilih kolom untuk sorting", filtered_df.columns)
    sort_order = st.radio("Urutan", ("Ascending", "Descending"))
    
    # Menerapkan sorting
    if sort_order == "Ascending":
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=True)
    else:
        sorted_df = filtered_df.sort_values(by=sort_column, ascending=False)
    
    # Menampilkan tabel dengan pagination
    page_size = 10
    page = st.number_input("Halaman", min_value=1, max_value=(len(sorted_df) // page_size) + 1, value=1)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    st.dataframe(sorted_df.iloc[start_idx:end_idx], use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Financial Dashboard © 2024")