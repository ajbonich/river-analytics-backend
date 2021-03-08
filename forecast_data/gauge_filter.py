import datetime
import pandas as pd
import time


def get_site_numbers(file_path: str) -> pd.DataFrame:
    """takes in a file path and returns a DataFrame of site numbers"""
    site_df = pd.read_json(file_path, dtype={"site_no": str})
    site_df.drop(columns=["coord_acy_cd", "dec_lat_long_datum_cd"], inplace=True)
    print(f"Loaded {len(site_df)} sites.")
    return site_df


def get_site_max_value(sites: list) -> pd.DataFrame:
    """Takes in a csv string of sites and
    returns a DataFrame of the max value for each site"""
    site_csv = ",".join(sites)
    # print(f"{len(sites)} Sites tested: ")
    # print(f"{site_csv}\n")
    url = f"https://nwis.waterdata.usgs.gov/nwis/peak?multiple_site_no={site_csv}&begin_date=2015-01-01&end_date=2021-01-01&format=rdb"  # noqa: E501
    max_df = pd.read_csv(url, sep="\t", comment="#", dtype={"site_no": str})
    max_df.drop(0, inplace=True)  # drops column type row
    max_df["peak_va"] = pd.to_numeric(max_df["peak_va"])
    return max_df.groupby("site_no")["peak_va"].max()


def filter_sites_annual_max(file_path: str, batch_size: int, min_value: float) -> None:
    """Runs a job to remove sites from the json file that don't meet the criteria"""
    site_df = pd.read_json(file_path, dtype={"site_no": str})
    site_numbers = site_df["site_no"].tolist()
    site_numbers.sort()
    print(f"Found {len(site_numbers)} sites.")

    # missing_data = []
    sites: list = []
    for i in range(0, int(len(site_numbers) / batch_size) + 1):
        tested_sites = site_numbers[i * batch_size : (i + 1) * batch_size]  # noqa: E203
        site_max_value = get_site_max_value(tested_sites)
        # found_data = site_max_value.index.tolist()
        # for site in tested_sites:
        #     if site not in found_data:
        #         missing_data.append(site)

        valid_sites = site_max_value[site_max_value > min_value].index.tolist()
        sites.append(site_df[site_df["site_no"].isin(valid_sites)])  # add valid sites
    all_valid_sites = pd.concat(sites)
    # print("No max data for sites:")
    # print(missing_data)
    print(f"{len(all_valid_sites)} valid out of {len(site_numbers)} sites.")
    all_valid_sites.to_json(
        f"./test_data/all_filtered_sites_min_value_{min_value}_since_2015.json",
        orient="records",
    )


def get_daily_mean_data(site_numbers: list) -> pd.DataFrame:
    site_csv = ",".join(site_numbers)
    # print(f"{len(sites)} Sites tested: ")
    # print(f"{site_csv}\n")
    url = f"https://waterservices.usgs.gov/nwis/stat/?format=rdb,1.0&sites={site_csv}&startDT=2000-01-01&endDT=2021-01-01&statReportType=daily&statTypeCd=mean&parameterCd=00060"  # noqa: E501
    df = pd.read_csv(url, sep="\t", comment="#", dtype={"site_no": str})
    df.drop(0, inplace=True)  # drops column type row
    return df


def filter_sites_daily_mean(file_path: str, batch_size: int) -> None:
    """Runs a job"""
    site_df = pd.read_json(file_path, dtype={"site_no": str})
    site_numbers = site_df["site_no"].tolist()
    site_numbers.sort()
    print(f"Loaded {len(site_numbers)} sites.")

    # missing_data = []
    daily_means: list = []
    for i in range(0, int(len(site_numbers) / batch_size) + 1):
        site_number_batch = site_numbers[
            i * batch_size : (i + 1) * batch_size  # noqa:E203
        ]
        mean_daily_values = get_daily_mean_data(site_number_batch)
        daily_means.append(mean_daily_values)
        if i % 100 == 0:
            print(f"{datetime.datetime.now().time()}: Processing index {i * 10}")
        time.sleep(1)

    all_site_daily_means = pd.concat(daily_means)
    print(f"Retrieved {len(all_site_daily_means)} lines of data.")
    all_site_daily_means.to_json(
        "./test_data/all_all_site_daily_means_since_2000.json",
        orient="records",
    )


def filter_sites_with_daily_mean(file_path: str, min_value: float, days: int) -> None:
    """Takes in a file, path, a daily mean minimum, and the number of days the site has
    to be above the minimum"""
    sites_df = get_site_numbers(file_path)
    site_means_df = pd.read_json(
        "./test_data/all_all_site_daily_means_since_2000.json",
        dtype={"site_no": str, "mean_va": float},
    )
    site_means_df.drop(
        columns=[
            "agency_cd",
            "parameter_cd",
            "ts_id",
            "loc_web_ds",
            "begin_yr",
            "end_yr",
            "count_nu",
        ],
        inplace=True,
    )
    site_means_df = site_means_df.groupby("site_no")["mean_va"].nlargest(days)
    site_mins_df = site_means_df.groupby("site_no").min()
    valid_sites = site_mins_df[site_mins_df > min_value].index.tolist()
    all_valid_sites = sites_df[sites_df["site_no"].isin(valid_sites)]
    print(f"Remaining sites: {len(all_valid_sites)}.")
    all_valid_sites.to_json(
        f"./test_data/sites_with_{days}_days_above_{min_value}_since_2000.json",
        orient="records",
    )


if __name__ == "__main__":
    batch_length = 10
    minimum_value = 250
    days = 7
    sites_to_filter_daily_mean_file = (
        "./test_data/all_filtered_sites_min_value_250_since_2015.json"
    )
    sites_to_filter_annual_peak_file = "./test_data/all_sites_since_2000.json"
    filter_sites_with_daily_mean(sites_to_filter_daily_mean_file, minimum_value, days)
    # filter_sites_daily_mean(sites_to_filter_annual_peak_file, batch_length)
    # filter_sites_annual_max(sites_to_filter_annual_peak_file, batch_length, minimum_value)  # noqa: E501
    # filter_sites("./test_data/site_list.json")
