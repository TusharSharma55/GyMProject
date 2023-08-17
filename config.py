import os
from urllib.parse import quote_plus


# HTTP config
HTTP_PORT = int(os.getenv("HTTP_PORT", 8084))

# JWT config
SECRET_KEY = "8ea3ee0cf4cca600fd7fc8aba3a8cd40484198075c8f2a809f010fbfbad1d25b"
ALGORITHM = "HS256"

# MongoDB config
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "johnwick")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "secret@55")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "gym")
MONGO_HOST = os.getenv("MONGO_HOST", "cluster0.yirlx5n.mongodb.net")

MONGO_AUTH = f"{quote_plus(MONGO_USERNAME)}:{quote_plus(MONGO_PASSWORD)}"
MONGO_CLUSTER_URI = f"mongodb+srv://{MONGO_AUTH}@{MONGO_HOST}"

# Collections
USER_COLLECTION = "user"
GYM_COLLECTION = "gym"