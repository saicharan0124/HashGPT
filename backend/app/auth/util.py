from passlib.context import CryptContext
from app.schema.model import UserLoginSchema
from app.database import db_config
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

posts_collection, users_collection = db_config.init_db()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def check_user(data: UserLoginSchema):
    user = users_collection.find_one({"email": data.email})
    if user and verify_password(data.password, user["password"]):
        return True
    return False