"""
BOLT Agentic AI Controller - Final Enhanced Streamlit Chat UI
This file creates a chat interface for interacting with the BOLT AI agent
with enhanced file viewing capabilities.
"""

import streamlit as st
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import io
import traceback
import glob
import re

# Import our enhanced agent
from bolt_agent import EnhancedBoltAgent

# Set page config
st.set_page_config(
    page_title="BOLT AI Controller",
    page_icon="🤖",
    layout="wide"
)

# Set up session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'agent' not in st.session_state:
    st.session_state.agent = None
    
if 'displayed_files' not in st.session_state:
    st.session_state.displayed_files = {}

# Title
st.title("BOLT AI Controller")

# Function to display a projection file
def display_projection(filepath):
    try:
        # Load and display the projection
        projection = np.load(filepath)
        
        fig, ax = plt.subplots(figsize=(6, 6))
        im = ax.imshow(projection, cmap='viridis')
        plt.colorbar(im, ax=ax)
        
        # Try to extract angle from filename
        try:
            angle_str = filepath.split('projection_')[1].split('deg_')[0]
            ax.set_title(f"Projection at {angle_str}°")
        except:
            ax.set_title(f"Projection")
            
        ax.set_axis_off()
        
        # Convert plot to image
        buf = io.BytesIO()
        plt.tight_layout()
        fig.savefig(buf, format='png')
        buf.seek(0)
        img = Image.open(buf)
        
        # Get caption
        try:
            angle_str = filepath.split('projection_')[1].split('deg_')[0]
            caption = f"Projection at {angle_str}°"
        except:
            caption = f"Projection from {os.path.basename(filepath)}"
        
        return img, caption
    except Exception as e:
        st.warning(f"Could not display projection: {str(e)}")
        return None, None

# Function to find a projection file
def find_projection_file(filename):
    # Check data directory
    data_dir = "tomography_data"
    if os.path.exists(data_dir):
        # Try exact match first
        exact_path = os.path.join(data_dir, filename)
        if os.path.exists(exact_path):
            return exact_path
            
        # Try partial match
        for file in os.listdir(data_dir):
            if filename.lower() in file.lower() and file.endswith('.npy'):
                return os.path.join(data_dir, file)
    
    # Check current directory
    if os.path.exists(filename):
        return filename
    
    # Try to find any projection file if none specified
    if os.path.exists(data_dir):
        npy_files = glob.glob(os.path.join(data_dir, "*.npy"))
        if npy_files:
            return sorted(npy_files)[-1]  # Return the most recent one
    
    return None

# Function to process user input and handle file viewing directly
def process_file_view_request(user_input):
    user_input_lower = user_input.lower().strip()
    
    # Check if this is a file viewing request
    if any(cmd in user_input_lower for cmd in ["show", "display", "view", "see"]):
        if "reconstruction" in user_input_lower or "png" in user_input_lower:
            # Looking for reconstruction.png
            if os.path.exists("reconstruction_result.png"):
                return True, "reconstruction_result.png", "png"
            else:
                return False, "No reconstruction file found", None
        elif "projection" in user_input_lower or "npy" in user_input_lower or "measurement" in user_input_lower:
            # Try to extract a filename
            filename_match = re.search(r'([\w\.-]+\.npy)', user_input)
            if filename_match:
                filename = filename_match.group(1)
                filepath = find_projection_file(filename)
                if filepath:
                    return True, filepath, "npy"
                else:
                    return False, f"Could not find file {filename}", None
            
            # Try to extract an angle
            angle_match = re.search(r'(\d+\.?\d*)\s*(?:deg|degree)', user_input_lower)
            if angle_match:
                angle = float(angle_match.group(1))
                
                # Find a file with that angle
                best_match = None
                smallest_diff = float('inf')
                
                data_dir = "tomography_data"
                if os.path.exists(data_dir):
                    for file in os.listdir(data_dir):
                        if file.endswith('.npy') and 'projection_' in file:
                            try:
                                file_angle = float(file.split('projection_')[1].split('deg_')[0])
                                diff = abs(file_angle - angle)
                                if diff < smallest_diff:
                                    smallest_diff = diff
                                    best_match = os.path.join(data_dir, file)
                            except:
                                continue
                
                if best_match:
                    return True, best_match, "npy"
                else:
                    return False, f"Could not find a projection near {angle} degrees", None
            
            # Check for "last" or "latest"
            if any(word in user_input_lower for word in ["last", "latest", "recent"]):
                data_dir = "tomography_data"
                if os.path.exists(data_dir):
                    npy_files = glob.glob(os.path.join(data_dir, "*.npy"))
                    if npy_files:
                        # Get the most recent file
                        latest_file = max(npy_files, key=os.path.getmtime)
                        return True, latest_file, "npy"
                
                return False, "No projection files found", None
                
        # Check for general file listing
        elif "list" in user_input_lower and "file" in user_input_lower:
            # Just list files, don't show any specific one
            files_info = "Available files:\n"
            
            # Check for NPY files
            data_dir = "tomography_data"
            if os.path.exists(data_dir):
                npy_files = glob.glob(os.path.join(data_dir, "*.npy"))
                if npy_files:
                    files_info += f"\nProjection files ({len(npy_files)}):\n"
                    for i, file in enumerate(sorted(npy_files)):
                        if i < 5:  # Limit to 5 examples
                            angle_str = file.split('projection_')[1].split('deg_')[0] if 'projection_' in file else 'unknown'
                            files_info += f"  - {os.path.basename(file)} (Angle: {angle_str}°)\n"
                        elif i == 5:
                            files_info += f"  - ... and {len(npy_files) - 5} more\n"
                            break
            
            # Check for PNG files
            png_files = glob.glob("*.png")
            if png_files:
                files_info += f"\nReconstruction files ({len(png_files)}):\n"
                for file in sorted(png_files):
                    files_info += f"  - {file}\n"
            
            if files_info == "Available files:\n":
                files_info += "No data files found"
            
            return False, files_info, None
    
    # Not a file viewing request
    return False, None, None

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    
    # Ollama settings
    ollama_model = st.selectbox(
        "Ollama Model",
        options=["llama3", "llama2", "mistral", "mixtral", "gemma"],
        index=0
    )
    
    ollama_url = st.text_input(
        "Ollama URL",
        value="http://localhost:11434"
    )
    
    # Initialize button (no WebSocket URL needed as we're using fixed mock)
    if st.button("Initialize Agent"):
        with st.spinner("Initializing BOLT AI Agent..."):
            try:
                st.session_state.agent = EnhancedBoltAgent(
                    ollama_model=ollama_model,
                    ollama_url=ollama_url
                )
                
                # Create data directory
                os.makedirs("tomography_data", exist_ok=True)
                
                st.success("BOLT AI Agent initialized successfully!")
                
                # Add system message
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "BOLT AI Assistant is ready! I can help you control the beamline, run tomography scans, and analyze data. What would you like to do today?"
                })
            except Exception as e:
                st.error(f"Error initializing agent: {str(e)}")
                st.error(traceback.format_exc())

