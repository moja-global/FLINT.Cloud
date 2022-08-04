import sqlite3
import pandas as pd

conn = sqlite3.connect("local/rest_api_gcbm/tests/output/compiled_simulation_output.db")

query = f"""
        SELECT years.year, COALESCE(SUM(i.pool_tc), 0) / 1e6 AS total_biomass_mt
        FROM (SELECT DISTINCT year FROM v_age_indicators ORDER BY year) AS years
        LEFT JOIN v_pool_indicators i
            ON years.year = i.year
        WHERE i.indicator = 'Total Biomass'
            AND (years.year BETWEEN 2010 AND 2020)
        GROUP BY years.year
        ORDER BY years.year
        """

df = pd.read_sql_query(query, conn)
ax = df.plot.line("year")  # x-axis
ax.figure.savefig("local/rest_api_gcbm/tests/output/total_biomass_mt.png", dpi=300)
