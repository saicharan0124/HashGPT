from fastapi import Body, status, HTTPException, APIRouter
from app.schema import model
from app.auth import auth_handler, util
from app.database import db_config

router = APIRouter()
doc_collection, users_collection = db_config.init_db()


@router.post("/signup", tags=["user"])
def create_user(user: model.UserSchema = Body(...)):
    # Check if the email already exists in the database
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        # If the email already exists, raise an HTTPException with a 400 status code
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_dict = user.dict()
    user_dict["password"] = util.get_password_hash(user_dict["password"])
    users_collection.insert_one(user_dict)

    return auth_handler.signJWT(user.email)


@router.post("/login", tags=["user"])
def user_login(user: model.UserLoginSchema = Body(...)):
    if util.check_user(user):
        return auth_handler.signJWT(user.email)
    return {
        "error": "Wrong login details!"
    }
