
from datetime import datetime, timedelta
import re

def rewrite_query(user_query: str) -> str:
    query = user_query

    m = re.search(r"last\s+(\d+)\s+months", query.lower())
    if m:
        months = int(m.group(1))
        end = datetime.today()
        start = end - timedelta(days=months*30)
        query += f" (Date between {start.strftime('%Y-%m-%d')} and {end.strftime('%Y-%m-%d')})"

    query = re.sub(r"\$([0-9]+)", r"\1 USD", query)
    return query
