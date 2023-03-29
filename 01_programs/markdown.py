################################################################################
#region IMPORTS
################################################################################
from config import *
import csv, datetime
import plotly_express as px
from collections import defaultdict
################################################################################
#endregion
################################################################################



################################################################################
#region CONSTANTS
################################################################################
FRD_TITLES = {
    "FRD01": "Boston",
    "FRD02": "New York",
    "FRD03": "Philadelphia",
    "FRD04": "Cleveland",
    "FRD05": "Richmond",
    "FRD06": "Atlanta",
    "FRD07": "Chicago",
    "FRD08": "St. Louis",
    "FRD09": "Minneapolis",
    "FRD10": "Kansas City",
    "FRD11": "Dallas",
    "FRD12": "San Francisco",
    "FRD99": "Unknown"
}
CHART_ATTRS = {
    "Total U.S.": {"color": "#000000", "dash": "dot"},
    "Boston": {"color": "#D81B60", "dash": "solid"},
    "New York": {"color": "#1E88E5", "dash": "solid"},
    "Philadelphia": {"color": "#5e5726", "dash": "solid"},
    "Cleveland": {"color": "#004D40", "dash": "solid"},
    "Richmond": {"color": "#d8fcad", "dash": "solid"},
    "Atlanta": {"color": "#2f33b1", "dash": "solid"},
    "Chicago": {"color": "#9a0dfb", "dash": "solid"},
    "St. Louis": {"color": "#e4b2c7", "dash": "solid"},
    "Minneapolis": {"color": "#71efc9", "dash": "solid"},
    "Kansas City": {"color": "#e7cea5", "dash": "solid"},
    "Dallas": {"color": "#f15b23", "dash": "solid"},
    "San Francisco": {"color": "#f09406", "dash": "solid"},
}
CSV_DATA_TYPES = {
    "area_code": str,
    "year": str,
    "area_title": str,
    "annual_avg_emplvl": int,
    "avg_annual_pay": int,
}
BAR_CHART_ANNOTATION = dict(
    showarrow=False,
    font_size=9,
    xref='paper',
    yref='paper',
    x=-0.15,
    y=-0.10,
    text="Source: Author's (github@TrentLThompson) calculations based on data from the U.S. Bureau of Labor Statistics.",
)
LINE_CHART_ANNOTATION = dict(
    showarrow=False,
    font_size=9,
    xref='paper',
    yref='paper',
    x=0.0,
    y=-0.10,
    text="Source: Author's (github@TrentLThompson) calculations based on data from the U.S. Bureau of Labor Statistics.",
)
################################################################################
#endregion
################################################################################



################################################################################
#region FUNCTIONS
################################################################################
#region main FUNCTION -------------------------------------------------------- #
def main() -> None:

    # Read in the data.
    longitudinal_data = read_data()

    # Get the most recent year.
    latest_year = longitudinal_data[-1]["year"]

    # Get the data belonging to the most recent year-quarter.
    latest_data = [d for d in longitudinal_data if d["year"] == latest_year]
    
    # Generate pie chart image.
    generate_pie_chart(latest_data, latest_year)
    
    # Generate bar chart images.
    for field in ("oty_annual_avg_emplvl_pct", "oty_avg_annual_pay_pct"):
        generate_bar_chart(latest_data, latest_year, field)
    
    # Generate line chart images.
    for field in ("annual_avg_emplvl", "avg_annual_pay"):
        generate_line_chart(longitudinal_data, latest_year, field)

    # Write the markdown (.MD) file.
    write_markdown(longitudinal_data, latest_year)
