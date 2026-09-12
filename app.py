from pathlib import Path
import pandas as pd
import numpy as np
from dash import Dash, dcc, html, Input, Output, State, dash_table, no_update
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "sources.csv"

MONTHS_ID = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",7:"Jul",8:"Agu",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
COLORS = {"primary":"#2563EB","secondary":"#14B8A6","accent":"#F59E0B","danger":"#EF4444","purple":"#8B5CF6","ink":"#0F172A","muted":"#64748B"}

def load_data(path):
    df = pd.read_csv(path, decimal=",")
    for c in ["tanggal_pemesanan","tanggal_pengiriman","clean_tanggal_pengiriman"]:
        df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ["penjualan","keuntungan","kuantitas","diskon"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["clean_kota"] = df["clean_kota"].fillna(df["kota"]).fillna("Tidak diketahui")
    df["tahun"] = df["tanggal_pemesanan"].dt.year
    df["bulan_num"] = df["tanggal_pemesanan"].dt.month
    df["bulan"] = df["bulan_num"].map(MONTHS_ID)
    df["periode"] = df["tanggal_pemesanan"].dt.to_period("M").dt.to_timestamp()
    df["durasi_pengiriman"] = (df["clean_tanggal_pengiriman"] - df["tanggal_pemesanan"]).dt.days.clip(lower=0)
    df["margin"] = np.where(df["penjualan"] != 0, df["keuntungan"] / df["penjualan"], 0)
    return df

df = load_data(DATA_PATH)

def rupiah(v):
    a=abs(v)
    if a >= 1_000_000_000: s=f"Rp{a/1_000_000_000:.2f} M"
    elif a >= 1_000_000: s=f"Rp{a/1_000_000:.1f} jt"
    elif a >= 1_000: s=f"Rp{a/1_000:.1f} rb"
    else: s=f"Rp{a:,.0f}"
    return f"-{s}" if v < 0 else s

def options(col):
    return [{"label":str(x),"value":x} for x in sorted(df[col].dropna().unique())]

def empty_fig(msg="Tidak ada data untuk filter ini"):
    fig=go.Figure()
    fig.add_annotation(text=msg,x=.5,y=.5,xref="paper",yref="paper",showarrow=False,font=dict(size=17,color=COLORS["muted"]))
    fig.update_layout(template="plotly_white",xaxis_visible=False,yaxis_visible=False,height=360)
    return fig

def polish(fig, height=380):
    fig.update_layout(template="plotly_white",height=height,margin=dict(l=30,r=20,t=55,b=35),font=dict(family="Inter,Segoe UI,Arial",color=COLORS["ink"]),legend_title_text="",hoverlabel=dict(bgcolor="white"))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="#E2E8F0")
    return fig

def card(title, value_id, sub_id, tone):
    return dbc.Card(dbc.CardBody([html.Div(title,className="kpi-label"),html.Div(id=value_id,className="kpi-value"),html.Div(id=sub_id,className="kpi-sub")]),className=f"kpi-card {tone}")

app=Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title="Supermarket BI by Kendrick Filbert"

sidebar=html.Div([
    html.Div([html.Div("SI",className="brand-mark"),html.Div([html.H4("Supermarket BI",className="mb-0"),html.Small("by Kendrick Filbert")])],className="brand-wrap"),
    html.Hr(),
    html.Label("Rentang tahun",className="filter-label"),
    dcc.RangeSlider(id="year",min=int(df.tahun.min()),max=int(df.tahun.max()),step=1,value=[int(df.tahun.min()),int(df.tahun.max())],marks={int(y):str(int(y)) for y in sorted(df.tahun.dropna().unique())},tooltip={"placement":"bottom"}),
    html.Label("Wilayah",className="filter-label mt-4"), dcc.Dropdown(id="wilayah",options=options("wilayah"),multi=True,placeholder="Semua wilayah"),
    html.Label("Kota",className="filter-label mt-3"), dcc.Dropdown(id="kota",options=options("clean_kota"),multi=True,placeholder="Semua kota"),
    html.Label("Kategori",className="filter-label mt-3"), dcc.Dropdown(id="kategori",options=options("kategori"),multi=True,placeholder="Semua kategori"),
    html.Label("Segmen",className="filter-label mt-3"), dcc.Dropdown(id="segmen",options=options("segmen"),multi=True,placeholder="Semua segmen"),
    dbc.Button([html.I(className="bi bi-arrow-counterclockwise me-2"),"Reset filter"],id="reset",outline=True,color="light",className="w-100 mt-4"),
    html.Div([html.Small("Dataset bersih"),html.Strong(f"{len(df):,} baris"),html.Small(f"{df.tanggal_pemesanan.min():%d %b %Y} – {df.tanggal_pemesanan.max():%d %b %Y}")],className="dataset-note")
],className="sidebar")

