from agent import AIAgent
import uuid

def main():
    # Initialize the agent
    agent = AIAgent()
    
    # Create a session ID (in a real app, this would persist between requests)
    session_id = str(uuid.uuid4())
    print("[+] AI Agent initialized. Type 'quit' to exit.")
    print(f"======================================")
    print(f"--------------- Enjoy ----------------")
    print(f"======================================\n")
    
    while True:
        user_input = input("👨 You: ")
        
        if user_input.lower() == 'quit':
            break
        
        # Get response from the agent
        response = agent.generate_response(user_input, session_id)
        print(f"🌚 Agent: {response}\n")
    
    # Clean up
    agent.close()

if __name__ == "__main__":
    main()