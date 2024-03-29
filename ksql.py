"""Configures KSQL to combine station and turnstile data"""
import json
import logging

import requests

import topic_check


logger = logging.getLogger(__name__)


KSQL_URL = "http://localhost:8088"

KSQL_STATEMENT = """
CREATE TABLE turnstile (
    station_id INT,
    station_name VARCHAR,
    line VARCHAR 
) WITH (
    kafka_topic = 'turnstile',
    value_format = 'avro', 
    key = 'station_id'
);
CREATE TABLE turnstile_summary 
WITH (
    kafka_topic = 'turnstile_summary',
    value_format = 'json') AS 
    SELECT station_id, COUNT(station_id) AS count
    FROM turnstile 
    GROUP BY station_id;
"""


def execute_statement():
    """Executes the KSQL statement against the KSQL API"""
    if topic_check.topic_exists("TURNSTILE_SUMMARY") is True:
        return

    logging.debug("executing ksql statement now...")

    resp = requests.post(
        f"{KSQL_URL}/ksql",
        headers={"Content-Type": "application/vnd.ksql.v1+json; charset=utf-8"},
        data=json.dumps(
            {
                "ksql": KSQL_STATEMENT,
                "streamsProperties": {"ksql.streams.auto.offset.reset": "earliest"},
            }
        ),
    )

    # Ensure that a 2XX status code was returned
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        logger.info("Error with KSQL POST request.")


if __name__ == "__main__":
    execute_statement()
