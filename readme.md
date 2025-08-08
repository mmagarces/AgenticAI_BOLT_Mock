# BOLT AI Controller - Enhanced Chat Interface

This project provides an intelligent chat interface for interacting with the BOLT beamline using an AI agent powered by a local Ollama LLM. Control the beamline, run tomography scans, and analyze data through natural language commands with automatic visualization of results.

## Features

- **Pure Natural Language Control**: Interact with the beamline using only conversational commands
- **Automatic Visualization**: Images of projections and reconstructions appear directly in the chat
- **File Browsing Capabilities**: View specific data files with simple commands like "Show me the projection at 45 degrees"
- **Local AI Processing**: Uses Ollama for local language model inference
- **Mock Implementation**: Includes fallback mock devices for testing without hardware

## Setup Instructions

### 1. Install Ollama

First, install Ollama on your system:

```bash
# For Linux
curl -fsSL https://ollama.com/install.sh | sh

# For macOS
brew install ollama
```

For other installation methods, visit: https://ollama.com/download

### 2. Start Ollama and Pull the Model

Start the Ollama service and pull your preferred model:

```bash
ollama serve  # Start the Ollama service
ollama pull llama3  # Pull the llama3 model
```

### 3. Install Python Requirements

```bash
pip install -r requirements.txt
```

### 4. Run the Enhanced Chat Interface

```bash
streamlit run app.py
```

This will start the web server and open the interface in your browser.

## Using the Chat Interface

### Step 1: Initialize the Agent

1. Select your preferred Ollama model from the dropdown in the sidebar
2. Click "Initialize Agent"

### Step 2: Chat with the Agent

Once initialized, you can control the entire system using natural language commands. Here are some examples:

#### Basic Commands

- **Moving the Sample**:
  - "Move to 45 degrees"
  - "Rotate the sample to 90 degrees"

- **Taking Measurements**:
  - "Take a measurement"
  - "Capture data at current position"

- **Running Scans**:
  - "Run tomography scan from 0 to 180 with 10 projections"
  - "Perform a scan with 20 projections"

- **Reconstruction**:
  - "Reconstruct data"
  - "Create 3D reconstruction from projections"

- **Information**:
  - "What is the current angle?"
  - "Tell me about the dataset"

#### File Viewing Commands

- **Viewing Specific Files**:
  - "Show me the projection at 45 degrees"
  - "Display the last measurement"
  - "View the reconstruction"
  - "Show me projection_45.00deg_20250701_125617.npy"

- **File Browsing**:
  - "List available files"
  - "What files do we have?"

### Viewing Results

When the AI takes measurements or performs reconstructions, the images automatically appear in the chat thread under the AI's response. No need to click any buttons to see the results.

## Example Conversation

```
You: Move to 45 degrees
AI: I've moved the sample stage to a rotation angle of 45.0 degrees. The rotation has been successfully completed.

You: Take a measurement
AI: I've taken a measurement at the current position (45.0 degrees). The data has been saved to tomography_data/projection_45.00deg_20250701_125617.npy.
[Image of projection appears here]

You: Run a tomography scan from 0 to 180 with 10 projections
AI: I've completed the tomography scan with 10 projections ranging from 0.0 to 180.0 degrees. All projection data has been saved to the tomography_data directory.

You: Reconstruct the data
AI: Reconstruction complete! I've processed the projection data and created a 3D reconstruction. The results have been saved to reconstruction_result.png.
[Reconstruction image appears here]

You: Show me the projection at 90 degrees
AI: Here's the projection file you requested: projection_90.00deg_20250701_125623.npy
[Image of projection at 90 degrees appears here]
```

## Project Structure

- **final_enhanced_app.py**: Enhanced Streamlit chat interface with file viewing capabilities
- **enhanced_bolt_agent.py**: AI agent implementation with Ollama integration
- **fixed_mock_bolt.py**: Mock implementation for testing without hardware
- **tomography_data/**: Directory where projection data is stored
- **reconstruction_result.png**: Output file for tomography reconstructions

## Customization

- **Ollama Models**: Change the LLM model by selecting a different option in the sidebar
- **Adding New Commands**: Extend the agent's capabilities by modifying the `process_input` method in `enhanced_bolt_agent.py`
- **Mock Data**: Adjust the simulated projections in `fixed_mock_bolt.py` for different test patterns

## Troubleshooting

- **Connection Issues**: If you encounter connection problems, the system will automatically fall back to using mock devices
- **File Viewing Problems**: If a file isn't displaying, try using "List available files" to see what's available
- **LLM Response Issues**: Try using a different Ollama model if responses aren't helpful

## License

This project is provided as open-source software under the MIT License.