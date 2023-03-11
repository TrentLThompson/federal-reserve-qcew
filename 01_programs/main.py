################################################################################
#region IMPORTS
################################################################################
from config import *
from collections import defaultdict
import csv, datetime, json, os, requests
################################################################################
#endregion
################################################################################



################################################################################
#region FUNCTIONS
################################################################################
#region main FUNCTION -------------------------------------------------------- #
def main() -> None:
    # Generate quarterly JSON data if it does not yet exist.
    if not os.path.exists(f"{DIR_OUTPUT}/01_json/quarterly_data.json"):
        generate_qtrly_json()
    
    # Update quarterly JSON data with new data from BLS's QCEW API.
    update_qtrly_json()

    # (Re)-Generate the annual JSON data.
    generate_annual_json()
    
    # Generate quarterly and annual CSV data.
    for i in ["quarterly", "annual"]:
        generate_csv(i)
#endregion ------------------------------------------------------------------- #
#region generate_qtrly_database FUNCTION ------------------------------------- #
def generate_qtrly_json() -> None:
    '''
    Creates a quarterly JSON database using historical source files downloaded
    from the Bureau of Labor Statistics' Quarterly Census of Employment and 
    Wages (QCEW) to the source directory (`DIR_INPUT`).
    '''
    # Initialize an empty dictionary, then update the dictionary with data from
    # the source QCEW files.
    json_data = {}
    for file in os.listdir(DIR_INPUT):
        with open(f"{DIR_INPUT}/{file}", "r") as input:
            csv_reader = csv.DictReader(input)
            json_data.update(aggregate_data(csv_reader))
    
    # Write the dictionary out to a JSON file.
    with open(f"{DIR_OUTPUT}/01_json/quarterly_data.json", "w") as output:
        json.dump(json_data, output, indent=4)
#endregion ------------------------------------------------------------------- #
#region update_qtrly_database FUNCTION --------------------------------------- #
def update_qtrly_json() -> None:
    '''
    Updates the quarterly JSON database with any new data from the Bureau of 
    Labor Statistics' Quarterly Census of Employment and Wages (QCEW) API.
    '''
    # Read in the existing database.
    with open(f"{DIR_OUTPUT}/01_json/quarterly_data.json", "r") as input:
        json_data = json.load(input)

    # Update the database for all quarters this year and last year, if these
    # data are available. QCEW data are revised four times after they are 
    # first published, so it is necessary each quarter to update the 
    # database with the revised, back-quarter data.
    current_year = datetime.date.today().year
    for year in [current_year, current_year - 1]:
        for qtr in ["1", "2", "3", "4"]:
            url = f"http://www.bls.gov/cew/data/api/{year}/{qtr}/industry/10.csv"
            response = requests.get(url)
            if response.status_code == 200:
                csv_reader = csv.DictReader(
                    response.content.decode().splitlines()
                )
                json_data.update(aggregate_data(csv_reader))

    # Write the data out to a JSON file.
    with open(f"{DIR_OUTPUT}/01_json/quarterly_data.json", "w") as output:
        json.dump(json_data, output, indent=4)
