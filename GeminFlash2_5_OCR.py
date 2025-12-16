import os
from google import genai
from google.genai.errors import APIError
from pathlib import Path
import time
import requests

# --- Configuration and Setup ---

# Set a dummy file name for demonstration. 
# You MUST replace this with a valid path to an actual image file (e.g., a diagram, chart, or photo).
IMAGE_FILE_PATH = "WalmartReceipt.png"
FILE_DISPLAY_NAME = "Diagram for Analysis"
API_KEY = os.getenv("GOOGLE_AI_STUDIO_API_KEY")
MODEL_NAME = "gemini-2.5-flash"

# --- Helper Function for File Creation (if needed) ---
def create_dummy_file(file_path: str):
    """Creates a small, plain text file for demonstration if the image path doesn't exist."""
    if not Path(file_path).exists():
        print(f"⚠️ Warning: File '{file_path}' not found. Creating a dummy text file instead.")
        try:
            # Create a simple file if the target image doesn't exist
            with open(file_path, 'w') as f:
                f.write("This is a simple text file representing a diagram.")
            print(f"Created a dummy text file at {file_path}")
        except IOError as e:
            print(f"Error creating dummy file: {e}")
            raise
    else:
        print(f"✅ Found file: {file_path}")

# --- Main Script Logic ---
def run_gemini_file_workflow():
    """
    Executes the full Gemini File API and Generation workflow.
    """
    
    # 1. Initialize the Client
    try:
        # Client automatically picks up the GEMINI_API_KEY environment variable
        client = genai.Client(api_key=API_KEY)
        print("Client initialized successfully.")
    except Exception as e:
        print(f"❌ Error initializing client. Is GEMINI_API_KEY set? Details: {e}")
        return

    # Check for the file and create a dummy one if it doesn't exist
    create_dummy_file(IMAGE_FILE_PATH)
    
    uploaded_file = None
    try:
        # --- 2. Upload the File using genai.upload_file ---
        print(f"\n🚀 Step 2: Uploading file '{IMAGE_FILE_PATH}'...")
        
        # The upload_file method handles streaming the file to the Google infrastructure
        uploaded_file = client.files.upload(
            file=IMAGE_FILE_PATH
        )
        
        print(f"✅ Upload successful!")
        print(f"   File Name (Resource ID): {uploaded_file.name}")
        print(f"   MIME Type: {uploaded_file.mime_type}")
        
        file_resource_name = uploaded_file.name
        
        # --- 3. Use the Uploaded File in a Generation Request ---
        print("\n🧠 Step 3: Generating content with the uploaded file...")
        
        # Select the desired model
        model = client.models.get(model="gemini-2.5-flash")

        # Construct the prompt with both text and the file object
        model_prompt = [
            "Analyze this file. What key concepts or elements does it contain? "
            "Respond in a detailed, structured list.",
            uploaded_file
        ]

        # Generate the content
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents=model_prompt # Your list of text and file objects
        )

        print("✅ Generation successful!")
        print("\n--- Model Response ---")
        print(response.text)
        print("-----------------------\n")
        
        # --- 4. Retrieve File Metadata using genai.get_file ---
        print(f"🔍 Step 4: Retrieving metadata for file ID '{file_resource_name}'...")
        
        # Retrieve the file object using its resource name
        retrieved_file = client.files.get(name=file_resource_name)
        
        print("✅ Retrieval successful!")
        print(f"   Retrieved File Display Name: {retrieved_file.display_name}")
        print(f"   URI for temporary access: {retrieved_file.uri}")
        print(f"   Creation Time: {retrieved_file.create_time}")

    except APIError as e:
        print(f"❌ An API error occurred during the workflow: {e}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
    finally:
        # --- 5. Clean Up: Delete the File ---
        if uploaded_file:
            print(f"\n🗑️ Step 5: Deleting file '{uploaded_file.name}' for cleanup...")
            try:
                client.files.delete(name=uploaded_file.name)
                print(f"✅ File '{uploaded_file.name}' deleted successfully.")
            except Exception as e:
                print(f"⚠️ Warning: Could not delete file {uploaded_file.name}. Details: {e}")


if __name__ == "__main__":
    run_gemini_file_workflow()