#endregion ------------------------------------------------------------------- #
#region read_data FUNCTION --------------------------------------------------- #
def read_data() -> list[dict]:
    csv_data = {}
    with open(f"{DIR_OUTPUT}/02_csv/annual_data.csv", "r") as input:
        csv_reader = csv.DictReader(input)
        for row in csv_reader:
            if row["area_code"] != "FRD99":
                year = row["year"]
                area = row["area_code"]
                if year not in csv_data:
                    csv_data[year] = {}
                if area not in csv_data[year]:
                    csv_data[year][area] = defaultdict(int)
                for field in ("annual_avg_emplvl", "avg_annual_pay"):
                    csv_data[year][area][field] += int(row[field])
    
    longitudinal_data = []
    for year, area_codes in csv_data.items():
        prior_year = f"{int(year)-1}"
        prior_decade = f"{int(year)-10}"
        for area_code, fields in area_codes.items():
            area_title = "Total U.S." if area_code == "USDPV" else FRD_TITLES[area_code]
            csv_row = {
                "year": year,
                "area_title": area_title,
            }
            for field, value in fields.items():
                csv_row[field] = value
                # Get the over-the-year and over-the-decade changes.
                for prior_period in (prior_year, prior_decade):
                    t = "y" if prior_period == prior_year else "d"
                    if prior_period in csv_data.keys():
                        prior_values = csv_data[prior_period][area_code]
                        for field, prior_value in prior_values.items():
                            value = fields[field]
                            if value is not None and prior_value is not None:
                                delta = value - prior_value
                            else:
                                delta = None
                            csv_row[f"ot{t}_{field}_chg"] = delta
                            if delta is not None and prior_value > 0:
                                csv_row[f"ot{t}_{field}_pct"] = round(delta/prior_value*100, 1)
                            else:
                                csv_row[f"ot{t}_{field}_pct"] = None
                    else:
                        for field, value in fields.items():
                            csv_row[f"ot{t}_{field}_chg"] = None
                            csv_row[f"ot{t}_{field}_pct"] = None
            longitudinal_data.append(csv_row)
    
    longitudinal_data = sorted(longitudinal_data, key=lambda d: d["year"])

    return(longitudinal_data)
#endregion ------------------------------------------------------------------- #
#region generate_pie_chart FUNCTION ------------------------------------------ #
def generate_pie_chart(data: list[dict], ref_year: str) -> None:
    
    chart_data = [d for d in data if d["area_title"] != "Total U.S."]
    
    fig = px.pie(
        data_frame=chart_data,
        names="area_title", 
        values="annual_avg_emplvl", 
        color="area_title",
        color_discrete_map={k: v["color"] for k, v in CHART_ATTRS.items()},
        category_orders={"area_title": [v for v in FRD_TITLES.values()]},
        title=f"Distribution of U.S. annual average employment, by Federal Reserve district, {ref_year}",
        hole=0.3
    )

    fig.update_traces(texttemplate="%{percent:.1%}")

    fig.update_layout(
        font_color="black",
        legend_title=None,
        legend_y=0.55,
        margin_t=40,
        margin_b=50,
        margin_r=10,
        title_font_size=15,
        title_x=0.02,
        title_y=0.98,
    )

    fig.add_annotation(BAR_CHART_ANNOTATION)

    fig.write_image(f"{DIR_OUTPUT}/03_charts/pie_annual_avg_emplvl.png", scale=6)
