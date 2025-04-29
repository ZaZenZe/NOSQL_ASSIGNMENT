# This script migrates data from a SQLite database to a Neo4j database.
# RUN IT WITH (ON TERMINAL) : python migrate_sqlite_to_neo4j.py
import os
import sqlite3
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()
SQLITE_DB = "social_network.db" 
NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USER = os.environ.get("NEO4J_USER")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def migrate_users(cursor):
    for row in cursor.execute("SELECT id, username, name FROM users"):
        user_id, username, name = row
        with driver.session() as session:
            session.run(
                "CREATE (u:User {id: $id, username: $username, name: $name})",
                id=str(user_id), username=username, name=name
            )

def migrate_posts(cursor):
    for row in cursor.execute("SELECT id, user_id, content, timestamp FROM posts"):
        post_id, user_id, content, timestamp = row
        with driver.session() as session:
            session.run(
                "MATCH (u:User {id: $user_id}) "
                "CREATE (p:Post {id: $id, content: $content, timestamp: datetime($timestamp)}) "
                "MERGE (u)-[:POSTED]->(p)",
                id=str(post_id), user_id=str(user_id), content=content, timestamp=timestamp
            )

def migrate_follows(cursor):
    for row in cursor.execute("SELECT follower_id, followee_id FROM followers"):
        follower_id, followee_id = row
        with driver.session() as session:
            session.run(
                "MATCH (a:User {id: $follower_id}), (b:User {id: $followee_id}) "
                "MERGE (a)-[:FOLLOWS]->(b)",
                follower_id=str(follower_id), followee_id=str(followee_id)
            )

def main():
    conn = sqlite3.connect(SQLITE_DB)
    cursor = conn.cursor()
    print("Migrating users...")
    migrate_users(cursor)
    print("Migrating posts...")
    migrate_posts(cursor)
    print("Migrating follows...")
    migrate_follows(cursor)
    print("Migration complete.")
    conn.close()
    driver.close()

if __name__ == "__main__":
    main()