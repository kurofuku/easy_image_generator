# frontend/app.py
import streamlit as st
import requests
import base64
import os

# Get environment variables configured in docker-compose
SD_API_HOST = os.getenv("SD_API_HOST")
SD_MODEL_NAME = os.getenv("SD_MODEL_NAME")
DEFAULT_OLLAMA_HOST = os.getenv("DEFAULT_OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "mistral")

# --- 1. Prompt Enhancement Function using Ollama ---
def generate_detailed_prompt(ollama_host: str, ollama_model: str, user_input: str) -> str:
    """Calls the Ollama API to expand user input into a detailed SD prompt."""
    st.info("Expanding prompt using Ollama...")

    prompt_enhancer_payload = {
        "model": ollama_model,
        "prompt": f"User Input: {user_input}",
        "sampler_name": "DPM++ 2M Karras",
        "system": "You are a professional Stable Diffusion prompt engineer. Create a detailed English prompt (approx. 200 words) for high-quality, photorealistic human image generation. Emphasize realism, natural anatomy, and clear facial features. Do not include negative prompts in this output. Always include high-quality keywords like photorealistic, highly detailed, realistic skin texture, natural lighting, masterpiece, best quality, sharp focus. Describe the person's age, gender, hair color, eye color, and action clearly. Output a single English string.",
        "stream": False
    }

    try:
        # Use the externally specified ollama_host
        response = requests.post(f"{ollama_host}/api/generate", json=prompt_enhancer_payload, timeout=120)
        response.raise_for_status()

        # Extract the generated text from Ollama's response
        generated_text = response.json()["response"].strip()
        return generated_text

    except requests.exceptions.RequestException as e:
        st.error(f"Communication error with Ollama server ({ollama_host}). Please check the URL, port, and Ollama status. Error: {e}")
        st.stop()
        return ""


# --- 2. Image Generation Function using Stable Diffusion ---
def generate_image(sd_url: str, sd_model: str, detailed_prompt: str):
    """Calls the Stable Diffusion Web UI API to generate an image."""
    st.info("Generating image using Stable Diffusion API...")

    # JSON payload for Stable Diffusion API (txt2img)
    sd_payload = {
        "prompt": detailed_prompt,
        "negative_prompt": "ugly, deformed, extra limbs, fused fingers, mutated hands, bad anatomy, disfigured, poorly drawn face, bad proportions, extra faces, extra digits, missing limbs, text, watermark, signature",
        "sampler_name": "DPM++ 2M Karras",
        "steps": 30,
        "cfg_scale": 7,
        "width": 768,
        "height": 512,
        "n_iter": 1,
        "batch_size": 1,
        "seed": -1,
        "override_settings": {
            "sd_model_checkpoint": sd_model
        }
    }

    try:
        # SD API runs internally using SD_API_HOST
        response = requests.post(f"{sd_url}/sdapi/v1/txt2img", json=sd_payload, timeout=300)
        response.raise_for_status()

        result = response.json()
        if result and "images" in result and result["images"]:
            return result["images"][0]

        st.error("The response from Stable Diffusion did not contain image data.")
        return None

    except requests.exceptions.RequestException as e:
        st.error(f"Communication error with Stable Diffusion API ({sd_url}). Please check if the API is enabled and the model is loaded. Error: {e}")
        st.stop()
        return None


# --- Streamlit UI Construction ---
st.set_page_config(layout="wide")
st.title("💡 Automated Image Generation System")
st.caption("Brief Input → Ollama Generates Detailed Prompt → Stable Diffusion Generates Image")

# --- Sidebar Configuration for Ollama ---
st.sidebar.header("⚙️ Configuration")
ollama_url = st.sidebar.text_input(
    "Ollama API URL (e.g., http://host:port)",
    DEFAULT_OLLAMA_HOST
)
ollama_model = st.sidebar.text_input(
    "Ollama model (e.g., mistral)",
    OLLAMA_MODEL_NAME
)
sd_url = st.sidebar.text_input(
    "Stable Diffusion API URL (e.g., http://host:port)",
    SD_API_HOST
)
sd_model = st.sidebar.text_input(
    "Stable Diffusion model (e.g., sd_xl_refiner_1.0.safetensors)",
    SD_MODEL_NAME
)

# --- Main Content ---
user_input = st.text_input(
    "Enter a brief description of the image you want to create (e.g., neon street of a future city)",
    "A sleek robot dog sitting in a park with cherry blossoms, realistic"
)

if st.button("Generate Image"):
    if user_input:
        if not ollama_url:
            st.error("Please set the Ollama API URL.")
            st.stop()

        with st.spinner("System processing..."):
            # 1. Prompt Enhancement via Ollama
            detailed_prompt = generate_detailed_prompt(ollama_url, ollama_model, user_input)

            if detailed_prompt:
                st.subheader("Expanded Prompt (for Stable Diffusion)")
                st.code(detailed_prompt, language='text')

                # 2. Image Generation via Stable Diffusion
                base64_img = generate_image(sd_url, sd_model, detailed_prompt)

                # 3. Display Image
                if base64_img:
                    # Decode the Base64 string to image
                    image_bytes = base64.b64decode(base64_img)
                    st.image(image_bytes, caption="Generated Image", use_column_width=True)
                    st.success("Image generation completed successfully!")

