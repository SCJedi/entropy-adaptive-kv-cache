"""
Labor-Time Price Calculation Tools

Convert nominal prices to labor-time units (hours, days, weeks, years)
across countries and historical periods. Provides a universal measurement
of value based on human labor time.

Theory: Price in labor-hours = Nominal Price / Hourly Wage
This measures the "real" cost of goods as the portion of human life
required to earn enough to purchase them.
"""

from dataclasses import dataclass
from typing import Optional, Dict, List, Union
import warnings

# Try to import pandas and matplotlib, with graceful fallback
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    warnings.warn("pandas not available. DataFrame functions will return dicts instead.")

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("matplotlib not available. Plotting functions will print tables instead.")


# =============================================================================
# CORE CONVERSION FUNCTIONS
# =============================================================================

def labor_hours(price: float, hourly_wage: float) -> float:
    """
    Convert nominal price to labor-hours.

    Args:
        price: Nominal price in currency units
        hourly_wage: Hourly wage in the same currency

    Returns:
        Number of labor-hours required to purchase the item
    """
    if hourly_wage <= 0:
        raise ValueError("Hourly wage must be positive")
    return price / hourly_wage


def labor_days(price: float, hourly_wage: float, hours_per_day: float = 8) -> float:
    """
    Convert nominal price to labor-days.

    Args:
        price: Nominal price in currency units
        hourly_wage: Hourly wage in the same currency
        hours_per_day: Working hours per day (default: 8)

    Returns:
        Number of labor-days required to purchase the item
    """
    return labor_hours(price, hourly_wage) / hours_per_day


def labor_weeks(price: float, hourly_wage: float, hours_per_week: float = 40) -> float:
    """
    Convert nominal price to labor-weeks.

    Args:
        price: Nominal price in currency units
        hourly_wage: Hourly wage in the same currency
        hours_per_week: Working hours per week (default: 40)

    Returns:
        Number of labor-weeks required to purchase the item
    """
    return labor_hours(price, hourly_wage) / hours_per_week


def labor_years(price: float, hourly_wage: float, hours_per_year: float = 2080) -> float:
    """
    Convert nominal price to labor-years.

    Args:
        price: Nominal price in currency units
        hourly_wage: Hourly wage in the same currency
        hours_per_year: Working hours per year (default: 2080 = 52 weeks * 40 hours)

    Returns:
        Number of labor-years required to purchase the item
    """
    return labor_hours(price, hourly_wage) / hours_per_year


# =============================================================================
# COUNTRY WAGE DATA
# =============================================================================

@dataclass
class CountryWageData:
    """
    Wage data for a country.

    Attributes:
        name: Country name
        median_hourly_wage_usd: Median hourly wage in USD
        currency: Local currency code
        ppp_factor: Purchasing power parity adjustment factor
                    (1.0 = same purchasing power as USD in USA)
    """
    name: str
    median_hourly_wage_usd: float
    currency: str
    ppp_factor: float


# Country wage data (approximate values for 2024)
# Sources: OECD, ILO, World Bank estimates
COUNTRY_DATA: Dict[str, CountryWageData] = {
    "USA": CountryWageData("United States", 30.00, "USD", 1.00),
    "Germany": CountryWageData("Germany", 28.00, "EUR", 0.85),
    "UK": CountryWageData("United Kingdom", 22.00, "GBP", 0.90),
    "Japan": CountryWageData("Japan", 18.00, "JPY", 0.75),
    "South Korea": CountryWageData("South Korea", 16.00, "KRW", 0.80),
    "Mexico": CountryWageData("Mexico", 4.50, "MXN", 0.45),
    "Brazil": CountryWageData("Brazil", 4.00, "BRL", 0.50),
    "China": CountryWageData("China", 6.50, "CNY", 0.55),
    "India": CountryWageData("India", 2.00, "INR", 0.30),
    "Nigeria": CountryWageData("Nigeria", 1.50, "NGN", 0.35),
    "Egypt": CountryWageData("Egypt", 2.50, "EGP", 0.40),
    "Vietnam": CountryWageData("Vietnam", 3.00, "VND", 0.45),
}


# =============================================================================
# HISTORICAL USA WAGE DATA
# =============================================================================

USA_HISTORICAL_WAGES: Dict[int, float] = {
    1950: 1.50,
    1960: 2.30,
    1970: 3.50,
    1980: 7.00,
    1990: 10.00,
    2000: 14.00,
    2010: 18.00,
    2020: 25.00,
    2024: 30.00,
}