#endregion ------------------------------------------------------------------- #
#region generate_bar_chart FUNCTION ------------------------------------------ #
def generate_bar_chart(data: list[dict], ref_year: str, field: str) -> None:

    chart_data = []
    for dict in data:
        if dict["area_title"] == "Total U.S.":
            us_avg = dict[field]
            reverse_indicator = False if dict[field] > 0 else True
        else:
            chart_data.append(dict)

    chart_data = sorted(
        chart_data, 
        key=lambda d: d[field], 
        reverse=reverse_indicator
    )
    
    x_max = round(max([dict[field] for dict in chart_data])) + 1
    x_max = 0 if x_max < 0 else x_max
    
    x_min = round(min([dict[field] for dict in chart_data])) - 1
    x_min = 0 if x_min > 0 else x_min
    
    prior_year = str(int(ref_year) - 1)

    field_title = "annual average employment" if field == "oty_annual_avg_emplvl_pct" else "average annual pay"
    title = f"Percent change in {field_title}, by Federal Reserve district, {prior_year}-{ref_year}"

    fig = px.bar(
        data_frame=chart_data, 
        x=field,
        y="area_title",
        color="area_title",
        color_discrete_map={k: v["color"] for k, v in CHART_ATTRS.items()},
        orientation="h", 
        text_auto=True,
        title=title
    )

    fig.add_vline(
        x=us_avg, 
        line_width=2,
        line_dash="dot", 
        line_color="black",
        annotation_text=f" Total U.S. = {us_avg}%",
        annotation_position="bottom right",
        annotation_font_color="black",
    )

    fig.update_layout(
        font_color="black",
        title_font_size=15,
        margin_t=40,
        margin_b=50,
        margin_r=10,
        xaxis_title=None,
        yaxis_title=None,
        yaxis_categoryorder="total ascending",
        xaxis_ticksuffix = "%",
        title_x=0.02,
        title_y=0.98,
        showlegend=False,
        plot_bgcolor="white",
    )

    fig.update_traces(
        marker_line_color="black", 
        marker_line_width=1
    )

    fig.update_xaxes(
        range=[x_min, x_max],
        zeroline=True, 
        zerolinewidth=2, 
        zerolinecolor="black", 
        showline=True, 
        linewidth=2, 
        linecolor="black", 
        mirror=True, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor="black"
    )
    
    fig.update_yaxes(
        showline=True, 
        linewidth=2, 
        linecolor="black", 
        mirror=True
    )

    fig.add_annotation(BAR_CHART_ANNOTATION)

    fig.write_image(f"{DIR_OUTPUT}/03_charts/bar_{field}.png", scale=6)
#endregion ------------------------------------------------------------------- #
#region generate_line_chart FUNCTION ----------------------------------------- #
def generate_line_chart(data: list[dict], ref_year: str, field: str) -> None:

    index_year = str(int(ref_year) - 10) # Index year = same year as reference year minus ten years.

    index_year_data = defaultdict(int)
    for dict in data:
        if dict["year"] == index_year:
            index_year_data[dict["area_title"]] = dict[field]
    
    chart_data = []
    for dict in data:
        year = dict["year"]
        if int(year) >= int(index_year):
            index = index_year_data[dict["area_title"]]
            chart_data.append({
                "Year": year,
                "Area": dict["area_title"],
                "Index": round(dict[field]/index*100, 1)
            })
    
    chart_xaxis_dtick = 2
    field_title = "annual average employment" if field == "annual_avg_emplvl" else "average annual pay"
    title = f"Indexed {field_title}, by Federal Reserve district, {index_year}-{ref_year}<br>"
    title += f"<sup>Index: {index_year} = 100</sup>"

    fig = px.line(
        data_frame=chart_data,
        x="Year",
        y="Index",
        color="Area",
        color_discrete_map={k: v["color"] for k, v in CHART_ATTRS.items()},
        line_dash="Area",
        line_dash_map={k: v["dash"] for k, v in CHART_ATTRS.items()},
        title=title,
    )

    fig.add_hline(
        y=100, 
        line_width=2,
        line_color="black",
        opacity=1
    )

    fig.update_layout(
        font_color="black",
        plot_bgcolor="white",
        margin_t=55,
        margin_b=50,
        margin_l=10,
        margin_r=100,
        xaxis_title=None,
        xaxis_dtick=chart_xaxis_dtick,
        xaxis_tickfont_size=9,
        yaxis_title=None,
        title_font_size=15,
        title_x=0.02,
        title_y=0.95,
        legend_title=None,
        legend_y=0.85,
        legend_xanchor="left",
        legend_x=1.1,  
    )

    fig.update_yaxes(
        showline=True, 
        linewidth=2, 
        linecolor="black",
        mirror=True, 
        showgrid=True, 
        gridwidth=1, 
        gridcolor="grey",
        side="right",
    )

    fig.update_xaxes(
        showline=True,
        linewidth=2,
        linecolor="black",
        mirror=True
    )

    fig.add_annotation(LINE_CHART_ANNOTATION)

    fig.write_image(f"{DIR_OUTPUT}/03_charts/line_{field}.png", scale=6)
