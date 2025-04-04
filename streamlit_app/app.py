import streamlit as st
import requests
import base64

st.title("Pokémon Image Generator")
prompt = st.text_input("Enter a prompt for the Pokémon image", "A cartoon drawing of a blue Pokemon with wings and a fiery tail")

# Update this URL to your deployed FastAPI endpoint after deployment
API_URL = "http://localhost:8000/generate-image" 

if st.button("Generate Image"):
    with st.spinner("Generating image..."):
        try:
            response = requests.post(
                API_URL,
                json={"prompt": prompt}
            )
            response.raise_for_status()
            image_data = response.json()["image"]
            
            # Display the image
            st.image(
                f"data:image/png;base64,{image_data}",
                caption=prompt,
                use_container_width=True
            )

            # Convert base64 string back to binary data for download
            image_binary = base64.b64decode(image_data)
            
            # Download button with binary data
            st.download_button(
                label="Download Image",
                data=image_binary,
                file_name="generated_pokemon.png",
                mime="image/png"
            )
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")

st.write("Note: Image generation may take a few seconds.")