header=html.Div([html.Div([html.H2("Supermarket BI by Kendrick Filbert"),html.P("Insight penjualan, profitabilitas, pelanggan, produk, dan operasi dalam satu tampilan interaktif.")]),html.Div([dbc.Button([html.I(className="bi bi-download me-2"),"Unduh data terfilter"],id="download-btn",color="primary"),dcc.Download(id="download")])],className="topbar")

content=html.Div([
    header,
    dbc.Row([dbc.Col(card("Total Penjualan","sales","sales-sub","blue"),md=3),dbc.Col(card("Total Keuntungan","profit","profit-sub","teal"),md=3),dbc.Col(card("Margin Keuntungan","margin","margin-sub","purple"),md=2),dbc.Col(card("Pesanan Unik","orders","orders-sub","amber"),md=2),dbc.Col(card("Pelanggan Unik","customers","customers-sub","slate"),md=2)],className="g-3"),
    dcc.Tabs(id="tabs",value="overview",children=[
        dcc.Tab(label="Executive Overview",value="overview"),dcc.Tab(label="Profitability",value="profitability"),dcc.Tab(label="Product Intelligence",value="product"),dcc.Tab(label="Customer & Operations",value="customer")
    ],className="main-tabs"),
    html.Div(id="tab-content"),
    html.Div([html.Strong("Made by Kendrick Filbert"), html.Span(" • Supermarket Intelligence Dashboard • Dash 4.4.1")],className="footer")
],className="content")
app.layout=html.Div([sidebar,content])

def graph_card(title, graph_id, subtitle=None, width=6):
    return dbc.Col(dbc.Card(dbc.CardBody([html.Div([html.H5(title),html.Small(subtitle or "")],className="chart-head"),dcc.Loading(dcc.Graph(id=graph_id,config={"displaylogo":False,"responsive":True}))]),className="chart-card"),md=width)

@app.callback(Output("tab-content","children"),Input("tabs","value"))
def render_tab(tab):
    if tab=="overview":
        return html.Div([dbc.Row([graph_card("Tren Penjualan & Keuntungan","trend","Agregasi bulanan",8),graph_card("Kontribusi Penjualan per Kategori","category","Persentase dari total penjualan",4)],className="g-3"),dbc.Row([graph_card("Kinerja Kota","city","Penjualan dan margin keuntungan",6),graph_card("Seasonality Heatmap","heatmap","Penjualan bulanan per tahun",6)],className="g-3 mt-1")])
    if tab=="profitability":
        return html.Div([dbc.Row([graph_card("Penjualan vs Keuntungan","scatter","Ukuran bubble merepresentasikan kuantitas",7),graph_card("Profit Bridge per Subkategori","subprofit","Hijau menguntungkan, merah merugi",5)],className="g-3"),dbc.Row([graph_card("Dampak Diskon terhadap Margin","discount","Distribusi margin per tingkat diskon",6),graph_card("Transaksi dengan Kerugian Terbesar","loss-table","Prioritas investigasi",6)],className="g-3 mt-1")])
    if tab=="product":
        return html.Div([dbc.Row([graph_card("Top 15 Produk Berdasarkan Penjualan","top-products","Label menunjukkan margin",7),graph_card("Portofolio Produk","portfolio","Kuadran sales dan profit",5)],className="g-3"),dbc.Row([graph_card("Pareto Produk","pareto","Kontribusi kumulatif penjualan",7),graph_card("Komposisi Subkategori","treemap","Hierarki kategori dan subkategori",5)],className="g-3 mt-1")])
    return html.Div([dbc.Row([graph_card("Nilai Pelanggan per Segmen","segment","Penjualan, profit, dan pelanggan",6),graph_card("Preferensi Metode Pengiriman","shipmode","Frekuensi transaksi",6)],className="g-3"),dbc.Row([graph_card("Kecepatan Pengiriman","delivery","Rata-rata durasi per metode",5),graph_card("Top Pelanggan","customers-chart","Berdasarkan total penjualan",7)],className="g-3 mt-1")])