# =============================================================================
# COMPARISON FUNCTIONS
# =============================================================================

def compare_countries(price_usd: float, countries: Optional[List[str]] = None) -> Union['pd.DataFrame', Dict]:
    """
    Compare labor-hours across countries for a given USD price.

    Args:
        price_usd: Price in USD
        countries: List of country codes (default: all available)

    Returns:
        DataFrame or dict with labor-hours by country
    """
    if countries is None:
        countries = list(COUNTRY_DATA.keys())

    results = []
    for code in countries:
        if code not in COUNTRY_DATA:
            warnings.warn(f"Country '{code}' not found in database")
            continue
        country = COUNTRY_DATA[code]
        hours = labor_hours(price_usd, country.median_hourly_wage_usd)
        results.append({
            "Country": country.name,
            "Code": code,
            "Hourly Wage (USD)": country.median_hourly_wage_usd,
            "Labor Hours": round(hours, 2),
            "Labor Days": round(labor_days(price_usd, country.median_hourly_wage_usd), 2),
        })

    if PANDAS_AVAILABLE:
        return pd.DataFrame(results).sort_values("Labor Hours")
    return results


def compare_historical(prices_by_year: Dict[int, float],
                       years: Optional[List[int]] = None) -> Union['pd.DataFrame', Dict]:
    """
    Compare labor-hours across years for prices in different years.

    Args:
        prices_by_year: Dict mapping year to price in that year's dollars
        years: List of years to include (default: all in prices_by_year)

    Returns:
        DataFrame or dict with labor-hours by year
    """
    if years is None:
        years = sorted(prices_by_year.keys())

    results = []
    for year in years:
        if year not in prices_by_year:
            continue
        if year not in USA_HISTORICAL_WAGES:
            warnings.warn(f"No wage data for year {year}")
            continue

        price = prices_by_year[year]
        wage = USA_HISTORICAL_WAGES[year]
        hours = labor_hours(price, wage)

        results.append({
            "Year": year,
            "Price ($)": price,
            "Hourly Wage ($)": wage,
            "Labor Hours": round(hours, 2),
            "Labor Days": round(hours / 8, 2),
            "Labor Weeks": round(hours / 40, 2),
        })

    if PANDAS_AVAILABLE:
        return pd.DataFrame(results)
    return results


def inequality_ratio(price_usd: float, country1: str, country2: str) -> float:
    """
    Calculate how many times more labor country2 needs vs country1.

    Args:
        price_usd: Price in USD
        country1: Code of reference country (typically higher wage)
        country2: Code of comparison country

    Returns:
        Ratio of labor-hours (country2 / country1)

    Example:
        inequality_ratio(1000, "USA", "India") might return 15.0,
        meaning an Indian worker needs 15x the labor-hours of a US worker
        to afford the same $1000 item.
    """
    if country1 not in COUNTRY_DATA or country2 not in COUNTRY_DATA:
        raise ValueError("Country code not found")

    hours1 = labor_hours(price_usd, COUNTRY_DATA[country1].median_hourly_wage_usd)
    hours2 = labor_hours(price_usd, COUNTRY_DATA[country2].median_hourly_wage_usd)

    return hours2 / hours1


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def plot_country_comparison(item_name: str, price_usd: float,
                           countries: Optional[List[str]] = None):
    """
    Create a bar chart of labor-hours by country.

    Args:
        item_name: Name of the item for the title
        price_usd: Price in USD
        countries: List of country codes (default: all available)
    """
    if countries is None:
        countries = list(COUNTRY_DATA.keys())

    data = []
    for code in countries:
        if code in COUNTRY_DATA:
            hours = labor_hours(price_usd, COUNTRY_DATA[code].median_hourly_wage_usd)
            data.append((COUNTRY_DATA[code].name, hours))

    data.sort(key=lambda x: x[1])
    names, hours_list = zip(*data)

    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(names, hours_list, color='steelblue')
        ax.set_xlabel('Labor Hours')
        ax.set_title(f'Labor-Hours to Purchase {item_name} (${price_usd:,.2f})')
        ax.bar_label(bars, fmt='%.1f hrs')
        plt.tight_layout()
        plt.show()
    else:
        print(f"\nLabor-Hours to Purchase {item_name} (${price_usd:,.2f})")
        print("-" * 50)
        for name, hrs in data:
            bar = "#" * int(hrs / max(hours_list) * 30)
            print(f"{name:20s} | {bar:30s} {hrs:.1f} hrs")


