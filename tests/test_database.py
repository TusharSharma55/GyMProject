import uuid

from db import DB

from config import (
    GYM_COLLECTION
)

created_collections = DB.db.list_collection_names()

required_collections = GYM_COLLECTION

fake_collection = f"fake_{uuid.uuid4()}"


def test_db_insert_data():
    DB.insert_record(fake_collection, {"f_name": "XYZ", "l_name": "prs"})


def test_db_get_data_after_insert():
    data = DB.get_record(fake_collection, "l_name", "prs")
    assert data, "Failed to get data"
    assert data.get("f_name") == "XYZ", "Fetched data did not match"


def test_db_update_data():
    DB.update_record(fake_collection, {
                     "f_name": "bye", "l_name": "prs"}, "l_name")


def test_db_get_data_after_update():
    data = DB.get_records(fake_collection, "l_name", "prs")
    print("Checking 1: ", data)
    assert data, "Failed to get data"
    matching_records = [
        record for record in data if record.get("f_name") == "bye"]
    assert matching_records, "No record with f_name 'bye' found"
    # assert data.get("f_name") == "bye", "Fetched data did not match"


def test_db_delete_data():
    DB.delete_record(fake_collection, "l_name", "prs")


def test_db_get_data_after_delete():
    data = DB.get_record(fake_collection, "l_name", "prs")
    assert data is None, "Fetched data did not match"


def test_db_delete_collection():
    DB.db.drop_collection(fake_collection)