def filtered(year,wilayah,kota,kategori,segmen):
    d=df[df.tahun.between(year[0],year[1])].copy()
    for col,vals in [("wilayah",wilayah),("clean_kota",kota),("kategori",kategori),("segmen",segmen)]:
        if vals: d=d[d[col].isin(vals)]
    return d

@app.callback(
    Output("sales","children"),Output("sales-sub","children"),Output("profit","children"),Output("profit-sub","children"),Output("margin","children"),Output("margin-sub","children"),Output("orders","children"),Output("orders-sub","children"),Output("customers","children"),Output("customers-sub","children"),
    Input("year","value"),Input("wilayah","value"),Input("kota","value"),Input("kategori","value"),Input("segmen","value"))
def kpis(year,wilayah,kota,kategori,segmen):
    d=filtered(year,wilayah,kota,kategori,segmen)
    sales=d.penjualan.sum(); profit=d.keuntungan.sum(); margin=profit/sales if sales else 0
    orders=d.order_id.nunique(); customers=d.customer_id.nunique(); aov=sales/orders if orders else 0
    losses=(d.keuntungan<0).sum(); avg_ship=d.durasi_pengiriman.mean()
    return rupiah(sales),f"AOV {rupiah(aov)}",rupiah(profit),f"{losses:,} transaksi merugi",f"{margin:.1%}","Keuntungan ÷ penjualan",f"{orders:,}",f"{len(d):,} line items",f"{customers:,}",f"Rata-rata kirim {avg_ship:.1f} hari"

@app.callback(Output("kota","options"),Input("wilayah","value"))
def city_options(w):
    d=df if not w else df[df.wilayah.isin(w)]
    return [{"label":x,"value":x} for x in sorted(d.clean_kota.dropna().unique())]

@app.callback(Output("year","value"),Output("wilayah","value"),Output("kota","value"),Output("kategori","value"),Output("segmen","value"),Input("reset","n_clicks"),prevent_initial_call=True)
def reset(_): return [int(df.tahun.min()),int(df.tahun.max())],[],[],[],[]

@app.callback(Output("download","data"),Input("download-btn","n_clicks"),State("year","value"),State("wilayah","value"),State("kota","value"),State("kategori","value"),State("segmen","value"),prevent_initial_call=True)
def download(_,year,w,k,c,s):
    return dcc.send_data_frame(filtered(year,w,k,c,s).to_csv,"supermarket_filtered.csv",index=False)

@app.callback(Output("trend","figure"),Output("category","figure"),Output("city","figure"),Output("heatmap","figure"),Input("year","value"),Input("wilayah","value"),Input("kota","value"),Input("kategori","value"),Input("segmen","value"))
def overview(year,w,k,c,s):
    d=filtered(year,w,k,c,s)
    if d.empty:return (empty_fig(),)*4
    m=d.groupby("periode",as_index=False)[["penjualan","keuntungan"]].sum().sort_values("periode")
    f1=go.Figure(); f1.add_trace(go.Scatter(x=m.periode,y=m.penjualan,name="Penjualan",mode="lines",line=dict(color=COLORS["primary"],width=3),fill="tozeroy",fillcolor="rgba(37,99,235,.08)")); f1.add_trace(go.Scatter(x=m.periode,y=m.keuntungan,name="Keuntungan",mode="lines",line=dict(color=COLORS["secondary"],width=3)))
    f1.update_yaxes(tickprefix="Rp",tickformat="~s"); polish(f1)
    cat=d.groupby("kategori",as_index=False).penjualan.sum().sort_values("penjualan",ascending=False)
    f2=px.pie(cat,names="kategori",values="penjualan",hole=.58,color_discrete_sequence=[COLORS["primary"],COLORS["accent"],COLORS["purple"]]); f2.update_traces(textposition="inside",textinfo="percent+label",hovertemplate="%{label}<br>Penjualan: Rp%{value:,.0f}<extra></extra>");polish(f2)
    city=d.groupby("clean_kota",as_index=False).agg(penjualan=("penjualan","sum"),keuntungan=("keuntungan","sum"));city["margin"]=city.keuntungan/city.penjualan;city=city.sort_values("penjualan")
    f3=px.bar(city,x="penjualan",y="clean_kota",orientation="h",color="margin",color_continuous_scale="Blues",hover_data={"keuntungan":":,.0f","margin":":.1%"});f3.update_xaxes(tickprefix="Rp",tickformat="~s");polish(f3)
    hm=d.pivot_table(index="tahun",columns="bulan_num",values="penjualan",aggfunc="sum",fill_value=0).reindex(columns=range(1,13),fill_value=0);hm.columns=[MONTHS_ID[x] for x in hm.columns]
    f4=px.imshow(hm,aspect="auto",color_continuous_scale="Blues",labels=dict(x="Bulan",y="Tahun",color="Penjualan"));f4.update_traces(hovertemplate="%{y} %{x}<br>Rp%{z:,.0f}<extra></extra>");polish(f4)
    return f1,f2,f3,f4

