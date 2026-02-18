"""
Labor-Time Price Analysis Demo

This script demonstrates the labor-time price calculation tools
with real-world examples and formatted output.

Run with: python labor_time_demo.py
"""

from labor_time_tools import (
    labor_hours, labor_days, labor_weeks, labor_years,
    compare_countries, compare_historical, inequality_ratio,
    plot_country_comparison, plot_historical, plot_inequality_map,
    affordability_index, real_price_change,
    COUNTRY_DATA, USA_HISTORICAL_WAGES
)


def print_header(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f" {title}")
    print("=" * 70)


def print_subheader(title: str):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")


def demo_basic_conversions():
    """Demonstrate basic price-to-labor conversions."""
    print_header("BASIC LABOR-TIME CONVERSIONS")

    examples = [
        ("Coffee", 5.00),
        ("Movie Ticket", 15.00),
        ("New Sneakers", 120.00),
        ("Smartphone", 999.00),
        ("Used Car", 15000.00),
        ("New Car", 35000.00),
        ("Median Home (USA)", 420000.00),
    ]

    usa_wage = COUNTRY_DATA["USA"].median_hourly_wage_usd

    print(f"\nUsing USA median wage: ${usa_wage:.2f}/hour")
    print("-" * 70)
    print(f"{'Item':<25} {'Price':>12} {'Hours':>10} {'Days':>8} {'Weeks':>8}")
    print("-" * 70)

    for item, price in examples:
        hours = labor_hours(price, usa_wage)
        days = labor_days(price, usa_wage)
        weeks = labor_weeks(price, usa_wage)

        print(f"{item:<25} ${price:>10,.2f} {hours:>10.1f} {days:>8.1f} {weeks:>8.2f}")


def demo_global_inequality():
    """Demonstrate labor-time inequality across countries."""
    print_header("GLOBAL LABOR-TIME INEQUALITY")

    items = [
        ("iPhone 15 Pro", 999),
        ("Netflix (annual)", 180),
        ("Nike Air Max", 150),
        ("PlayStation 5", 500),
        ("MacBook Air", 1200),
    ]

    for item_name, price in items:
        print_subheader(f"{item_name} (${price})")

        print(f"{'Country':<20} {'Wage ($/hr)':>12} {'Hours':>10} {'Days':>8} {'vs USA':>10}")
        print("-" * 65)

        usa_hours = labor_hours(price, COUNTRY_DATA["USA"].median_hourly_wage_usd)

        country_data = []
        for code, country in COUNTRY_DATA.items():
            hours = labor_hours(price, country.median_hourly_wage_usd)
            ratio = hours / usa_hours
            country_data.append((country.name, country.median_hourly_wage_usd, hours, ratio))

        country_data.sort(key=lambda x: x[2])

        for name, wage, hours, ratio in country_data:
            days = hours / 8
            ratio_str = f"{ratio:.1f}x" if ratio > 1.05 else "1.0x"
            print(f"{name:<20} ${wage:>10.2f} {hours:>10.1f} {days:>8.1f} {ratio_str:>10}")


def demo_historical_analysis():
    """Demonstrate historical labor-time analysis."""
    print_header("HISTORICAL LABOR-TIME ANALYSIS (USA)")

    # Various goods with historical prices
    analyses = {
        "Median Home": {
            1950: 7400,
            1960: 11900,
            1970: 17000,
            1980: 47200,
            1990: 79100,
            2000: 119600,
            2010: 221800,
            2020: 329000,
            2024: 420000,
        },
        "New Car (Average)": {
            1950: 1510,
            1960: 2600,
            1970: 3900,
            1980: 7200,
            1990: 15400,
            2000: 21000,
            2010: 29000,
            2020: 38000,
            2024: 48000,
        },
        "College Tuition (4-year public)": {
            1970: 400,
            1980: 800,
            1990: 1900,
            2000: 3500,
            2010: 8000,
            2020: 10500,
            2024: 11000,
        },
    }

    for item_name, prices in analyses.items():
        print_subheader(item_name)

        print(f"{'Year':<8} {'Price':>12} {'Wage ($/hr)':>12} {'Hours':>10} {'Weeks':>8}")
        print("-" * 55)

        for year, price in sorted(prices.items()):
            if year in USA_HISTORICAL_WAGES:
                wage = USA_HISTORICAL_WAGES[year]
                hours = labor_hours(price, wage)
                weeks = hours / 40

                print(f"{year:<8} ${price:>10,} ${wage:>10.2f} {hours:>10.0f} {weeks:>8.1f}")


def demo_real_price_changes():
    """Demonstrate real (labor-time) price change calculations."""
    print_header("REAL PRICE CHANGES (LABOR-TIME ADJUSTED)")

    print("\nComparing 1970 vs 2024 (prices and wages from those years)")
    print("-" * 70)

    comparisons = [
        ("Median Home", 17000, 3.50, 420000, 30.00),
        ("New Car", 3900, 3.50, 48000, 30.00),
        ("TV (Color)", 500, 3.50, 400, 30.00),
        ("Refrigerator", 400, 3.50, 1200, 30.00),
        ("College (1 year)", 400, 3.50, 11000, 30.00),
        ("Doctor Visit", 15, 3.50, 200, 30.00),
        ("Gallon of Gas", 0.36, 3.50, 3.50, 30.00),
        ("Dozen Eggs", 0.60, 3.50, 4.00, 30.00),
    ]

    print(f"{'Item':<20} {'1970 Hrs':>10} {'2024 Hrs':>10} {'Change':>12} {'Direction':<15}")
    print("-" * 70)

    for name, p70, w70, p24, w24 in comparisons:
        hours_70 = labor_hours(p70, w70)
        hours_24 = labor_hours(p24, w24)
        change = real_price_change(p70, w70, p24, w24)

        if change < -10:
            direction = "Much cheaper"
        elif change < 0:
            direction = "Cheaper"
        elif change < 10:
            direction = "About same"
        elif change < 50:
            direction = "More expensive"
        else:
            direction = "Much more expensive"

        print(f"{name:<20} {hours_70:>10.1f} {hours_24:>10.1f} {change:>+11.1f}% {direction:<15}")


