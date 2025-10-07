<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
- [x] Verify that the copilot-instructions.md file in the .github directory is created. ✓ COMPLETED

- [x] Clarify Project Requirements ✓ COMPLETED
	<!-- Real-time inference with Apache Kafka, FastAPI, Docker, Python -->

- [x] Scaffold the Project ✓ COMPLETED
	<!--
	Ensure that the previous step has been marked as completed.
	Call project setup tool with projectType parameter.
	Run scaffolding command to create project files and folders.
	Use '.' as the working directory.
	If no appropriate projectType is available, search documentation using available tools.
	Otherwise, create the project structure manually using available file creation tools.
	-->

- [x] Customize the Project ✓ COMPLETED
	<!-- 
	Created complete real-time inference project with:
	- FastAPI REST API for ML predictions
	- ML model handler with sample RandomForest classifier  
	- Kafka producer/consumer for streaming data
	- Docker containerization setup
	- Configuration management with Pydantic settings
	-->

- [x] Install Required Extensions ✓ COMPLETED
	<!-- No additional extensions required beyond Python environment -->

- [x] Compile the Project ✓ COMPLETED
	<!--
	Python virtual environment configured successfully
	All dependencies installed: fastapi, uvicorn, kafka-python, scikit-learn, pandas, numpy, joblib, pydantic, loguru
	Sample ML model created and tested
	API service tested and working
	-->

- [x] Create and Run Task ✓ COMPLETED
	<!-- Created VS Code task "Start ML Inference API" that launches the FastAPI server -->

- [ ] Launch the Project
	<!--
	Verify that all previous steps have been completed.
	Prompt user for debug mode, launch only if confirmed.
	 -->

- [ ] Ensure Documentation is Complete
	<!--
	Verify that all previous steps have been completed.
	Verify that README.md and the copilot-instructions.md file in the .github directory exists and contains current project information.
	Clean up the copilot-instructions.md file in the .github directory by removing all HTML comments.
	 -->