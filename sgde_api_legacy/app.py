from fastapi import FastAPI

# app = FastAPI()

@app.post("/auth/register", response_model=db_schemas.User)
def auth_register(
        user: db_schemas.UserCreate,
        db: Session = Depends(db_app.get_db)
):
    db_user = db_utils.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user = db_utils.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return db_utils.create_user(db, user)


@app.post("/auth/login", response_model=oauth_schemas.Token)
def auth_login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(db_app.get_db)
):
    user = oauth_utils.authenticate_user(db, username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=get_settings().sgde_access_token_expire_minutes)
    access_token = oauth_utils.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/whoami", response_model=db_schemas.User)
async def auth_whoami(
        current_user: db_schemas.User = Depends(oauth_utils.get_current_user)
):
    return current_user


@app.get("/users", response_model=list[db_schemas.User])
async def get_users(
        skip: int = Query(default=0, ge=0),
        limit: int = Query(default=10, le=get_settings().sgde_max_items_from_get),
        db: Session = Depends(db_app.get_db)
):
    users = db_utils.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{username}", response_model=db_schemas.User)
async def get_user(
        username: str,
        db: Session = Depends(db_app.get_db)
):
    db_user = db_utils.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
