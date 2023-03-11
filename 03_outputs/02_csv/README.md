# Technical Information

## Handling of Unknown or Undefined County Data

County-level data from the Quarterly Census of Employment and Wages (QCEW) are aggregated to the Federal Reserve District level based on the county-to-federal-reserve-district crosswalk provided by [Tousey (2019)](https://doi.org/10.18651/TB/TB1901). However, because the QCEW also designates special counties to hold data belonging to unknown or undefined counties, these data must be aggregated in a special manner.

To aggregate unknown or undefined county data (i.e. QCEW records with area code XX99X) to the Federal Reserve district level, the data for these counties are split proportionally among the Federal Reserve districts these data could possibly belong to. For a XX99X county in a state that belongs to just one Federal Reserve district (e.g. California) the calculation is simple: 100% of the data belong to that district. However, for a XX99X county in a state that straddles two or more districts, the data must be distributed proportionally across the districts.

For example, the state of New Mexico straddles two Federal Reserve districts: Kansas City and Dallas. In December 2021, 70.52 percent of the state's employment in known/defined counties belonged to the Kansas City district, and the remaining 29.48 percent belonged to the Dallas district. So, when splitting up the 24,503 in December employment for the Unknown or Undefined, New Mexico county (QCEW area code 35999) across the two districts, 70.52 percent (17,280) goes to the Kansas City district and the remaining 29.48 percent (7,223) goes to the Dallas district.

## Handling of Suppressed County Data

Sometimes it is not possible to completely aggregate QCEW county-level data to the Federal Reserve district-level due to suppressions in the QCEW data (for more information, see: https://www.bls.gov/cew/overview.htm#confidentiality). In these instances there is a difference between the U.S. Total and the sum total across the twelve Federal Reserve districts, such that the twelve-district sum is less than the U.S. total. To capture these differences, a thirteenth district—FRD99, Unknown -- Federal Reserve District—is used.

In many reference periods, this thirteenth district is not needed because there are no suppressions, so there is no FRD99 record. For reference periods in which this district is needed, the share of data captured by this district is usually negligible, but nevertheless reported in an FRD99 record.
<br>

# CSV File Layout
Col. | Field | Description | Type
---- | ----- | ----------- | ----
1 | `year` | Reference year | String
2 | `qtr` | Reference quarter (always "A" for annual data) | String
3 | `area_code` | 5-digit area code (see [area code taxonomy table](#area-code-taxonomy) below for more information) | String
4 | `area_title` | Area title (see [area code taxonomy table](#area-code-taxonomy) below for more information) | String
**Col.** | **Quarterly Field** | **Description** | **Type**
5 | `qtrly_estabs_count` | Count of establishments for a given quarter | Number
6 | `month1_emplvl` | Employment level for the first month of a given quarter (i.e. January, April, July, or October) | Number
7 | `month2_emplvl` | Employment level for the second month of a given quarter (i.e. February, May, August, or November) | Number
8 | `month3_emplvl` | Employment level for the third month of a given quarter (i.e. March, June, September, or December) | Number
9 | `total_qtrly_wages` | Total wages for a given quarter | Number
10 | `avg_wkly_wage` | Average weekly wage for a given quarter | Number
**Col.** | **Annual Field** | **Description** | **Type**
5 | `annual_avg_estabs_count` | Annual average of quarterly establishment counts for a given year | Number
6 | `annual_avg_emplvl` | Annual average of monthly employment levels for a given year | Number
7 | `total_annual_wages` | Sum of the four quarterly total wage levels for a given year | Number
8 | `annual_avg_wkly_wage` | Average weekly wage based on the 12-monthly employment levels and total annual wage levels | Number
9 | `avg_annual_pay` | Average annual pay based on employment and wage levels for a given year | Number
<br>

# Area Code Taxonomy
Area Code | Area Title | Description   
--------- | ---------- | -----------
`FRD01` | Boston -- Federal Reserve District | Covers the states of Maine, Massachusetts, New Hampshire, Rhode Island, and Vermont; and all but Fairfield County in Connecticut.
`FRD02` | New York -- Federal Reserve District | Covers the state of New York; Fairfield County in Connecticut; and 12 counties in northern New Jersey, and serves the Commonwealth of Puerto Rico and the U.S. Virgin Islands.
`FRD03` | Philadelphia -- Federal Reserve District | Covers the state of Delaware; nine counties in southern New Jersey; and 48 counties in the eastern two-thirds of Pennsylvania.
`FRD04` | Cleveland -- Federal Reserve District | Covers the state of Ohio; 56 counties in eastern Kentucky; 19 counties in western Pennsylvania; and 6 counties in northern West Virginia .
`FRD05` | Richmond -- Federal Reserve District | Covers the states of Maryland, Virginia, North Carolina, and South Carolina; 49 counties constituting most of West Virginia; and the District of Columbia.
`FRD06` | Atlanta -- Federal Reserve District | Covers the states of Alabama, Florida, and Georgia; 74 counties in the eastern two-thirds of Tennessee; 38 parishes of southern Louisiana; and 43 counties of southern Mississippi.
`FRD07` | Chicago -- Federal Reserve District | Covers the state of Iowa; 68 counties of northern Indiana; 50 counties of northern Illinois; 68 counties of southern Michigan; and 46 counties of southern Wisconsin.
`FRD08` | St. Louis -- Federal Reserve District | Covers the state of Arkansas; 44 counties in southern Illinois; 24 counties in southern Indiana; 64 counties in western Kentucky; 39 counties in northern Mississippi; 71 counties in central and eastern Missouri; the city of St. Louis; and 21 counties in western Tennessee.
`FRD09` | Minneapolis -- Federal Reserve District | Covers the states of Minnesota, Montana, North Dakota, and South Dakota; the Upper Peninsula of Michigan; and 26 counties in northern Wisconsin.
`FRD10` | Kansas City -- Federal Reserve District | Covers the states of Colorado, Kansas, Nebraska, Oklahoma, and Wyoming; 43 counties in western Missouri; and 14 counties in northern New Mexico.
`FRD11` | Dallas -- Federal Reserve District | Covers the state of Texas; 26 parishes in northern Louisiana; and 18 counties in southern New Mexico.
`FRD12` | San Francisco -- Federal Reserve District | Covers the states of Alaska, Arizona, California, Hawaii, Idaho, Nevada, Oregon, Utah, and Washington.<br><br>Note: While the San Francisco Fed serves American Samoa, Guam, and the Commonwealth of the Northern Mariana Islands, employment and wage data for these areas are not included in the FRD12 totals because these jurisdictions do not report to the Bureau of Labor Statistics' Quarterly Census of Employment and Wages (QCEW).
`FRD99` | Unknown -- Federal Reserve District | See [Technical Information](#handling-of-suppressed-county-data).
`USDPV` | Total U.S. | Total United States (includes the 50 U.S. states, District of Columbia, Puerto Rico, and U.S. Virgin Islands).