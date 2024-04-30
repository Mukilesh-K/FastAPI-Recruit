from fastapi import FastAPI, Query, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from data_model import Input, GetInsightsInput
from process import ProcessJdResume
from utils import validate_credentials
from Logging import setup_logging

app = FastAPI()

# Initialize logger
logger = setup_logging()

@app.get("/")
def health_check(username: str = Depends(validate_credentials)):
    logger.info("Health check request received.")
    return "Application Health Status Good"


@app.post("/process/")
async def generate_insights(request: Input, background_tasks: BackgroundTasks,
                            username: str = Depends(validate_credentials)):
    try:
        obj = ProcessJdResume()
        obj.run(request)
        background_tasks.add_task(obj.background_processing_tasks)
        logger.info(f"Processing initiated by {username}.")
        return JSONResponse(content={"message": "Processing initiated successfully"})
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.get("/getinsights/")
async def fetch_insights(username: str = Depends(validate_credentials),
                         applicant_id: str = Query(..., description="Applicant ID")):
    try:
        obj = ProcessJdResume()
        status, insights, resume_entities, jd_entities = obj.get_analysed_insights(applicant_id)
        return JSONResponse(content={"status": status, "insights": insights, "resume_relevance": resume_entities,
                                     "job_requirement": jd_entities})
    except Exception as e:
        logger.error(f"Error fetching insights: {str(e)}")
        logger.error("An error occurred:", exc_info=True)
        return JSONResponse(content={"error": str(e)}, status_code=500)
