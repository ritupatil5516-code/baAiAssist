from datetime import datetime, timedelta
import re

def rewrite_query(user_query: str) -> str:
    """
    Very basic query rewrite:
    - Normalize dates for 'last X months'
    - Keep amounts in numeric form
    """
    query = user_query

    # Last X months → date range
    match = re.search(r"last (\d+) months", query.lower())
    if match:
        months = int(match.group(1))
        end = datetime.today()
        start = end - timedelta(days=months * 30)
        query += f" (Date between {start.strftime('%Y-%m-%d')} and {end.strftime('%Y-%m-%d')})"

    # $ amounts → numeric
    query = re.sub(r"\$([0-9]+)", r"\1 USD", query)

    return query