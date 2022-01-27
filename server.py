from flask import Flask, render_template, Markup#, Response
from datetime import date
from charts import RealTimePlot
import plotly.offline as pyo
import plotly.graph_objects as go
from weather_data import GetWeatherData


app = Flask(__name__)



@app.route("/")
def home():
    rt_plot = RealTimePlot()
    weather = GetWeatherData()
    fingrid_pie_chart = Markup(rt_plot.fingrid_pie_chart())
    fingrid_area_chart = Markup(rt_plot.fingrid_area_chart())
    swe_pie_chart = Markup(rt_plot.swe_pie_chart())
    swe_area_chart = Markup(rt_plot.swe_area_chart())
    swe_area_chart_cons_prod = Markup(rt_plot.swe_area_chart_cons_prod())
    fi_area_chart_cons_prod = Markup(rt_plot.fi_area_chart_cons_prod())
    weather_data_stockholm = weather.get_data("stockholm")
    weather_data_malmo = weather.get_data("malmo")
    weather_data_lulea = weather.get_data("lulea")
    weather_data_sundsvall = weather.get_data("sundsvall")
    weather_data_fi = weather.get_data("helsinki")
    # price_chart_swe = Markup(price_plot.price_chart("swe"))
    # price_chart_fi = Markup(price_plot.price_chart("fi"))

    return render_template('index.html', 
    fi_pie_chart=fingrid_pie_chart, 
    fi_area_chart=fingrid_area_chart,
    swe_pie_chart=swe_pie_chart, 
    swe_area_chart=swe_area_chart, 
    weather_data_stockholm=weather_data_stockholm,
    weather_data_lulea=weather_data_lulea,
    weather_data_malmo=weather_data_malmo,
    weather_data_sundsvall=weather_data_sundsvall,
    weather_data_fi=weather_data_fi,
    swe_area_chart_cons_prod=swe_area_chart_cons_prod,
    fi_area_chart_cons_prod=fi_area_chart_cons_prod
    )




if __name__ == "__main__":
    app.run(debug=True)