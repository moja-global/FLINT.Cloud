import sqlite3
import os


def get_table_schema(conn, table_name):
    """
    Get table schema for gcbm_input.db
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Get table schema for gcbm_input.db
    """
    schema = []
    ins = "PRAGMA table_info('" + table_name + "')"
    print(ins)
    for row in conn.execute(ins).fetchall():
        schema.append(row[1])
    return schema


def rename_columns(request, title):
    """
    Rename the columns/tables inside gcbm_input.db
    ---
    tags:
            - gcbm
    responses:
            200:
    parameters:
                    - in: body
            name: title
            required: true
            schema:
                    type: string
            description: Rename the columns/tables inside gcbm_input.db

    """
    input_dir = f"{os.getcwd()}/input/{title}"
    response = dict()
    conn = sqlite3.connect(f"{input_dir}/gcbm_input.db")
    for table, config in request.items():
        response[table] = dict()
        print("TABLE IS ")
        print(table)
        print(config)
        response[table]["schema_before"] = get_table_schema(conn, table)
        for old_name, new_name in config.items():
            print(old_name, new_name)
            try:
                rename = (
                    "ALTER TABLE "
                    + table
                    + " RENAME COLUMN "
                    + old_name
                    + " TO "
                    + new_name
                )
                conn.execute(rename)
            except Exception:
                print("Exception occured is ", Exception)
        response[table]["schema_after"] = get_table_schema(conn, table)
        print(response)
    conn.commit()
    conn.close()
    return response
