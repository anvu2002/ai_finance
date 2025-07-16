import sys
from openai import OpenAI
import psycopg2
from typing import List, Dict, Optional
from loguru import logger
from configs.config import OPENAI_API_KEY, DATABASE_URL

class AIAgent:
    def __init__(self,
                 db_name: str = 'ai_finance'):
        # Init OpenAI API and PostgreSQL
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.db_connection = psycopg2.connect(f"{DATABASE_URL}/{db_name}")
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            print(f"[+] DB CONNECTED: {self.db_connection.info.dbname}@{self.db_connection.info.host}")


        self.create_tables()
        
        # Agent configuration
        self.system_prompt = """
        You are a helpful AI assistant. Your responses should be concise, 
        accurate, and helpful. If you don't know something, say so rather 
        than making up information.
        """
    
    def create_tables(self):
        """Ensure required tables exist"""
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    user_message TEXT,
                    agent_response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS agent_knowledge (
                    id SERIAL PRIMARY KEY,
                    key VARCHAR(255) NOT NULL,
                    value TEXT,
                    embedding VECTOR(1536),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.db_connection.commit()
    
    def get_conversation_history(self, session_id: str, limit: int = 5) -> List[Dict]:
        """Retrieve conversation history for context"""
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_message, agent_response 
                FROM conversations 
                WHERE session_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """, (session_id, limit))
            rows = cursor.fetchall()
            history = []
            for user_msg, agent_resp in reversed(rows):
                history.append({"role": "user", "content": user_msg})
                history.append({"role": "assistant", "content": agent_resp})
            return history
    
    def generate_response(self, 
                          user_input: str, 
                          session_id: str) -> str:
        """Generate a response using OpenAI's API with conversation context"""
        # Get conversation history for context
        history = self.get_conversation_history(session_id)
        
        # Prepare messages for OpenAI API
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                store=True,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )            
            
            agent_response = response.choices[0].message.content
            
            # Store the interaction in the database
            self.store_conversation(session_id, user_input, agent_response)
            
            return agent_response
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            sys.exit(1)
    
    def store_conversation(self, session_id: str, user_message: str, agent_response: str):
        """Store a conversation in the database"""
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO conversations (session_id, user_message, agent_response)
                VALUES (%s, %s, %s)
            """, (session_id, user_message, agent_response))
            self.db_connection.commit()
    
    def add_knowledge(self, key: str, value: str):
        """Add knowledge to the agent's database"""
        # First check if the key exists
        with self.db_connection.cursor() as cursor:
            cursor.execute("""
                SELECT id FROM agent_knowledge WHERE key = %s
            """, (key,))
            exists = cursor.fetchone()
            
            if exists:
                # Update existing knowledge
                cursor.execute("""
                    UPDATE agent_knowledge 
                    SET value = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE key = %s
                """, (value, key))
            else:
                # Insert new knowledge
                cursor.execute("""
                    INSERT INTO agent_knowledge (key, value)
                    VALUES (%s, %s)
                """, (key, value))
            self.db_connection.commit()
    
    def query_knowledge(self, query: str, threshold: float = 0.7) -> Optional[str]:
        """Query the agent's knowledge base using vector similarity"""
        # First get the embedding for the query
        try:
            response = openai.Embedding.create(
                input=query,
                model="text-embedding-ada-002"
            )
            query_embedding = response['data'][0]['embedding']
            
            # Query the database for similar knowledge
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT key, value, embedding <=> %s AS similarity
                    FROM agent_knowledge
                    WHERE embedding <=> %s < %s
                    ORDER BY similarity
                    LIMIT 1
                """, (query_embedding, query_embedding, threshold))
                result = cursor.fetchone()
                
                if result:
                    return result[1]  # Return the value
                return None
        except Exception as e:
            print(f"Error querying knowledge: {e}")
            return None
    
    def close(self):
        """Clean up resources"""
        self.db_connection.close()

agent = AIAgent()