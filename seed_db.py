import json
from main import SessionLocal, engine, Base, DBUser, DBProperty, DBBid, Role, get_password_hash

# Refresh database schema
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# 1. Create Test Users
owner = DBUser(
    name="Vikram Joshi (Owner)", 
    role=Role.owner, 
    email="owner@kothrud.com", 
    hashed_password=get_password_hash("password123"),
    is_id_verified=True,
    background_check_passed=True
)

tenant_verified = DBUser(
    name="Neha Kulkarni (Verified Tenant)", 
    role=Role.tenant, 
    email="tenant@kothrud.com", 
    hashed_password=get_password_hash("password123"),
    is_id_verified=True,
    background_check_passed=True
)

tenant_unverified = DBUser(
    name="Rohan Sharma (Unverified Tenant)", 
    role=Role.tenant, 
    email="rohan@kothrud.com", 
    hashed_password=get_password_hash("password123"),
    is_id_verified=False,
    background_check_passed=False
)

db.add_all([owner, tenant_verified, tenant_unverified])
db.commit()

# 2. Add 10 Kothrud Properties
kothrud_properties = [
    DBProperty(owner_id=owner.id, title="Premium 3BHK in Sobha Nesara", description="Luxury high-rise, 1200 sqft carpet, facing NDA hills. Unfurnished with modular kitchen.", area="Chandni Chowk / Kothrud", rent_asking_price=65000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="1BHK near Vanaz Metro Station", description="Ideal for daily commuters. 600 sqft, semi-furnished, 2 mins walk to metro.", area="Paud Road, Kothrud", rent_asking_price=22000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="Spacious 2BHK in Mayur Colony", description="Quiet residential lane, prime locality, 24/7 water supply. Family preferred.", area="Mayur Colony, Kothrud", rent_asking_price=35000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="Fully Furnished 3BHK near MIT-WPU", description="Perfect for students or professors. Includes beds, ACs, and Wi-Fi setup.", area="Rambaug Colony, Kothrud", rent_asking_price=55000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="Compact 1RK for Bachelors", description="Affordable room-kitchen setup. Close to local eateries and grocery stores.", area="Bhusari Colony, Kothrud", rent_asking_price=12000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="Modern 2BHK in Dahanukar Colony", description="Recently renovated, 900 sqft carpet, excellent cross ventilation.", area="Dahanukar Colony, Kothrud", rent_asking_price=30000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="1BHK in Mahatma Society", description="Premium gated community, well-maintained gardens, highly secure.", area="Mahatma Society, Kothrud", rent_asking_price=24000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="2BHK Flat near Karve Statue", description="Walkable distance to central Kothrud amenities. Dedicated bike parking.", area="Karve Road, Kothrud", rent_asking_price=32000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="Studio Apartment Ideal Colony", description="Minimalist studio setup, bachelor friendly, pet friendly.", area="Ideal Colony, Kothrud", rent_asking_price=18000, images=json.dumps([])),
    DBProperty(owner_id=owner.id, title="4BHK Duplex Penthouse", description="Massive terrace, exclusive lift access, servant quarters included.", area="Paud Road, Kothrud", rent_asking_price=80000, images=json.dumps([]))
]

db.add_all(kothrud_properties)
db.commit()
db.close()

print("✅ Database successfully created & seeded!")
print("\n--- Test Credentials ---")
print("1. Property Owner:      owner@kothrud.com  | password123")
print("2. Verified Tenant:     tenant@kothrud.com | password123")
print("3. Unverified Tenant:   rohan@kothrud.com  | password123")