@app.callback(Output("scatter","figure"),Output("subprofit","figure"),Output("discount","figure"),Output("loss-table","figure"),Input("year","value"),Input("wilayah","value"),Input("kota","value"),Input("kategori","value"),Input("segmen","value"))
def profitability(year,w,k,c,s):
    d=filtered(year,w,k,c,s)
    if d.empty:return (empty_fig(),)*4
    sample=d.sample(min(len(d),2500),random_state=42)
    f1=px.scatter(sample,x="penjualan",y="keuntungan",color="kategori",size="kuantitas",hover_name="nama_produk",hover_data=["clean_kota","diskon"],opacity=.65,color_discrete_sequence=[COLORS["primary"],COLORS["accent"],COLORS["purple"]]);f1.add_hline(y=0,line_dash="dash",line_color=COLORS["danger"]);f1.update_xaxes(tickprefix="Rp",tickformat="~s");f1.update_yaxes(tickprefix="Rp",tickformat="~s");polish(f1,430)
    sp=d.groupby("sub_kategori",as_index=False).keuntungan.sum().sort_values("keuntungan");sp["status"]=np.where(sp.keuntungan>=0,"Untung","Rugi")
    f2=px.bar(sp,x="keuntungan",y="sub_kategori",orientation="h",color="status",color_discrete_map={"Untung":COLORS["secondary"],"Rugi":COLORS["danger"]});f2.update_xaxes(tickprefix="Rp",tickformat="~s");polish(f2,430)
    dd=d.copy();dd["diskon_label"]=(dd.diskon*100).round().astype(int).astype(str)+"%";grp=dd.groupby("diskon_label",as_index=False).agg(margin=("margin","mean"),transaksi=("row_id","count"));grp["diskon_num"]=grp.diskon_label.str.rstrip("%").astype(int);grp=grp.sort_values("diskon_num")
    f3=px.bar(grp,x="diskon_label",y="margin",color="margin",color_continuous_scale="RdYlGn",hover_data=["transaksi"]);f3.update_yaxes(tickformat=".0%");polish(f3)
    loss=d.nsmallest(10,"keuntungan")[["nama_produk","clean_kota","penjualan","diskon","keuntungan"]]
    f4=go.Figure(data=[go.Table(header=dict(values=["Produk","Kota","Penjualan","Diskon","Kerugian"],fill_color="#0F172A",font=dict(color="white"),align="left"),cells=dict(values=[loss.nama_produk,loss.clean_kota,[rupiah(x) for x in loss.penjualan],[f"{x:.0%}" for x in loss.diskon],[rupiah(x) for x in loss.keuntungan]],fill_color="#F8FAFC",align="left",height=28))]);polish(f4)
    return f1,f2,f3,f4

