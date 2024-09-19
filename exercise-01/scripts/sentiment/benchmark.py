import os
import csv
import snowflake.connector
import queries.udtf as udtf
import queries.sql as sql

def create_connection(database_name, schema_name):
    password = os.getenv('SNOWSQL_PWD')

    snowflake_config = {
        "user": "COBRA",
        "password": password,
        "account": "sfedu02-gyb58550",
        "database": database_name,
        "schema": schema_name,
        "session_parameters": {
            "USE_CACHED_RESULT": False
        }
    }

    return snowflake_config

def get_query_stats(cur, query_ids):
    query_ids_str = ', '.join([f"'{qid}'" for qid in query_ids])

    stats_query = f"""
    SELECT query_id, schema_name, warehouse_size, total_elapsed_time/1000 AS time_elapsed_in_seconds, total_elapsed_time AS total_elapsed_time_milli
    FROM
        table(information_schema.query_history())
    WHERE user_name = 'COBRA' and execution_status = 'SUCCESS' and query_id IN ({query_ids_str})
    ORDER BY start_time desc;
    """
    
    cur.execute(stats_query)
    return cur.fetchall()

def run_udtf_query(cur):
    cur.execute(udtf.udtf_train)
    cur.execute(udtf.udtf_query)

def run_sql_query(cur):
    cur.execute(sql.sql_query)

def use_warehouse(cur, warehouse):
    cur.execute(f"use warehouse {warehouse}")

if __name__ == '__main__':
    repetitions = 3
    query_ids = []
    queryids_to_querytype = {}

    connection_config = create_connection("COBRA_DB", "PUBLIC")
    conn = snowflake.connector.connect(**connection_config)
    cur = conn.cursor()


    try:
        use_warehouse(cur, "ANIMAL_TASK_WH")

        # Run SQL train queries
        print("Running SQL train queries")
        for i in range(repetitions):
            cur.execute(sql.sql_train)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "SQL_TRAIN"

        # Run SQL predict queries        
        print("Running SQL predict queries")
        for i in range(repetitions):
            cur.execute(sql.sql_query)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "SQL_PREDICT"
        
        # Run UDTF train queries
        print("Running UDTF train queries")
        for i in range(repetitions):
            cur.execute(udtf.udtf_train)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "UDTF_TRAIN"
        
        # Run UDTF predict queries
        print("Running UDTF predict queries")
        for i in range(repetitions):
            cur.execute(udtf.udtf_query)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "UDTF_PREDICT"

        
        stats = get_query_stats(cur, query_ids)
        with open('./benchmark_stats.csv', 'w') as file:
            writer = csv.writer(file, delimiter=';')

            for qid, schema, warehouse_size, elapsed_seconds, elapsed_milli in stats:
                writer.writerow((qid, queryids_to_querytype[qid], schema, warehouse_size, float(elapsed_seconds), elapsed_milli))

    finally:
        conn.close()