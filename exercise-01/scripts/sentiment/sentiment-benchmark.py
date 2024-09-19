import os
from collections import defaultdict
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

def use_warehouse(cur, warehouse):
    cur.execute(f"use warehouse {warehouse}")

if __name__ == '__main__':
    repetitions = 3
    query_ids = []
    queryids_to_querytype = {}
    repetition_to_queryid = {}

    connection_config = create_connection("COBRA_DB", "PUBLIC")
    conn = snowflake.connector.connect(**connection_config)
    cur = conn.cursor()


    try:
        use_warehouse(cur, "ANIMAL_TASK_WH")

        # Run SQL train queries
        print("Running SQL train queries")
        for i in range(repetitions):
            queries = []
            if i < (repetitions - 1):
                print(f"Running repetition {1+i} out of {repetitions}", end="\r")
            else:
                print(f"Running repetition {1+i} out of {repetitions}")

            for idx, query in enumerate(sql.sql_train_queries):
                cur.execute(query)
                qid = cur.sfqid
                query_ids.append(qid)
                queries.append(qid)
                queryids_to_querytype[qid] = "SQL_TRAIN"
            
            repetition_to_queryid[(i, "SQL_TRAIN")] = queries


        # Run SQL predict queries        
        print("Running SQL predict queries")
        for i in range(repetitions):
            queries = []
            if i < (repetitions - 1):
                print(f"Running repetition {1+i} out of {repetitions}", end="\r")
            else:
                print(f"Running repetition {1+i} out of {repetitions}")

            for query in sql.sql_test_queries:
                cur.execute(query)
                qid = cur.sfqid
                query_ids.append(qid)
                queryids_to_querytype[qid] = "SQL_PREDICT"

            repetition_to_queryid[(i, "SQL_PREDICT")] = queries
        
        # Run UDTF train queries
        print("Running UDTF train queries")
        for i in range(repetitions):
            if i < (repetitions - 1):
                print(f"Running repetition {1+i} out of {repetitions}", end="\r")
            else:
                print(f"Running repetition {1+i} out of {repetitions}")

            cur.execute(udtf.udtf_train)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "UDTF_TRAIN"
            repetition_to_queryid[(i, "UDTF_TRAIN")] = [qid]
        
        # Run UDTF predict queries
        print("Running UDTF predict queries")
        for i in range(repetitions):
            if i < (repetitions - 1):
                print(f"Running repetition {1+i} out of {repetitions}", end="\r")
            else:
                print(f"Running repetition {1+i} out of {repetitions}")

            cur.execute(udtf.udtf_query)
            qid = cur.sfqid
            query_ids.append(qid)
            queryids_to_querytype[qid] = "UDTF_PREDICT"
            repetition_to_queryid[(i, "UDTF_PREDICT")] = [qid]

        
        stats = get_query_stats(cur, query_ids)
        stats_mapping = {}
        for qid, schema, warehouse_size, elapsed_seconds, elapsed_milli in stats:
            stats_mapping[qid] = (schema, warehouse_size, elapsed_seconds, elapsed_milli)

        with open('./benchmark_sentiment_stats.csv', 'w') as file:
            writer = csv.writer(file, delimiter=';')


            for (i, query_type), qids in repetition_to_queryid.items():
                aggregated_elapsed_milli = sum([stats_mapping[qid][3] for qid in qids])
                aggregated_elapsed_seconds = aggregated_elapsed_milli / 1000
                writer.writerow((i, query_type, aggregated_elapsed_seconds, aggregated_elapsed_milli))

    finally:
        conn.close()

    print("Benchmark results is written to 'benchmark_sentiment_stats.csv'")