# Main chat area
st.header("Chat with BOLT AI")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # Regular message
        st.write(message["content"])
        
        # If the message contains a reference to a reconstruction, show the image
        if "reconstruction complete" in message["content"].lower() and os.path.exists("reconstruction_result.png"):
            st.image("reconstruction_result.png", caption="Tomography Reconstruction")
        
        # If the message refers to a projection, try to show it
        if "measurement taken" in message["content"].lower() and "saved to" in message["content"]:
            try:
                # Extract filename from the message
                filepath = message["content"].split("saved to")[-1].strip().split("\n")[0]
                img, caption = display_projection(filepath)
                if img:
                    st.image(img, caption=caption)
            except Exception as e:
                st.warning(f"Could not display image: {str(e)}")

# Chat input
if st.session_state.agent is None:
    st.info("Please initialize the agent using the sidebar controls.")
else:
    if prompt := st.chat_input("What would you like the BOLT AI to do?"):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Check if this is a file viewing request first
        is_file_request, file_result, file_type = process_file_view_request(prompt)
        
        if is_file_request and file_result and file_type:
            # This is a file viewing request with a found file
            if file_type == "npy":
                img, caption = display_projection(file_result)
                if img:
                    response = f"Here's the projection file you requested: {os.path.basename(file_result)}"
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
                        st.image(img, caption=caption)
                else:
                    response = f"I found the file {os.path.basename(file_result)} but couldn't display it."
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    with st.chat_message("assistant"):
                        st.write(response)
            elif file_type == "png":
                response = f"Here's the reconstruction image you requested:"
                st.session_state.messages.append({"role": "assistant", "content": response})
                with st.chat_message("assistant"):
                    st.write(response)
                    st.image(file_result, caption="Tomography Reconstruction")
        elif is_file_request:
            # This is a file request but no file was found
            response = file_result  # This contains the error message
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.write(response)
        else:
            # Regular command - get response from agent
            with st.spinner("BOLT AI Assistant is thinking..."):
                try:
                    response = st.session_state.agent.process_input(prompt)
                except Exception as e:
                    st.error(f"Error processing request: {str(e)}")
                    st.error(traceback.format_exc())
                    response = f"Error processing your request. Please try again."
                
            # Add assistant message to chat
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                # Regular message
                st.write(response)
                
                # If the message contains a reference to a reconstruction, show the image
                if "reconstruction complete" in response.lower() and os.path.exists("reconstruction_result.png"):
                    st.image("reconstruction_result.png", caption="Tomography Reconstruction")
                
                # If the message refers to a projection, try to show it
                if "measurement taken" in response.lower() and "saved to" in response:
                    try:
                        # Extract filename from the response
                        filepath = response.split("saved to")[-1].strip().split("\n")[0]
                        img, caption = display_projection(filepath)
                        if img:
                            st.image(img, caption=caption)
                    except Exception as e:
                        st.warning(f"Could not display image: {str(e)}")

# Add helpful commands guide
with st.sidebar:
    st.markdown("---")
    st.subheader("Command Examples")
    st.markdown("""
    **Move the Sample:**
    - "Move to 45 degrees"
    - "Move by 180 degrees"
    - "Rotate the sample to 90 degrees"
    
    **Take Measurements:**
    - "Take a measurement"
    - "Capture data at current position"
    
    **Run Scans:**
    - "Run tomography scan from 0 to 180 with 10 projections and save it to [desired folder name]"
    - "Perform a scan with 20 projections and save it to [desired folder name]"
    - "Run tomography scan from 0 to 180 with 10 projections"
    - "Perform a scan with 20 projections"
                
    **Reconstruction:**
    - "Reconstruct data from [folder_name]"
    - "Create 3D reconstruction from projections from [folder_name]"
    
    **Information:**
    - "What is the current angle?"
    - "Tell me about the dataset [folder_name]"
    
    **File Display:**
    - "Show me the last measurement"
    - "Display the reconstruction in [folder_name]"
    - "List available files"
    - "List available folders"
    - "Show me file [filename.png]"
    """)

# Footer
st.markdown("---")
st.markdown("BOLT AI Controller - Chat Interface")