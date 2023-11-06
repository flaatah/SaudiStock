# Import Streamlit and yfinance modules
import streamlit as st
import yfinance as yf
from datetime import date
from prophet.plot import plot_plotly, plot_components_plotly
from plotly import graph_objs as go
import pandas as pd
from prophet import Prophet
from datetime import datetime
import datetime
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


st.title("التنبؤ بأسعار الاسهم السعودية")
st.write("صفحة خاصة للتنبؤ لبعض أسعار السهم السعودية ")
st.warning("الصفحة عبارة عن وسيلة لمساعدة المستخدمين لمعرفة اتجاه الاسعار ولسيت نصيحة أو توصية للشراء",
            icon="⚠️")




# Define the start and end dates
START = "2000-01-01"
# datetime.strftime(START, "%Y-%m-%d")
TODAY = datetime.datetime.now().strftime("%Y-%m-%d")

# Create a dictionary of symbols and names of the companies
companies = {
    "2222.SR": "ارامكو", 
    "3060.SR": "اسمنت ينبع",
    "4220.SR": "اعمار",
    "1180.SR": "الاهلي",
    "7010.SR": "الاتصالات",
    "8010.SR": "التعاونية",
    "1120.SR": "الراجحي",
    "1010.SR": "الرياض",
    "2280.SR": "المراعي",
    "4164.SR": "النهدي",
    "2010.SR": "سابك",
    "2020.SR": "سابك للمغذيات",
    "2050.SR": "صافولا",
    "5110.SR": "كهرباء السعودية",
    "1211.SR": "معادن",
    "7020.SR": "موبايلي",
        
}

# Create a list of names for the select box options
names = list(companies.values())

# Display a select box widget with the names as options
selected_name = st.selectbox("اختر الشركة", names)

# Get the symbol corresponding to the selected name
selected_symbol = [symbol for symbol, name in companies.items() if name == selected_name][0]

# Display the selected symbol
# Slider for user to choose number of months
# The model can predict up to 12 months
n_months = st.slider("اختر عدد الشهور", 0, 12)
st.write(" اختيار 0 يعني عدم التنبؤ \n أما اختيار من 1-12 التبنؤ بالاشهر المستقبلية")
period = n_months 

# Download and cache the stock data for the selected symbol
data = yf.download(selected_symbol, START, TODAY)
data_copy = data.copy()
data.reset_index(inplace = True)

# Display data's tail
st.write("البيانات الحقيقية لآخر ستة أيام")

# Rename columns to Arabic
data_arabic = data.rename(columns={
    "Date": "التاريخ",
    "Open": "الافتتاح",
    "High": "أعلى سعر",
    "Low": "أدنى سعر",
    "Close": "الإغلاق",
    "Adj Close": "سعر الإغلاق المعدل",
    "Volume": "كمية التداول"
})

# Reorder columns
desired_order = ["كمية التداول", "سعر الإغلاق المعدل", "الإغلاق", "أدنى سعر", "أعلى سعر" ,"الافتتاح" ,"التاريخ"] #,"التاريخ"]
data_arabic = data_arabic[desired_order]

# Display tail
st.write(data_arabic.tail(6))



# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.update_layout(
		    xaxis_title="التاريخ",
		    yaxis_title="الأسعار بالريال السعودي",
            title='عرض البيانات الزمنية التاريخية')
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="الافتتاح"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="الاغلاق"))
    fig.layout.update(#title_text='عرض البيانات الزمنية التاريخية',
         xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)	
plot_raw_data()


# Predict forecast with Prophet.
train = data[['Date','Close']]
train = train.rename(columns={"Date": "ds", "Close": "y"})

#To datetime
train['ds'] = pd.to_datetime(train['ds'])

#Fit and predict
m = Prophet()
m.add_country_holidays(country_name='SA')
m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
m.fit(train)
future = m.make_future_dataframe(periods=period, freq="M")
forecast = m.predict(future)

# Show and plot forecast
st.subheader('البيانات المتنبؤة')
forecast_copy = forecast.copy()

# Rename the columns
forecast_arabic = forecast.rename(columns={'ds': "التاريخ", "trend":"اتجاه الأسعار",
										    "yhat": "القيمة المتنبئة", "yhat_lower": "الحد الأدنى المتنبئ",
											  "yhat_upper": "الحد الأعلى المتنبئ"})

st.write(forecast_arabic[["الحد الأعلى المتنبئ",  "الحد الأدنى المتنبئ", "القيمة المتنبئة",
					    "اتجاه الأسعار", "التاريخ"]].tail(12))											  

# def plot_forecast_data():
# 	fig = plot_plotly.Figure()
#   fig.add_trace(plot_plotly.(x=data['Date'], y=data['Open'], name="الافتتاح"))
# 	fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="الاغلاق"))
# 	fig.layout.update(title_text='عرض البيانات الزمنية التاريخية', xaxis_rangeslider_visible=True)
# 	st.plotly_chart(fig)	
# plot_raw_data()


#fig1 = plot_plotly(m, forecast)

# Customize the labels for the x-axis and y-axis
def plot_forecast_data(m, forecast):
    fig1 = go.Figure()
    fig1.update_layout(
        xaxis_title="التاريخ",
        yaxis_title="الأسعار بالريال السعودي",
        title=f' عرض توقع الاسعار ل {period} أشهر')
    fig1.add_trace(go.Scatter(x=forecast['ds'], y=train['y'],name='الحقيقية'))
    fig1.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],name='المتنبئة'))
    fig1.layout.update(xaxis_rangeslider_visible=True)
    

# Display the customized plot in Streamlit or any other environment you're using
    st.plotly_chart(fig1)
plot_forecast_data(m, forecast)

# st.write("مكونات التنبؤ")
# fig2 = m.plot_components(forecast)
# st.write(fig2)
#m.plot_plotly()