#endregion ------------------------------------------------------------------- #
#region generate_annual_database FUNCTION ------------------------------------ #
def generate_annual_json() -> None:
    '''
    Creates an annual JSON database from the quarterly JSON database.
    '''
    # Read in the quarterly database.
    with open(f"{DIR_OUTPUT}/01_json/quarterly_data.json", "r") as input:
        json_data = json.load(input)

    # Initialize annual data.
    annual_data = {}
    periods = list(json_data.keys())
    years = set([period[0:4] for period in periods])
    for year in sorted(list(years)):
        if all([f"{year}_{qtr}" in periods for qtr in ["1", "2", "3", "4"]]):
            period = f"{year}_A"
            annual_data[period] = {}
            for area in FRD_TITLES.keys():
                annual_data[period][area] = defaultdict(int)
            annual_data[period]["USDPV"] = defaultdict(int)
    
    # Aggregate annual data.
    for period, areas in json_data.items():
        annual_period = f"{period[0:4]}_A"
        if annual_period in annual_data.keys():
            for area, fields in areas.items():
                dict = annual_data[annual_period][area]
                dict["annual_avg_estabs_count"] += fields["qtrly_estabs_count"]
                for m in ("1", "2", "3"):
                    dict["annual_avg_emplvl"] += fields[f"month{m}_emplvl"]
                dict["total_annual_wages"] += fields["total_qtrly_wages"]

    # Finalize annual averages.
    for areas in annual_data.values():
        for fields in areas.values():
            for field in ("annual_avg_estabs_count", "annual_avg_emplvl"):
                denominator = 4 if field == "annual_avg_estabs_count" else 12
                fields[field] = round(fields[field]/denominator)
            emp = fields["annual_avg_emplvl"]
            if emp > 0:
                pay = round(fields["total_annual_wages"]/emp)
                fields["annual_avg_wkly_wage"] = round(pay/52)
                fields["avg_annual_pay"] = pay
            else:
                fields["annual_avg_wkly_wage"] = None
                fields["avg_annual_pay"] = None
    
    # Write the data out to a JSON file.
    with open(f"{DIR_OUTPUT}/01_json/annual_data.json", "w") as output:
        json.dump(annual_data, output, indent=4)
#endregion ------------------------------------------------------------------- #
#region aggregate_data FUNCTION ---------------------------------------------- #
def aggregate_data(csv_reader: csv.DictReader) -> dict:
    '''
    Aggregates county-level QCEW data to the Federal Reserve district level.
    '''
    # Read in the QCEW data.
    qcew_slice = [dict for dict in csv_reader]
    
    # Fix field titling discrepancy between API-based and non-API-based QCEW 
    # data slices.
    for dict in qcew_slice:
        if "qtrly_estabs_count" not in dict.keys():
            dict["qtrly_estabs_count"] = dict["qtrly_estabs"]
            del dict["qtrly_estabs"]
    
    # Get the distribution of the data across Federal Reserve districts for each 
    # state.
    district_shares = get_district_shares(qcew_slice)

    # Aggregate the county-level total data to the Federal Reserve district 
    # level. Also aggregate the state-level total data to the U.S. Total.
    data = {}
    for row in qcew_slice:
        period = f"{row['year']}_{row['qtr']}"
        if period not in data:
            data[period] = {}
            for area in FRD_TITLES.keys():
                data[period][area] = defaultdict(int)
            data[period]["USDPV"] = defaultdict(int)
        if row["agglvl_code"] == "70" and row["disclosure_code"] == "":
            cnty_fips = row["area_fips"]
            if cnty_fips[2:4] != "99":
                area = CNTY_FRD_CROSSWALK[cnty_fips]
                for field in QTRLY_FIELDS:
                    data[period][area][field] += int(row[field])
            else:
                state_fips = cnty_fips[0:2]
                for area, fields in district_shares[period][state_fips].items():
                    for field, weight in fields.items():
                        data[period][area][field] += round(int(row[field])*weight)
        elif row["agglvl_code"] == "50":
            for field in QTRLY_FIELDS:
                data[period]["USDPV"][field] += int(row[field])
    
    # Get FRD99 totals, which are the differences between the U.S. Totals and 
    # the sum across the twelve Federal Reserve Districts.
    for period, areas in data.items():
        us_totals = {field: areas["USDPV"][field] for field in QTRLY_FIELDS}
        for field, us_total in us_totals.items():
            area_total = sum(areas[area][field] for area in FRD_TITLES.keys())
            data[period]["FRD99"][field] = us_total - area_total
    
    # Get average weekly wages.
    for period, areas in data.items():
        for area, fields in areas.items():
            tw = fields["total_qtrly_wages"]
            tot_emp = sum(fields[f"month{m}_emplvl"] for m in ("1", "2", "3"))
            ame = round(tot_emp/3)
            if ame > 0:
                data[period][area]["avg_wkly_wage"] = round(tw/ame/13)
            else:
                data[period][area]["avg_wkly_wage"] = None
                
    # Return the data dictionary.
    return(data)
