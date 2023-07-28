"""Module for printing report days"""
from datetime import date
from typing import Tuple
import sys
import json
import importlib
import argparse

from workalendar.core import WesternCalendar


###################################
SUPPORTED_MINOR_VERSION = 9
###################################

CONFIG_FILE_NAME = "time_report_config.json"
DAYS_IN_A_WEEK = 7

CFG = None


class Configuration:
    """Class for loading and accessing configuration"""

    def __init__(self) -> None:
        try:
            with open(CONFIG_FILE_NAME, "r", encoding="utf-8") as file:
                json_data = file.read()
        except FileNotFoundError as error_info:
            print(f"Failed to load configuration file: {error_info}")
            sys.exit(1)
        data = json.loads(json_data)

        try:
            self.report_language = data["report_language"]
            self.country = data["country"]
            self.continent = data["continent"]
            self.start_hour = data["start_hour"]
            self.end_hour = data["end_hour"]
            self.work_days = data["work_days"]
            self.vacation_spelling = data["vacation"]
            self.holiday_spelling = data["holiday"]
        except KeyError as key_info:
            print(f"Failed to access configuration parameter: {key_info}")

        country_class = load_country_module(self.continent, self.country)
        self.calendar = country_class()

    def is_holiday(self, day) -> bool:
        """Check if provided date is for holiday"""
        return self.calendar.is_holiday(day=day)

    def is_workday(self, day) -> bool:
        """Check if provided date is for a working day"""
        day_of_week = day.isocalendar().weekday
        return day_of_week in self.work_days

    def is_vacation(self, day) -> bool:
        """Check if provided date is part of vacation"""
        return False


def process_args():
    """Function for processing arguments"""
    args = argparse.ArgumentParser()

    args.add_argument(
        "-w",
        "--week",
        help="Relative week, 0 is this week, -x are previous weeks",
        type=int,
        default=0,
    )

    return args.parse_args()


def get_cfg() -> Configuration:
    """Return an instance of configuration object."""
    global CFG

    if CFG is None:
        CFG = Configuration()

    return CFG


def load_country_module(continent_name: str, country_name: str) -> WesternCalendar:
    """Loads a selected country module"""
    try:
        # Import the country module dynamically
        module_name = f"workalendar.{continent_name.lower()}.{country_name.lower()}"
        country_module = importlib.import_module(module_name)

        # Get the class name dynamically
        class_name = country_name

        # Import the specific class dynamically
        country_class = getattr(country_module, class_name)

    except (ImportError, AttributeError) as error_info:
        print(f"Failed to import country: {country_name}")
        print(f"Error: {error_info}")
        print(
            "Please note, country needs to be formatted like this: 'continent.country'"
        )
        print("Example: 'europe.poland'")
        sys.exit(1)

    return country_class


def get_current_year() -> int:
    """Function returns current year"""
    return date.today().isocalendar().year


def get_current_week() -> int:
    """Function returning number of a week"""
    return date.today().isocalendar().week


def get_day_from_week(week: int, day: int):
    """Function returning date from given week and day, 1==Monday"""
    year = get_current_year()
    return date.fromisocalendar(year, week, day)


def get_list_of_days(week: int) -> Tuple[date,]:
    """Return list of days in a week, if month changes it returns to separate lists in Tuple."""

    week_days = [get_day_from_week(week, day) for day in range(1, DAYS_IN_A_WEEK + 1)]
    work_days = [day for day in week_days if get_cfg().is_workday(day)]

    if work_days[0].month != work_days[-1].month:
        # a month change
        first_moth = work_days[0].month
        second_month = work_days[-1].month

        first_moth_days = [day for day in work_days if day.month == first_moth]
        second_moth_days = [day for day in work_days if day.month == second_month]

        return (first_moth_days, second_moth_days)

    return (work_days,)


def format_day(day) -> str:
    """Formats a day into final output"""
    cfg = get_cfg()
    date_str = day.strftime("%d:%m")
    day_name = day.strftime("%a")

    description = ""
    if cfg.is_holiday(day):
        description = cfg.holiday_spelling
    elif cfg.is_vacation(day):
        description = cfg.vacation_spelling
    else:
        work_start = cfg.start_hour
        work_end = cfg.end_hour
        description = f"Start: {work_start}; End: {work_end}"

    report = f"{day_name}-{date_str}.: {description}"

    return report


def get_reports(week) -> list:
    """Formats a final report for a week"""
    days = get_list_of_days(week)

    reports = []
    for sub_week in days:
        sub_report = []
        title = f"Working hours {sub_week[0]:%d}-{sub_week[-1]:%d} Of {sub_week[0]:%B}"
        sub_report.append(title)
        for day in sub_week:
            report = format_day(day)
            sub_report.append(report)
        reports.append(sub_report)

    return reports


def print_report(week):
    """Prints  a report"""
    reports = get_reports(week)

    for sub_report in reports:
        for report in sub_report:
            print(report)
        print("\n")


def main():
    """Main body"""
    args = process_args()

    week_delta = args.week

    week = get_current_week() + week_delta
    print_report(week)


if __name__ == "__main__":
    if sys.version_info.minor < SUPPORTED_MINOR_VERSION:
        raise ImportError(
            f"Minor version of your python: [{sys.version_info.minor}] is smaller\
             than minimal supported [{SUPPORTED_MINOR_VERSION}]"
        )
    main()