def plot_historical(item_name: str, prices_by_year: Dict[int, float]):
    """
    Create a line chart of labor-hours over time.

    Args:
        item_name: Name of the item for the title
        prices_by_year: Dict mapping year to price in that year's dollars
    """
    years = sorted(prices_by_year.keys())
    hours_list = []

    for year in years:
        if year in USA_HISTORICAL_WAGES:
            hours_list.append(labor_hours(prices_by_year[year], USA_HISTORICAL_WAGES[year]))
        else:
            hours_list.append(None)

    if MATPLOTLIB_AVAILABLE:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(years, hours_list, marker='o', linewidth=2, markersize=8)
        ax.set_xlabel('Year')
        ax.set_ylabel('Labor Hours')
        ax.set_title(f'Labor-Hours to Purchase {item_name} Over Time (USA)')
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print(f"\nLabor-Hours to Purchase {item_name} Over Time (USA)")
        print("-" * 50)
        for year, hrs in zip(years, hours_list):
            if hrs is not None:
                bar = "#" * int(hrs / max(h for h in hours_list if h) * 30)
                print(f"{year} | {bar:30s} {hrs:.1f} hrs")


def plot_inequality_map(item_name: str, price_usd: float):
    """
    Show labor-hours by country as a formatted table.
    (Full map visualization would require geopandas)

    Args:
        item_name: Name of the item for the title
        price_usd: Price in USD
    """
    print(f"\nGlobal Labor-Hour Inequality: {item_name} (${price_usd:,.2f})")
    print("=" * 65)

    data = []
    usa_hours = labor_hours(price_usd, COUNTRY_DATA["USA"].median_hourly_wage_usd)

    for code, country in COUNTRY_DATA.items():
        hours = labor_hours(price_usd, country.median_hourly_wage_usd)
        ratio = hours / usa_hours
        data.append((country.name, hours, ratio))

    data.sort(key=lambda x: x[1])

    print(f"{'Country':<20} {'Labor Hours':>12} {'vs USA':>10}")
    print("-" * 65)
    for name, hours, ratio in data:
        print(f"{name:<20} {hours:>12.1f} {ratio:>9.1f}x")


# =============================================================================
# REAL-TIME DATA PLACEHOLDERS
# =============================================================================

def get_current_wage(country: str) -> float:
    """
    Fetch current median wage for a country.

    This is a placeholder for API integration. In production, this would
    connect to data sources like:
    - Bureau of Labor Statistics (USA)
    - OECD.Stat
    - ILO ILOSTAT
    - World Bank Open Data

    Args:
        country: Country code

    Returns:
        Current median hourly wage in USD
    """
    if country in COUNTRY_DATA:
        return COUNTRY_DATA[country].median_hourly_wage_usd
    raise ValueError(f"Country '{country}' not found. API integration not implemented.")


def get_current_price(item: str, country: str) -> float:
    """
    Fetch current price for an item in a country.

    This is a placeholder for API integration. In production, this would
    connect to data sources like:
    - Numbeo
    - The Economist Big Mac Index
    - Official retail APIs

    Args:
        item: Item identifier
        country: Country code

    Returns:
        Current price in USD
    """
    raise NotImplementedError(
        "Price API not implemented. Provide prices directly or integrate with "
        "services like Numbeo, retail APIs, or government statistics."
    )


# =============================================================================
# ANALYSIS FUNCTIONS
# =============================================================================

def affordability_index(basket: Dict[str, float], hourly_wage: float) -> float:
    """
    Calculate total labor-hours for a basket of goods.

    Args:
        basket: Dict mapping item names to prices
        hourly_wage: Hourly wage in the same currency as prices

    Returns:
        Total labor-hours to purchase the entire basket

    Example:
        basket = {"Rent": 1500, "Food": 600, "Transport": 200}
        affordability_index(basket, 25.0)  # Returns 92.0 hours
    """
    total_hours = 0
    for item, price in basket.items():
        total_hours += labor_hours(price, hourly_wage)
    return total_hours


