# FastAPI

## Key Features:
Resume Parsing: Extracts relevant information from resumes, including job titles, education, experience, and skills.                                                       
Job Description Analysis: Evaluates job descriptions to identify key requirements and qualifications.                                                                  
Scoring System: Generates scores for different criteria, such as job title match, education level, years of experience, technical skills, and more.                
Insightful Feedback: Provides detailed analysis and feedback on each aspect of the candidate's profile.                                                          
Customizable Configuration: Allows customization of scoring weights and displayed information for tailored recruitment processes.                                      
FastAPI Web Application: Offers a user-friendly web interface for interacting with the application and viewing assessment results.

## Dependencies:
Python Libraries:
FastAPI: For building the web application and API endpoints.
OpenAI: Provides access to the GPT-3 language model for text analysis and completion.
PyYAML: Handles YAML configuration files for customizable settings.
External Services:
OpenAI GPT-3 API (Optional): Utilizes the powerful GPT-3 model for natural language processing tasks.

## Usage:
Installation:
Clone the repository: git clone https://github.com/your_username/Repo_name.git
Install Python dependencies: pip install -r requirements.txt
(Optional) Set up OpenAI API credentials.
Start the FastAPI application:

Run:
## Execution command
## uvicorn main:app --reload 
to start the web server.
Access the application at http://localhost:8000 in your web browser or via API requests.

## Configuration:
Customize scoring weights and UI display settings in the config.yaml file.

## Contributing:
Fork the repository.
Create a new branch for your feature or bug fix.
Make your changes and commit them with descriptive messages.
Push your changes to your fork.
Submit a pull request to the main repository.

