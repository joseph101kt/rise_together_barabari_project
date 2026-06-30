from app.core.database import Base, engine

# Register all models
import app.models

Base.metadata.create_all(bind=engine)

print("Tables created successfully")