def real_price_change(price_old: float, wage_old: float,
                      price_new: float, wage_new: float) -> float:
    """
    Calculate real (labor-time) price change as percentage.

    This measures whether an item has become more or less affordable
    in terms of labor required, independent of inflation.

    Args:
        price_old: Price in the old period
        wage_old: Hourly wage in the old period
        price_new: Price in the new period
        wage_new: Hourly wage in the new period

    Returns:
        Percentage change in labor-hours required
        Positive = item became more expensive in real terms
        Negative = item became cheaper in real terms

    Example:
        # TV cost $500 with $10/hr wage (50 hours)
        # Now costs $400 with $20/hr wage (20 hours)
        real_price_change(500, 10, 400, 20)  # Returns -60.0%
    """
    hours_old = labor_hours(price_old, wage_old)
    hours_new = labor_hours(price_new, wage_new)

    return ((hours_new - hours_old) / hours_old) * 100


# =============================================================================
# DEMO / EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LABOR-TIME PRICE TOOLS - DEMONSTRATION")
    print("=" * 70)

    # Example 1: iPhone comparison across countries
    print("\n1. IPHONE COMPARISON ACROSS COUNTRIES")
    print("-" * 70)
    iphone_price = 999
    print(f"iPhone Price: ${iphone_price}")

    comparison = compare_countries(iphone_price)
    if PANDAS_AVAILABLE:
        print(comparison.to_string(index=False))
    else:
        for row in comparison:
            print(f"{row['Country']:20s}: {row['Labor Hours']:>8.1f} hours ({row['Labor Days']:.1f} days)")

    # Example 2: Inequality ratios
    print("\n2. INEQUALITY RATIOS")
    print("-" * 70)
    pairs = [("USA", "Mexico"), ("USA", "India"), ("USA", "Nigeria"), ("Germany", "Vietnam")]
    for c1, c2 in pairs:
        ratio = inequality_ratio(iphone_price, c1, c2)
        print(f"{c2} worker needs {ratio:.1f}x the labor of {c1} worker for iPhone")

    # Example 3: Historical housing costs
    print("\n3. HISTORICAL MEDIAN HOME PRICES (USA)")
    print("-" * 70)
    home_prices = {
        1950: 7400,
        1960: 11900,
        1970: 17000,
        1980: 47200,
        1990: 79100,
        2000: 119600,
        2010: 221800,
        2020: 329000,
        2024: 420000,
    }

    historical = compare_historical(home_prices)
    if PANDAS_AVAILABLE:
        print(historical.to_string(index=False))
    else:
        for row in historical:
            print(f"{row['Year']}: ${row['Price ($)']:>10,} @ ${row['Hourly Wage ($)']:.2f}/hr = "
                  f"{row['Labor Hours']:>8.1f} hours ({row['Labor Weeks']:.1f} weeks)")

    # Example 4: Affordability basket
    print("\n4. MONTHLY AFFORDABILITY BASKET")
    print("-" * 70)
    monthly_basket = {
        "Rent": 1500,
        "Food": 600,
        "Utilities": 200,
        "Transport": 300,
        "Healthcare": 400,
        "Other": 500,
    }

    for country_code in ["USA", "Germany", "Mexico", "India"]:
        wage = COUNTRY_DATA[country_code].median_hourly_wage_usd
        total_hours = affordability_index(monthly_basket, wage)
        print(f"{COUNTRY_DATA[country_code].name:20s}: {total_hours:>6.1f} hours/month "
              f"({total_hours/40:.1f} weeks)")

    # Example 5: Real price changes
    print("\n5. REAL PRICE CHANGES (LABOR-TIME)")
    print("-" * 70)
    examples = [
        ("Television (1990 vs 2024)", 500, 10.00, 400, 30.00),
        ("College Tuition (1990 vs 2024)", 3000, 10.00, 25000, 30.00),
        ("Healthcare visit (1990 vs 2024)", 50, 10.00, 200, 30.00),
    ]

    for name, p_old, w_old, p_new, w_new in examples:
        change = real_price_change(p_old, w_old, p_new, w_new)
        direction = "cheaper" if change < 0 else "more expensive"
        print(f"{name}: {abs(change):.1f}% {direction} in real terms")

    # Visualizations
    print("\n6. VISUALIZATIONS")
    print("-" * 70)
    plot_country_comparison("iPhone", 999, ["USA", "Germany", "Mexico", "China", "India"])
    plot_inequality_map("iPhone", 999)
