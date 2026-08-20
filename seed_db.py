import json
from main import SessionLocal, engine, Base, DBUser, DBProperty, DBBid, Role, get_password_hash

# Refresh database schema
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Delete old users and create new ones
db.query(DBUser).delete()
        
tenant = DBUser(email="tenant@kothrud.com", password_hash=get_password_hash("password123"), role=Role.tenant)
owner1 = DBUser(email="owner1@kothrud.com", password_hash=get_password_hash("password123"), role=Role.owner)
owner2 = DBUser(email="owner2@kothrud.com", password_hash=get_password_hash("password123"), role=Role.owner)
        
db.add_all([tenant, owner1, owner2])
db.commit()

# 2. Add 10 Kothrud Properties
properties = [
            DBProperty(
                title="Cozy 1BHK near MIT College",
                description="Perfect for students. Walking distance to campus with fast WiFi.",
                area="Kothrud East",
                listing_type="Rent",
                property_type="Student Home",
                tenant_preference="Students Only",
                image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=500&q=80",
                rent_asking_price=16000,
                sale_price=None,
                owner_id=owner.id
            ),
            DBProperty(
                title="Quiet Ground Floor 2BHK",
                description="No stairs! Peaceful society with a private garden space.",
                area="Kothrud West",
                listing_type="Rent",
                property_type="Full House",
                tenant_preference="Seniors Preferred",
                image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=500&q=80",
                rent_asking_price=22000,
                sale_price=None,
                owner_id=owner.id
            ),
            DBProperty(
                title="Premium 3BHK Penthouse",
                description="Luxury living with a city view. Urgent sale by owner moving abroad.",
                area="Bhusari Colony",
                listing_type="Sale",
                property_type="Full House",
                tenant_preference="Anyone",
                image_url="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=500&q=80",
                rent_asking_price=None,
                sale_price=12500000, # 1.25 Cr
                owner_id=owner.id
            ),
            DBProperty(
                title="Shared PG for IT Professionals",
                description="Fully furnished with daily meals included. Near tech park.",
                area="Bavdhan Border",
                listing_type="Rent",
                property_type="PG",
                tenant_preference="Bachelors",
                image_url="https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=500&q=80",
                rent_asking_price=8500,
                sale_price=None,
                owner_id=owner.id
            )
        ]

db.add_all(properties)
db.commit()
db.close()

print("✅ Database successfully created & seeded!")
print("\n--- Test Credentials ---")
print("1. Property Owner:      owner@kothrud.com  | password123")
print("2. Verified Tenant:     tenant@kothrud.com | password123")
print("3. Unverified Tenant:   rohan@kothrud.com  | password123")
