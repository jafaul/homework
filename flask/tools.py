def selector(cursor, *, one=False) -> dict | tuple:
    # with conn.cursor() as cursor:
    #     cursor.execute(query, args)
    r = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
    return (r[0] if r else None) if one else r
