from google.genai import Client, types
import os
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "")
location = os.getenv("GOOGLE_CLOUD_LOCATION", "")

def check_token_count(file_bytes, mime_type, model_name="gemini-2.5-pro"):
    """
    Dry-run to see how many tokens a file will consume.
    """
    # 1. Initialize Client
    client = Client(
        vertexai=True, 
        project=project_id, 
        location=location
    )

    # 2. Create the Part (Exactly how your agent does it)
    file_part = types.Part(
        inline_data=types.Blob(
            data=file_bytes, 
            mime_type=mime_type
        )
    )

    # 3. Ask the API to count it
    print(f"☁️  Asking Vertex AI to count tokens for {mime_type}...")
    try:
        response = client.models.count_tokens(
            model=model_name,
            contents=[types.Content(role="user", parts=[file_part])]
        )
        
        count = response.total_tokens
        limit = 1048576 # 1M Limit for 2.5 Pro (check your specific model)
        
        print(f"📊 Token Count: {count:,}")
        
        if count > limit:
            print(f"❌ CRITICAL: This file is {count/limit:.1%} of the limit! It will crash.")
        else:
            print(f"✅ Safe: This file uses {count/limit:.1%} of the context window.")
            
        return count

    except Exception as e:
        print(f"Error counting tokens: {e}")
        return 0

# --- Usage Example ---
print("assets/pid_sample_1.pdf")
with open("assets/pid_sample_1.pdf", "rb") as f:
   pdf_bytes = f.read()
   check_token_count(pdf_bytes, "application/pdf")

print("\n\nassets/learning_course.pdf")
with open("assets/learning_course.pdf", "rb") as f:
   pdf_bytes = f.read()
   check_token_count(pdf_bytes, "application/pdf")