@app.callback(Output("top-products","figure"),Output("portfolio","figure"),Output("pareto","figure"),Output("treemap","figure"),Input("year","value"),Input("wilayah","value"),Input("kota","value"),Input("kategori","value"),Input("segmen","value"))
def product(year,w,k,c,s):
    d=filtered(year,w,k,c,s)
    if d.empty:return (empty_fig(),)*4
    p=d.groupby("nama_produk",as_index=False).agg(penjualan=("penjualan","sum"),keuntungan=("keuntungan","sum"),kuantitas=("kuantitas","sum"));p["margin"]=p.keuntungan/p.penjualan
    top=p.nlargest(15,"penjualan").sort_values("penjualan");f1=px.bar(top,x="penjualan",y="nama_produk",orientation="h",color="margin",color_continuous_scale="RdYlGn",text=top.margin.map(lambda x:f"{x:.1%}"));f1.update_xaxes(tickprefix="Rp",tickformat="~s");f1.update_traces(textposition="outside");polish(f1,500)
    med_s=p.penjualan.median();med_p=p.keuntungan.median();p["kuadran"]=np.select([(p.penjualan>=med_s)&(p.keuntungan>=med_p),(p.penjualan>=med_s)&(p.keuntungan<med_p),(p.penjualan<med_s)&(p.keuntungan>=med_p)],["Star","Volume Driver","Hidden Gem"],default="Underperformer")
    f2=px.scatter(p,x="penjualan",y="keuntungan",color="kuadran",size="kuantitas",hover_name="nama_produk",log_x=True,color_discrete_map={"Star":COLORS["secondary"],"Volume Driver":COLORS["accent"],"Hidden Gem":COLORS["purple"],"Underperformer":COLORS["muted"]});f2.add_hline(y=med_p,line_dash="dot");f2.add_vline(x=med_s,line_dash="dot");f2.update_xaxes(tickprefix="Rp",tickformat="~s");f2.update_yaxes(tickprefix="Rp",tickformat="~s");polish(f2,500)
    pp=p.sort_values("penjualan",ascending=False).head(30).copy();pp["kumulatif"]=pp.penjualan.cumsum()/p.penjualan.sum()
    f3=go.Figure();f3.add_bar(x=pp.nama_produk,y=pp.penjualan,name="Penjualan",marker_color=COLORS["primary"]);f3.add_scatter(x=pp.nama_produk,y=pp.kumulatif,name="Kumulatif",yaxis="y2",line=dict(color=COLORS["accent"],width=3));f3.update_layout(yaxis2=dict(overlaying="y",side="right",tickformat=".0%",range=[0,1.05]));f3.update_xaxes(showticklabels=False);f3.update_yaxes(tickprefix="Rp",tickformat="~s");polish(f3)
    tr=d.groupby(["kategori","sub_kategori"],as_index=False).penjualan.sum();f4=px.treemap(tr,path=["kategori","sub_kategori"],values="penjualan",color="penjualan",color_continuous_scale="Blues");polish(f4)
    return f1,f2,f3,f4

@app.callback(Output("segment","figure"),Output("shipmode","figure"),Output("delivery","figure"),Output("customers-chart","figure"),Input("year","value"),Input("wilayah","value"),Input("kota","value"),Input("kategori","value"),Input("segmen","value"))
def customer(year,w,k,c,s):
    d=filtered(year,w,k,c,s)
    if d.empty:return (empty_fig(),)*4
    sg=d.groupby("segmen",as_index=False).agg(penjualan=("penjualan","sum"),keuntungan=("keuntungan","sum"),pelanggan=("customer_id","nunique"));f1=px.bar(sg,x="segmen",y=["penjualan","keuntungan"],barmode="group",color_discrete_sequence=[COLORS["primary"],COLORS["secondary"]],hover_data=["pelanggan"]);f1.update_yaxes(tickprefix="Rp",tickformat="~s");polish(f1)
    sh=d.metode_pengiriman.value_counts().rename_axis("metode_pengiriman").reset_index(name="transaksi").sort_values("transaksi");f2=px.bar(sh,x="transaksi",y="metode_pengiriman",orientation="h",color="transaksi",color_continuous_scale="Blues",text="transaksi");polish(f2)
    dl=d.groupby("metode_pengiriman",as_index=False).agg(hari=("durasi_pengiriman","mean"),orders=("order_id","nunique")).sort_values("hari");f3=px.bar(dl,x="hari",y="metode_pengiriman",orientation="h",color="hari",color_continuous_scale="Teal",text=dl.hari.map(lambda x:f"{x:.1f} hari"),hover_data=["orders"]);polish(f3)
    cs=d.groupby(["customer_id","nama_pelanggan"],as_index=False).agg(penjualan=("penjualan","sum"),keuntungan=("keuntungan","sum"),orders=("order_id","nunique")).nlargest(15,"penjualan").sort_values("penjualan");f4=px.bar(cs,x="penjualan",y="nama_pelanggan",orientation="h",color="keuntungan",color_continuous_scale="RdYlGn",hover_data=["orders"]);f4.update_xaxes(tickprefix="Rp",tickformat="~s");polish(f4,430)
    return f1,f2,f3,f4

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050)
