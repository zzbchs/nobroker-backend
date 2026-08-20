import json
from main import SessionLocal, engine, Base, DBUser, DBProperty, DBBid, Role, get_password_hash

# Refresh database schema
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Delete old users and create new ones
db.query(DBUser).delete()
        
tenant = DBUser(email="tenant@kothrud.com", hashed_password=get_password_hash("password123"), role=Role.tenant)
owner1 = DBUser(email="owner1@kothrud.com", hashed_password=get_password_hash("password123"), role=Role.owner)
owner2 = DBUser(email="owner2@kothrud.com", hashed_password=get_password_hash("password123"), role=Role.owner)
        
db.add_all([tenant, owner1, owner2])
db.commit()

# Add 6 Detailed Kothrud Properties with Multimedia
properties = [
            DBProperty(
                title="3 BHK Flat for rent in Kothrud, Pune",
                description="Vilas Yashwin Orizzonte. Beautiful city views.",
                area="Kothrud East",
                listing_type="Rent",
                property_type="Full House",
                tenant_preference="Anyone",
                image_url="https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80",
                video_url="https://www.w3schools.com/html/mov_bbb.mp4", # Dummy Video!
                image_gallery="https://images.unsplash.com/photo-1502672260266-1c1e39b4980a?w=200,https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=200",
                rent_asking_price=55000,
                sale_price=None,
                sqft=1200,
                furnishing="Fully furnished",
                highlights="Power Backup • Gymnasium • Club House • Swimming Pool",
                owner_id=owner1.id
            ),
            DBProperty(
                title="2 BHK Flat for sale in Bavdhan",
                description="Peaceful society with private garden.",
                area="Bavdhan",
                listing_type="Sale",
                property_type="Full House",
                tenant_preference="Families",
                image_url="https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=600&q=80",
                video_url=None,
                image_gallery="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=200",
                rent_asking_price=None,
                sale_price=8500000,
                sqft=950,
                furnishing="Semi furnished",
                highlights="Park • Security • Elevator • Vastu Compliant",
                owner_id=owner1.id
            ),
            DBProperty(
                title="Premium 4 BHK Penthouse",
                description="Luxury living with top-tier amenities.",
                area="Bhusari Colony",
                listing_type="Sale",
                property_type="Full House",
                tenant_preference="Anyone",
                image_url="https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=600&q=80",
                video_url=None,
                image_gallery=None,
                rent_asking_price=None,
                sale_price=15000000,
                sqft=2200,
                furnishing="Unfurnished",
                highlights="Private Terrace • Smart Home • 2 Car Parking",
                owner_id=owner2.id
            ),
            DBProperty(
                title="Shared PG for IT Professionals",
                description="Daily meals and high-speed internet included.",
                area="Hinjewadi Border",
                listing_type="Rent",
                property_type="PG",
                tenant_preference="Bachelors",
                image_url="https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=600&q=80",
                video_url=None,
                image_gallery=None,
                rent_asking_price=8500,
                sale_price=None,
                sqft=300,
                furnishing="Fully furnished",
                highlights="WiFi • AC • Housekeeping • Meals",
                owner_id=owner2.id
            ),
            DBProperty(
                title="1 BHK Cozy Apartment for rent",
                description="Walking distance to MIT college.",
                area="Rambaug Colony",
                listing_type="Rent",
                property_type="Student Home",
                tenant_preference="Students Only",
                image_url="https://images.unsplash.com/photo-1502672260266-1c1e39b4980a?w=600&q=80",
                video_url=None,
                image_gallery=None,
                rent_asking_price=16000,
                sale_price=None,
                sqft=550,
                furnishing="Semi furnished",
                highlights="Close to Campus • Library • Cafeteria",
                owner_id=owner1.id
            ),
            DBProperty(
                title="Independent Villa for Sale",
                description="Spacious historical home in prime location.",
                area="Ideal Colony",
                listing_type="Sale",
                property_type="Full House",
                tenant_preference="Anyone",
                image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=600&q=80",
                video_url=None,
                image_gallery=None,
                rent_asking_price=None,
                sale_price=22000000,
                sqft=3500,
                furnishing="Unfurnished",
                highlights="Servant Quarters • Private Lawn • Corner Plot",
                owner_id=owner2.id
            )
        ]

db.add_all(properties)
db.commit()
db.close()

print("✅ Database successfully created & seeded!")
print("\n--- Test Credentials ---")
print("1. Property Owner 1:    owner1@kothrud.com | password123")
print("2. Property Owner 2:    owner2@kothrud.com | password123")
print("3. Verified Tenant:     tenant@kothrud.com | password123")
