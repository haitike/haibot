ASCENDING = 1
DESCENDING = -1

def get_col_lastdocs(col, amount, query=None):
    return col.find(query).sort("$natural",DESCENDING).limit(amount)