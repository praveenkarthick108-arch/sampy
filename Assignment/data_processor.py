import pandas as pd


def process_csv(df: pd.DataFrame) -> dict:
    df = df.copy()
    df['Date'] = pd.to_datetime(df['Date'])

    total_revenue = df['Revenue_USD'].sum()
    total_profit = df['Profit_USD'].sum()
    total_units = int(df['Units_Sold'].sum())
    avg_rating = df['Customer_Rating'].mean()
    total_returns = int(df['Returns'].sum())
    profit_margin = (total_profit / total_revenue * 100) if total_revenue else 0

    by_product = df.groupby('Product_Name').agg(
        Revenue_USD=('Revenue_USD', 'sum'),
        Profit_USD=('Profit_USD', 'sum'),
        Units_Sold=('Units_Sold', 'sum'),
        Customer_Rating=('Customer_Rating', 'mean'),
        Returns=('Returns', 'sum'),
        Marketing_Spend_USD=('Marketing_Spend_USD', 'sum'),
    ).round(2)
    by_product['Profit_Margin_pct'] = (by_product['Profit_USD'] / by_product['Revenue_USD'] * 100).round(1)
    by_product['Return_Rate_pct'] = (by_product['Returns'] / by_product['Units_Sold'] * 100).round(1)

    by_category = df.groupby('Category').agg(
        Revenue_USD=('Revenue_USD', 'sum'),
        Profit_USD=('Profit_USD', 'sum'),
        Units_Sold=('Units_Sold', 'sum'),
        Customer_Rating=('Customer_Rating', 'mean'),
    ).round(2)

    by_region = df.groupby('Region').agg(
        Revenue_USD=('Revenue_USD', 'sum'),
        Profit_USD=('Profit_USD', 'sum'),
        Units_Sold=('Units_Sold', 'sum'),
    ).round(2)

    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    monthly = df.groupby('Month').agg(
        Revenue_USD=('Revenue_USD', 'sum'),
        Profit_USD=('Profit_USD', 'sum'),
        Units_Sold=('Units_Sold', 'sum'),
    ).round(2)

    reviews = df[['Product_Name', 'Customer_Rating', 'Review']].dropna()
    review_sample = reviews.sample(min(40, len(reviews)), random_state=42)
    review_text = '\n'.join(
        f"- {row.Product_Name} ({row.Customer_Rating}/5): {row.Review}"
        for _, row in review_sample.iterrows()
    )

    summary_text = f"""## Sales Data Overview
- Date Range: {df['Date'].min().date()} to {df['Date'].max().date()}
- Total Records: {len(df):,}
- Total Revenue: ${total_revenue:,.2f}
- Total Profit: ${total_profit:,.2f}
- Overall Profit Margin: {profit_margin:.1f}%
- Total Units Sold: {total_units:,}
- Average Customer Rating: {avg_rating:.2f}/5.0
- Total Returns: {total_returns}

## Product Performance
{by_product[['Revenue_USD','Profit_USD','Units_Sold','Customer_Rating','Profit_Margin_pct','Return_Rate_pct']].to_string()}

## Category Performance
{by_category.to_string()}

## Regional Performance
{by_region.to_string()}

## Monthly Revenue & Profit Trends
{monthly.to_string()}

## Customer Reviews Sample ({len(review_sample)} entries)
{review_text}
"""

    return {
        'text': summary_text,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
        'total_units': total_units,
        'avg_rating': avg_rating,
        'total_returns': total_returns,
        'profit_margin': profit_margin,
        'by_product': by_product,
        'by_category': by_category,
        'by_region': by_region,
        'monthly': monthly,
        'df': df,
    }
