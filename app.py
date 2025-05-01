from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from datetime import datetime

app = FastAPI()

# Database connection parameters
DB_HOST = "ep-royal-cloud-a1ncyyrd-pooler.ap-southeast-1.aws.neon.tech"
DB_NAME = "gigilio"
DB_USER = "gigilio_owner"
DB_PASS = "npg_akcnZJGf69Ie"
DB_SSL = "require"

# Pydantic model for request validation
class UserStatus(BaseModel):
    userId: str
    function: str
    timestamp: str

# Initialize database
def init_db():
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS, sslmode=DB_SSL
    )
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_status (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR(255) NOT NULL,
            function VARCHAR(255) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn, cursor

@app.post("/user-status")
async def post_user_status(status: UserStatus):
    try:
        # Validate timestamp
        datetime.fromisoformat(status.timestamp.replace('Z', '+00:00'))
        
        # Connect to database
        conn, cursor = init_db()
        try:
            cursor.execute(
                """
                INSERT INTO user_status (user_id, function, timestamp)
                VALUES (%s, %s, %s)
                """,
                (status.userId, status.function, status.timestamp)
            )
            conn.commit()
            return {
                "status": "success",
                "received": status.dict()
            }
        finally:
            cursor.close()
            conn.close()
    except ValueError:
        raise HTTPException(status_code=400, detail="Định dạng timestamp không hợp lệ")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi server: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)