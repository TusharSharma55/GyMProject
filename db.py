from datetime import datetime

from pydantic import BaseModel
from pymongo import MongoClient, errors
from fastapi.encoders import jsonable_encoder
from fastapi import HTTPException, status

from config import MONGO_CLUSTER_URI, MONGO_DATABASE


TIMESTAMP_KEY = "timestamp"


class MongoDB():
    def __init__(self, uri: str, database: str) -> None:
        try:
            self.client = MongoClient(uri)
            self.db = self.client.get_database(name=database)
        except errors.ConnectionFailure as e:
            raise HTTPException(status=status.HTTP_400_BAD_REQUEST)

    def insert_record(self, collection: str, record: dict | BaseModel) -> None:
        self.db[collection].insert_one(jsonable_encoder(
            record) | {TIMESTAMP_KEY: datetime.utcnow()})

    def update_record(self, collection: str, record: dict | BaseModel, key: str) -> None:
        self.upsert_record_many(collection, jsonable_encoder(record), [key])

    def get_record(self, collection: str, key: str, value: str) -> dict | None:
        return self.db[collection].find_one(filter={key: value}, projection={"_id": False})

    def get_records(self, collection: str, key: str, value: str) -> list[dict]:
        records = list(self.db[collection].find(
            filter={key: value}, projection={"_id": False}))
        return records

    def delete_record(self, collection: str, key: str, value: str) -> None:
        self.db[collection].delete_one(filter={key: value})

    def upsert_record_many(self, collection: str, record: dict | BaseModel, keys: list[str]) -> None:
        record = jsonable_encoder(record)
        if len(set(keys) - set(record.keys())) != 0:
            raise ValueError(
                f"Invalid keys: {list(set(keys) - set(record.keys()))}")
        self.db[collection].update_many(
            filter={key: record[key] for key in keys},
            update={'$set': record | {TIMESTAMP_KEY: datetime.utcnow()}},
            upsert=True
        )


DB = MongoDB(uri=MONGO_CLUSTER_URI, database=MONGO_DATABASE)
