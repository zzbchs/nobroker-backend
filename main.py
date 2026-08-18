import os
import json
import shutil
from datetime import datetime, timedelta
from typing import List
from enum import Enum as PyEnum

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict

from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from jose import JWTError, jwt
import bcrypt

# --- 1. LOCAL STORAGE SETUP ---
UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- 2. DATABASE CONFIGURATION ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./nobroker_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- 3. ENUMS & SQL MODELS ---
class Role(str, PyEnum):
    owner = "owner"
    tenant = "tenant"

class BidStatus(str, PyEnum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"

class DBUser(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    role = Column(SQLEnum(Role))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_id_verified = Column(Boolean, default=False)
    background_check_passed = Column(Boolean, default=False)

class DBProperty(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    area = Column(String)
    rent_asking_price = Column(Integer)
    images = Column(String)  # JSON-encoded array of image URLs

class DBBid(Base):
    __tablename__ = "bids"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"))
    tenant_id = Column(Integer, ForeignKey("users.id"))
    bid_amount = Column(Integer)
    status = Column(SQLEnum(BidStatus), default=BidStatus.pending)

Base.metadata.create_all(bind=engine)

# --- 4. SCHEMAS (Pydantic V2) & JWT CONFIG ---
SECRET_KEY = "kothrud-app-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class UserSchema(BaseModel):
    id: int
    name: str
    role: Role
    email: str
    is_id_verified: bool
    background_check_passed: bool
    
    model_config = ConfigDict(from_attributes=True)

class PropertySchema(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    area: str
    rent_asking_price: int
    images: str
    
    model_config = ConfigDict(from_attributes=True)

class BidSchema(BaseModel):
    id: int
    property_id: int
    tenant_id: int
    bid_amount: int
    status: BidStatus
    
    model_config = ConfigDict(from_attributes=True)

# --- 5. NATIVE BCRYPT & JWT UTILITIES ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies plain password against stored hash using bcrypt directly."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hashes password using native bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except (JWTError, ValueError):
        raise credentials_exception
        
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- 6. FASTAPI APP & ENDPOINTS ---
app = FastAPI(title="NoBroker Clone API - Kothrud Edition")

# Serve uploaded static photos locally at /static/...
app.mount("/static", StaticFiles(directory=UPLOAD_DIR), name="static")

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Logs in an Owner or Tenant and returns a JWT access token."""
    user = db.query(DBUser).filter(DBUser.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/properties", response_model=List[PropertySchema])
def get_properties(db: Session = Depends(get_db)):
    """Public property listings feed."""
    return db.query(DBProperty).all()

@app.get("/users/{user_id}/profile", response_model=UserSchema)
def view_user_profile(user_id: int, db: Session = Depends(get_db)):
    """Owner can view tenant profile & background check status."""
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/bids", response_model=BidSchema)
def create_bid(
    property_id: int, 
    bid_amount: int, 
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Tenant places a bid on a property."""
    if current_user.role != Role.tenant:
        raise HTTPException(status_code=403, detail="Only tenants can make a bid")
    if not current_user.is_id_verified or not current_user.background_check_passed:
        raise HTTPException(status_code=403, detail="Tenant must pass ID verification and background check to bid")

    property_exists = db.query(DBProperty).filter(DBProperty.id == property_id).first()
    if not property_exists:
        raise HTTPException(status_code=404, detail="Property not found")

    new_bid = DBBid(property_id=property_id, tenant_id=current_user.id, bid_amount=bid_amount)
    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)
    return new_bid

@app.put("/bids/{bid_id}/review", response_model=BidSchema)
def review_bid(
    bid_id: int, 
    action: BidStatus, 
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Owner approves or rejects a bid."""
    if current_user.role != Role.owner:
        raise HTTPException(status_code=403, detail="Only property owners can review bids")
        
    bid = db.query(DBBid).filter(DBBid.id == bid_id).first()
    if not bid:
        raise HTTPException(status_code=404, detail="Bid not found")

    property_item = db.query(DBProperty).filter(DBProperty.id == bid.property_id).first()
    if property_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only review bids for your own properties")

    bid.status = action
    db.commit()
    db.refresh(bid)
    
    if action == BidStatus.approved:
        print(f"✅ Triggering Rent Agreement Generation for Property '{property_item.title}' and Tenant ID {bid.tenant_id}")

    return bid

@app.post("/properties/{property_id}/upload-image")
def upload_property_image(
    property_id: int, 
    file: UploadFile = File(...), 
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Saves property image locally and attaches static URL to database record."""
    if current_user.role != Role.owner:
        raise HTTPException(status_code=403, detail="Only owners can upload images")
        
    property_item = db.query(DBProperty).filter(DBProperty.id == property_id).first()
    if not property_item:
        raise HTTPException(status_code=404, detail="Property not found")
    if property_item.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only upload images for your own properties")

    clean_filename = file.filename.replace(" ", "_")
    file_path = os.path.join(UPLOAD_DIR, f"prop_{property_id}_{clean_filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/static/prop_{property_id}_{clean_filename}"
    
    existing_images = json.loads(property_item.images) if property_item.images else []
    existing_images.append(image_url)
    property_item.images = json.dumps(existing_images)
    
    db.commit()
    db.refresh(property_item)
    
    return {"message": "Image saved successfully!", "image_url": image_url, "all_images": existing_images}