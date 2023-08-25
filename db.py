import logging
from datetime import datetime

from pydantic import BaseModel
from pymongo import MongoClient, errors
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status
from pymongo.errors import ServerSelectionTimeoutError

from config import MONGO_CLUSTER_URI, MONGO_DATABASE
from logging_config import formater, file_handler


logger = logging.getLogger(__name__)
file_handler.setFormatter(formater)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


TIMESTAMP_KEY = "timestamp"


class MongoDB():
    def __init__(self, uri: str, database: str) -> None:
        try:
            self.client = MongoClient(uri)
            self.db = self.client.get_database(name=database)
        # except ServerSelectionTimeoutError:
        #     raise ServerSelectionTimeoutError
        except errors.ConnectionFailure:
            raise HTTPException(status=status.HTTP_400_BAD_REQUEST,
                                detail="Server is Down for sometime.")

    def insert_record(self, collection: str, record: dict | BaseModel) -> None:
        try:
            self.db[collection].insert_one(jsonable_encoder(
                record) | {TIMESTAMP_KEY: datetime.utcnow()})
            logger.info(f"Record inserted in collection '{collection}'")
        except Exception as e:
            logger.error(
                f"Failed to insert record in collection '{collection}': {str(e)}")

    def update_record(self, collection: str, record: dict | BaseModel, key: str) -> None:
        try:
            self.upsert_record_many(
                collection, jsonable_encoder(record), [key])
            logger.info(f"Record updated in collection '{collection}'")
        except Exception as e:
            logger.error(
                f"Failed to update record in collection '{collection}': {str(e)}")

    def get_record(self, collection: str, key: str, value: str) -> dict | None:
        try:
            record = self.db[collection].find_one(
                filter={key: value}, projection={"_id": False})
            if record:
                logger.info(f"Record retrieved from collection '{collection}'")
            else:
                logger.info(f"Record not found in collection '{collection}'")
            return record
        except Exception as e:
            logger.error(
                f"Failed to retrieve record from collection '{collection}': {str(e)}")
            return None

    def get_records(self, collection: str, key: str, value: str) -> list[dict]:
        try:
            records = list(self.db[collection].find(
                filter={key: value}, projection={"_id": False}))
            logger.info(f"Records retrieved from collection '{collection}'")
            return records
        except Exception as e:
            logger.error(
                f"Failed to retrieve records from collection '{collection}': {str(e)}")
            return []

    def delete_record(self, collection: str, key: str, value: str) -> None:
        try:
            self.db[collection].delete_one(filter={key: value})
            logger.info(f"Record deleted from collection '{collection}'")
        except Exception as e:
            logger.error(
                f"Failed to delete record from collection '{collection}': {str(e)}")

    def upsert_record_many(self, collection: str, record: dict | BaseModel, keys: list[str]) -> None:
        try:
            record = jsonable_encoder(record)
            if len(set(keys) - set(record.keys())) != 0:
                raise ValueError(
                    f"Invalid keys: {list(set(keys) - set(record.keys()))}")
            self.db[collection].update_many(
                filter={key: record[key] for key in keys},
                update={'$set': record | {TIMESTAMP_KEY: datetime.utcnow()}},
                upsert=True
            )
            logger.info(f"Record upserted in collection '{collection}'")
        except Exception as e:
            logger.error(
                f"Failed to upsert record in collection '{collection}': {str(e)}")


DB = MongoDB(uri=MONGO_CLUSTER_URI, database=MONGO_DATABASE)