#endregion ------------------------------------------------------------------- #
#region get_district_shares FUNCTION ----------------------------------------- #
def get_district_shares(qcew_slice: list[dict]) -> dict:
    '''
    Gets the distribution of the data across Federal Reserve districts for
    each state. These distributions are needed later in order to aggregate 99x 
    county data for states belonging to more than one Federal Reserve district.
    '''
    # Get the set of Federal Reserve districts each state belongs to.
    districts_by_state = defaultdict(set)
    for cnty, district in CNTY_FRD_CROSSWALK.items():
        districts_by_state[cnty[0:2]].add(district)
    
    # For all non-99x counties, aggregate data to the Federal Reserve district 
    # level. All non-99x counties are associated with a single district.
    district_shares = {}
    for row in qcew_slice:
        period = f"{row['year']}_{row['qtr']}"
        if period not in district_shares:
            district_shares[period] = {}
            for state, districts in districts_by_state.items():
                district_shares[period][state] = {}
                for district in districts:
                    district_shares[period][state][district] = defaultdict(int)
        if row["agglvl_code"] == "70":
            cnty_fips = row["area_fips"]
            if cnty_fips[2:4] != "99":
                state = cnty_fips[0:2]
                district = CNTY_FRD_CROSSWALK[cnty_fips]
                for field in QTRLY_FIELDS:
                    district_shares[period][state][district][field] += int(row[field])
    
    # For each state, get the distribution of non-99x data across Federal 
    # Reserve districts.
    for period, states in district_shares.items():
        for state, districts in states.items():
            state_totals = defaultdict(int)
            for district, fields in districts.items():
                for field, value in fields.items():
                    state_totals[field] += value
            
            dict = district_shares[period][state]
            for field, state_total in state_totals.items():
                for district in districts.keys():
                    if state_total > 0:
                        district_total = dict[district][field]
                        dict[district][field] = district_total/state_total
                    else:
                        dict[district][field] = None
    
    # Return the district shares dictionary.
    return(district_shares)
#endregion ------------------------------------------------------------------- #
#region generate_csv FUNCTION ------------------------------------------------ #
def generate_csv(i: str) -> None:
    '''
    Generates a CSV file containing all of the establishment, employment, and
    wage data for Federal Reserve districts over-time. `i` should either be: 
    "quarterly" or "annual".
    '''
    with open(f"{DIR_OUTPUT}/01_json/{i}_data.json", "r") as input:
        json_data = json.load(input)

    # Construct the CSV data as a list of dictionaries. Don't include records 
    # with zero data on the file.
    csv_data = []
    for period, area_codes in json_data.items():
        year, qtr = tuple(period.split("_"))
        for area_code, fields in area_codes.items():
            zeroed = True
            for field, value in fields.items():
                if isinstance(value, int) and value > 0:
                    zeroed = False
            if not zeroed:
                csv_row = {
                    "year": year,
                    "qtr": qtr,
                    "area_code": area_code,
                    "area_title": "Total U.S." if area_code == "USDPV" else f"{FRD_TITLES[area_code]} -- Federal Reserve District",
                }
                for field, value in fields.items():
                    csv_row[field] = value
                csv_data.append(csv_row)
    
    # Sort the CSV data by year, quarter, and area.
    sort_cols = ["year", "qtr", "area_code"]
    csv_data = sorted(csv_data, key=lambda d: [d[col] for col in sort_cols])

    # Write out the CSV data.
    with open(f"{DIR_OUTPUT}/02_csv/{i}_data.csv", "w") as output:
        csv_writer = csv.DictWriter(
            output,
            fieldnames=csv_data[0].keys(),
            lineterminator="\n"
        )
        csv_writer.writeheader()
        csv_writer.writerows(csv_data)
#endregion ------------------------------------------------------------------- #
################################################################################
#endregion
################################################################################



if __name__ == "__main__":
    main()