#endregion ------------------------------------------------------------------- #
#region write_markdown FUNCTION ---------------------------------------------- #
def write_markdown(data: list[dict], ref_year: str) -> None:
    
    prior_year = str(int(ref_year) - 1)
    prior_decade = str(int(ref_year) - 10)

    latest_data = [d for d in data if d["year"] == ref_year]
    latest_district_data = [d for d in latest_data if d["area_title"] != "Total U.S."]
    latest_us_data = [d for d in latest_data if d["area_title"] == "Total U.S."][0]

    sorted_data = sorted(latest_district_data, key=lambda d: d["annual_avg_emplvl"], reverse=True)
    largest_district = sorted_data[0]["area_title"]
    largest_district_shr = round(sorted_data[0]["annual_avg_emplvl"]/latest_us_data["annual_avg_emplvl"]*100, 1)
    smallest_district = sorted_data[-1]["area_title"]
    smallest_district_shr = round(sorted_data[-1]["annual_avg_emplvl"]/latest_us_data["annual_avg_emplvl"]*100, 1)
    p1 = f"According to data from the Bureau of Labor Statistics' Quarterly Census of Employment and Wages ([QCEW](https://www.bls.gov/cew/)), the {largest_district} Federal Reserve district had the largest share of U.S. annual average employment ({largest_district_shr}%) in {ref_year}, while the {smallest_district} Federal Reserve district had the smallest share ({smallest_district_shr}%).\n\n"

    markdown = ""
    markdown += f"Last updated: {datetime.date.today().strftime('%B %d, %Y')}\n\n"
    markdown += f"# Federal Reserve District Employment & Wages\n\n"
    markdown += f"[Just give me the data!](https://github.com/TrentLThompson/federal-reserve-qcew/tree/main/03_outputs/02_csv)\n\n"
    markdown += p1
    markdown += f"![](03_outputs/03_charts/pie_annual_avg_emplvl.png)\n\n"
    
    for time_frame in ("oty", "otd"):
        for field in ("annual_avg_emplvl", "avg_annual_pay"):
            sorted_data = sorted(latest_district_data, key=lambda d: d[f"{time_frame}_{field}_pct"], reverse=True)
            focus = "increase" if sum([d[f"{time_frame}_{field}_chg"] for d in latest_district_data]) > 0 else "decrease"
            n_focus = "all" if all(d[f"{time_frame}_{field}_chg"] > 0 for d in sorted_data) else sum(1 for d in sorted_data if d[f"{time_frame}_{field}_chg"] > 0)
            top_district_title = sorted_data[0]["area_title"]
            top_district_pct = sorted_data[0][f"{time_frame}_{field}_pct"]
            
            field_title = "annual average employment" if field == "annual_avg_emplvl" else "average annual pay"
            prior_year = prior_year if time_frame == "oty" else prior_decade
            timespan = "year" if time_frame == "oty" else "decade"
            
            markdown += f"From {prior_year} to {ref_year}, {field_title} {focus}d in {n_focus} of the twelve Federal Reserve districts. The {top_district_title} Federal Reserve district had the largest over-the-{timespan} percentage {focus} in {field_title} ({top_district_pct} percent).\n\n"
            
            chart_ref = f"line_{field}" if time_frame == "otd" else f"bar_oty_{field}_pct"
            markdown += f"![](03_outputs/03_charts/{chart_ref}.png)\n\n"
    
    markdown += f"<br>Last updated: {datetime.date.today().strftime('%B %d, %Y')}"

    with open(f"{DIR_ROOT}/README.md", "w") as output:
        output.write(markdown)
#endregion ------------------------------------------------------------------- #
################################################################################
#endregion
################################################################################



if __name__ == "__main__":
    main()


