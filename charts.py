import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import plotly.offline as pyo
from datetime import datetime, date, timedelta
import json, os
import pandas as pd
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv


class RealTimePlot():

    def __init__(self):
                    #Colors [wind, nuclear, hydro, small scale, CHP_prod, CHP_district_heating]
        self.fi_colors = ["#40E0D0", "#778899", "#4682B4", "#000000", "#DB7093", "#FF4500"]
        self.swe_colors = ["#778899", "#FF4500", "#40E0D0", "#8B008B", "#4682B4", "#B22222"]
        self.cons_prod_colors = ["rgba(139,0,0, 0.5)", "rgba(30,144,255, 0.5)"]
        self.today = date.today().strftime('%Y-%m-%d')

        price_filename_fi = f"fi_elprice_{self.today}.json"
        price_filename_swe = f"swe_elprice_{self.today}.json"

        load_dotenv("creds.env")
        price_container_name = "el-price"
        container_name = "real-time-prod-data"
        storage_url = os.getenv("SAS_URL")
        storage_token = os.getenv("SAS_TOKEN")
        fi_filename = f"fi_real_time_data_{self.today}.json"
        swe_filename = f"swe_real_time_data_{self.today}.json"
        blob_service_client = BlobServiceClient(account_url=storage_url, credential=storage_token)

        blob_fi = blob_service_client.get_blob_client(container_name, fi_filename)
        self.fingrid_data = dict(json.loads(blob_fi.download_blob().readall()))

        blob_swe = blob_service_client.get_blob_client(container_name, swe_filename)
        self.swe_data = dict(json.loads(blob_swe.download_blob().readall()))

        price_blob_fi = blob_service_client.get_blob_client(price_container_name, price_filename_fi)
        self.fi_elprice = dict(json.loads(price_blob_fi.download_blob().readall()))

        price_blob_swe = blob_service_client.get_blob_client(price_container_name, price_filename_swe)
        self.swe_elprice = dict(json.loads(price_blob_swe.download_blob().readall()))


    def fingrid_area_chart(self):
        time_shift = 2 #Finnish time zone is EET
        time_label = [datetime.strptime(i["start_time"].replace("+0000", "").replace("T", " "), "%Y-%m-%d %H:%M:%S") + timedelta(hours=time_shift)\
             for i in self.fingrid_data["wind_prod"]]
        data = {key:[i["value"] for i in value] for key, value in self.fingrid_data.items() if key != "consumption"}
        data["time"] = time_label
        
        df = pd.DataFrame(data)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        n = 0
        for column_name in list(df.columns)[:len(df.columns) - 1]:
            if n == 0:
                fill = "tozeroy"
            else:
                fill = "tonexty"

            today = date.today().strftime("%Y-%m-%d %H:%M:%S")
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            fig.add_trace(go.Scatter(name=column_name, x=df.time, y=df[column_name], 
            hoverinfo="x+y", stackgroup='one', fill=fill, fillcolor=self.fi_colors[n], mode="none"
            )) # fill down to xaxis
            n += 1

        
        fig.update_layout(xaxis_range=[datetime.strptime(today, "%Y-%m-%d %H:%M:%S"), datetime.strptime(tomorrow, "%Y-%m-%d %H:%M:%S")])
        fig.update_layout(hovermode="x unified")
        fig.update_layout(title={
        'text': "Finland Energy Production Composition Over Time",
        'y':0.97,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        font=dict(size=12))

        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Energy Production [MW]", secondary_y=False)
        fig.update_yaxes(title_text="Electricity Price [€ cents/kWh]", secondary_y=True)

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        
        return chart_div_string


    def fingrid_pie_chart(self):
        labels = [key for key in self.fingrid_data if key != "consumption"]
        values = [self.fingrid_data[key][-1]["value"] for key in self.fingrid_data if key != "consumption"]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=12,
                        marker=dict(colors=self.fi_colors, line=dict(color='#F8F8FF', width=2)))
        fig.update_layout(title={
        'text': "Finland Current Energy Production Composition",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}, font=dict(size=12))

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return chart_div_string


    def swe_area_chart(self):
        df = pd.DataFrame.from_dict(self.swe_data, orient="index").reset_index().rename(columns={"index": "time"})
        fig = make_subplots(specs=[[{"secondary_y": True}]]) 
        n = 0

        
        for column_name in list(df.columns)[1:len(df.columns) - 1]:
            if n == 0:
                fill = "tozeroy"
            else:
                fill = "tonexty"

            today = date.today().strftime("%Y-%m-%d %H:%M:%S")
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            fig.add_trace(go.Scatter(name=column_name, x=df.time, y=df[column_name], 
            hoverinfo="x+y", stackgroup='one', fill=fill, fillcolor=self.swe_colors[n], mode="none"
            )) # fill down to xaxis
            n += 1

        
        fig.update_layout(xaxis_range=[datetime.strptime(today, "%Y-%m-%d %H:%M:%S"), datetime.strptime(tomorrow, "%Y-%m-%d %H:%M:%S")])
        fig.update_layout(hovermode="x unified")
        fig.update_layout(title={
        'text': "SWE Energy Production Composition Over Time",
        'y':0.95,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        font=dict(size=12))
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Energy Production [MW]", secondary_y=False)
        fig.update_yaxes(title_text="Electricity Price [Swedish cents/kWh]", secondary_y=True)

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        
        return chart_div_string


    def swe_pie_chart(self):
        latest_timestamp = list(self.swe_data)[-1]
        print(latest_timestamp)
        labels = [key for key in self.swe_data[latest_timestamp] if key != "consumption"]
        values = [self.swe_data[latest_timestamp][key] for key in self.swe_data[latest_timestamp] if key != "consumption"]

        fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
        fig.update_traces(hoverinfo='label+value', textinfo='percent', textfont_size=12,
                        marker=dict(colors=self.swe_colors, line=dict(color='#F8F8FF', width=2)))
        fig.update_layout(title={
        'text': "SWE Current Energy Production Composition",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'}, 
        font=dict(size=12))

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return chart_div_string

    def swe_area_chart_cons_prod(self):
        df = pd.DataFrame.from_dict(self.swe_data, orient="index").reset_index().rename(columns={"index": "time"})
        df["total_prod"] = df.drop("consumption", 1).drop("time", 1).sum(axis=1)
        df.consumption = df.consumption.fillna(0)

        #Transforming price data.
        df_price = pd.DataFrame(self.swe_elprice)
        df_price = df_price.rename(columns={self.today: "price"}).reset_index().rename(columns={"index": "time"})
        df_price.time = df_price.time.str.replace(".", ":")
        df_price.time = date.today().strftime('%Y-%m-%d') + " " + df_price.time.astype(str)
        df_price.time = pd.to_datetime(df_price.time, format="%Y-%m-%d %H:%M:%S")

        colors = self.cons_prod_colors[:]
        column_names = list(df.columns)[-2:len(df.columns)]
        if df.consumption.sum() < df.total_prod.sum():
            column_names.reverse()
            colors.reverse()

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        n = 0
        for column_name in column_names:
            today = date.today().strftime("%Y-%m-%d %H:%M:%S")
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            fig.add_trace(go.Scatter(name=column_name, x=df.time, y=df[column_name], 
            hoverinfo="x+y", fill="tozeroy", fillcolor=colors[n], line=dict(color=colors[n]), mode="lines"
            ))
            n += 1

        fig.add_trace(
            go.Scatter(
                name="El price (SE3)", 
                x=df_price.time, 
                y=df_price.price, 
                line=dict(color='darkslateblue', width=2)
                ), 
            secondary_y=True
            )

        fig.update_layout(xaxis_range=[datetime.strptime(today, "%Y-%m-%d %H:%M:%S"), datetime.strptime(tomorrow, "%Y-%m-%d %H:%M:%S")])
        fig.update_layout(hovermode="x unified")
        fig.update_layout(title={
        'text': "SWE Electricity Price Over Time",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        font=dict(size=12))
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Consumption & Production [MW]", secondary_y=False)
        fig.update_yaxes(title_text="Electricity Price [Swedish cents/kWh]", secondary_y=True)

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return chart_div_string

    def fi_area_chart_cons_prod(self):
        time_shift = 2 #Finnish time zone is EET
        time_label = [datetime.strptime(i["start_time"].replace("+0000", "").replace("T", " "), "%Y-%m-%d %H:%M:%S") + timedelta(hours=time_shift)\
             for i in self.fingrid_data["wind_prod"]]
        data = {key:[i["value"] for i in value] for key, value in self.fingrid_data.items() if key}
        data["time"] = time_label
        
        df = pd.DataFrame(data)
        new_column_list = df.columns.tolist()[:-1]
        new_column_list.insert(0, "time")
        df = df[new_column_list]

        df["total_prod"] = df.drop("consumption", 1).drop("time", 1).sum(axis=1)

        #Transforming price data.
        df_price = pd.DataFrame(self.fi_elprice)
        df_price = df_price.rename(columns={self.today: "price"}).reset_index().rename(columns={"index": "time"})
        df_price.time = df_price.time.str.replace(".", ":")
        df_price.time = date.today().strftime('%Y-%m-%d') + " " + df_price.time.astype(str)
        df_price.time = pd.to_datetime(df_price.time, format="%Y-%m-%d %H:%M:%S")

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        n = 0
        colors = self.cons_prod_colors[:]
        column_names = list(df.columns)[-2:len(df.columns)]
        print(colors)
        if df.consumption.sum() < df.total_prod.sum():

            column_names.reverse()
            colors.reverse()

        print(column_names, colors)
        for column_name in column_names:
            today = date.today().strftime("%Y-%m-%d %H:%M:%S")
            tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            fig.add_trace(go.Scatter(name=column_name, x=df.time, y=df[column_name], 
            hoverinfo="x+y", fill="tozeroy", fillcolor=colors[n], line=dict(color=colors[n]), mode="lines"
            ))
            n += 1

        fig.add_trace(
            go.Scatter(
                name="El price", 
                x=df_price.time, 
                y=df_price.price, 
                line=dict(color='darkslateblue', width=2)
                ), 
            secondary_y=True
            )

        fig.update_layout(xaxis_range=[datetime.strptime(today, "%Y-%m-%d %H:%M:%S"), datetime.strptime(tomorrow, "%Y-%m-%d %H:%M:%S")])
        fig.update_layout(hovermode="x unified")
        fig.update_layout(title={
        'text': "FI Electricity Price Over Time",
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'},
        legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        font=dict(size=12))
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Consumption & Production [MW]", secondary_y=False)
        fig.update_yaxes(title_text="Electricity Price [€ cents/kWh]", secondary_y=True)

        chart_div_string = pyo.offline.plot(fig, include_plotlyjs=False, output_type='div')
        return chart_div_string