def demo_affordability_baskets():
    """Demonstrate affordability basket analysis."""
    print_header("MONTHLY AFFORDABILITY BASKETS")

    # Define a standardized monthly basket (in USD)
    basic_basket = {
        "Housing (rent)": 1500,
        "Food & groceries": 600,
        "Utilities": 200,
        "Transportation": 300,
        "Healthcare": 400,
        "Clothing": 100,
        "Communication": 100,
        "Other necessities": 300,
    }

    total_basket = sum(basic_basket.values())

    print(f"\nMonthly Basket Total: ${total_basket:,}")
    print("\nBreakdown:")
    for item, cost in basic_basket.items():
        print(f"  {item:<25} ${cost:>6}")

    print("\n" + "-" * 70)
    print(f"{'Country':<20} {'Wage ($/hr)':>12} {'Hours/Mo':>10} {'Weeks/Mo':>10} {'% of Month':>12}")
    print("-" * 70)

    # Standard month = 173.3 hours (40 hrs/wk * 4.33 wks)
    standard_month_hours = 173.3

    for code, country in sorted(COUNTRY_DATA.items(), key=lambda x: -x[1].median_hourly_wage_usd):
        hours = affordability_index(basic_basket, country.median_hourly_wage_usd)
        weeks = hours / 40
        pct_month = (hours / standard_month_hours) * 100

        status = ""
        if pct_month > 100:
            status = "(deficit)"

        print(f"{country.name:<20} ${country.median_hourly_wage_usd:>10.2f} {hours:>10.1f} "
              f"{weeks:>10.1f} {pct_month:>11.1f}% {status}")


def demo_inequality_ratios():
    """Demonstrate inequality ratio calculations."""
    print_header("INEQUALITY RATIOS")

    reference_countries = ["USA", "Germany"]
    comparison_countries = ["Mexico", "Brazil", "China", "India", "Nigeria", "Vietnam"]
    price = 1000  # Reference amount

    print(f"\nFor a ${price:,} item, how many times more labor do workers need?")

    for ref in reference_countries:
        print(f"\n--- Compared to {COUNTRY_DATA[ref].name} ---")
        print(f"{'Country':<20} {'Their Hours':>12} {'Ratio':>10}")
        print("-" * 45)

        ref_hours = labor_hours(price, COUNTRY_DATA[ref].median_hourly_wage_usd)

        for comp in comparison_countries:
            ratio = inequality_ratio(price, ref, comp)
            comp_hours = labor_hours(price, COUNTRY_DATA[comp].median_hourly_wage_usd)
            print(f"{COUNTRY_DATA[comp].name:<20} {comp_hours:>12.1f} {ratio:>9.1f}x")


def demo_quick_calculations():
    """Quick calculations for common scenarios."""
    print_header("QUICK CALCULATIONS")

    print("\nHow long to afford major purchases at different wage levels?")
    print("-" * 70)

    wages = [7.25, 15.00, 25.00, 50.00, 100.00]  # Federal min, $15 min, median, upper, high
    wage_labels = ["$7.25 (Fed min)", "$15 (city min)", "$25 (median)", "$50 (upper)", "$100 (high)"]
    items = [("iPhone", 999), ("Used Car", 15000), ("Median Home", 420000)]

    # Table header
    header = f"{'Item':<20}"
    for label in wage_labels:
        header += f"{label:>14}"
    print(header)
    print("-" * 90)

    for item_name, price in items:
        row = f"{item_name:<20}"
        for wage in wages:
            weeks = labor_weeks(price, wage)
            if weeks < 1:
                row += f"{labor_hours(price, wage):>11.1f} hrs"
            elif weeks < 52:
                row += f"{weeks:>11.1f} wks"
            else:
                row += f"{labor_years(price, wage):>11.1f} yrs"
        print(row)


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 70)
    print("#" + " " * 68 + "#")
    print("#" + "  LABOR-TIME PRICE ANALYSIS - COMPREHENSIVE DEMO".center(68) + "#")
    print("#" + " " * 68 + "#")
    print("#" * 70)

    print("\nThis demo shows how to measure prices in LABOR-TIME instead of")
    print("currency units. Labor-time provides a universal, human-centered")
    print("measure of value: how much of your life do you trade for this item?")

    demo_basic_conversions()
    demo_global_inequality()
    demo_historical_analysis()
    demo_real_price_changes()
    demo_affordability_baskets()
    demo_inequality_ratios()
    demo_quick_calculations()

    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print("\nFor visualizations, import and call:")
    print("  plot_country_comparison('iPhone', 999)")
    print("  plot_historical('Home', {1970: 17000, 2024: 420000})")
    print("  plot_inequality_map('iPhone', 999)")
    print("\nSee labor_time_tools.py for full API documentation.")


if __name__ == "__main__":
    main()
