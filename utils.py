import re
import json
import random
import yaml
import ast
import openai
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from database import insert_query, MaayuErrors
from datetime import datetime
from Logging import setup_logging

# Initialize logger
logger = setup_logging()

# Add a basic HTTP authentication
security = HTTPBasic()

def dict_correction(dict_str, api_key):
    try:
        openai.api_key = api_key
        completion = openai.ChatCompletion.create(
            model='gpt-3.5-turbo-1106',
            messages=[
                        {"role": "system", "content": "You are a python programmer, I am going to pass a dictionary which may have syntax errors and may also include some text, I want you to correct it and return only the proper python dictionary"},
                        {"role": "user", "content": dict_str}
                    ],
                    temperature=0.3
                )
        response = completion['choices'][0]['message']['content']
        logger.info(f"Tokens used: {dict(completion)['usage']['total_tokens']}")
        return json.loads(response)
    except Exception as e:
        logger.error(f"Error occurred during dictionary correction: {e}", exc_info=True)
        raise


def extract_dict(input_text, api_key):
    """
    This function is used to parse text to dictionary
    :param input_text: text - raw text
    :return: Success - dictionary object, Failure - None
    """
    try:
        input_text = input_text.replace("None", "'None'").replace("'", '''"''')
        # Define a regular expression to match the entire dictionary
        pattern = r"{[^}]+}"

        # Use re.findall to find all occurrences of the dictionary in the input text
        matches = re.findall(pattern, input_text)

        # If matches are found, you can iterate through them
        for match in matches:
            # response = json.loads(match.replace('None', 'Not Available'))
            response = json.loads(match)
            if len(response) != 0:
                return response
    except Exception as e:
        corrected_dict = dict_correction(match, api_key)
        logger.warning(f"Extracted dictionary contains errors. Corrected version: {corrected_dict}")
        return corrected_dict
    
def score_job_title(job_title_comparison):
    """
    This function is used to generate a score for job title comparison.
    :param job_title_comparison: list - contains job title comparison result and reason
    :return: Dictionary containing the score and analysis
    """
    try:
        if job_title_comparison is not None and isinstance(job_title_comparison, list):
            result = job_title_comparison[0]
            reason = job_title_comparison[1]
            
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            
            # Define scoring based on different match scenarios for job title
            if result.strip().lower() == 'complete match':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'partial match':
                return {'score': random.randint(40, 70), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except Exception as e:
        logger.error(f"Error occurred while scoring job title: {e}", exc_info=True)
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_education(education):
    """
    This function is used to generate education score
    :param education: list - contains score comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if education is not None and isinstance(education, list):
            result = education[0]
            reason = education[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'complete match':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'partial match':
                return {'score': random.randint(40, 70), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}


def score_years_of_experience(years_of_experience):
    """
    This function is used to generate years_of_experience score
    :param years_of_experience: list - contains experience level comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """

    try:
        if years_of_experience is not None and isinstance(years_of_experience, list):
            result = years_of_experience[0]
            reason = years_of_experience[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'qualified':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'not qualified':
                return {'score': random.randint(10, 20), 'analysis': reason}
            if result.strip().lower() == 'could be considered':
                return {'score': random.randint(40, 60), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}


def score_technical_skills(technical_skills):
    """
    This function is used to generate technical_skills score
    :param technical_skills: list - contains technical skills comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if technical_skills is not None and isinstance(technical_skills, list):
            result = technical_skills[0]
            reason = technical_skills[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if 'complete match' in result.strip().lower():
                return {'score': random.randint(85, 100), 'analysis': reason}
            if 'partial match' in result.strip().lower():
                return {'score': random.randint(60, 70), 'analysis': reason}
            if 'poor match' in result.strip().lower():
                return {'score': random.randint(20, 30), 'analysis': reason}
            if 'not matching' in result.strip().lower():
                return {'score': random.randint(10, 15), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

   
def score_work_authorization(work_authorization):
    """
    This function is used to generate work_authorization score
    :param work_authorization: list - contains work authorization comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if work_authorization is not None and isinstance(work_authorization, list):
            result = work_authorization[0]
            reason = work_authorization[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'authorized':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'not authorized':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}


def score_employment_type(employment_type):
    """
    This function is used to generate employment_type score
    :param employment_type: list - contains employment type comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if employment_type is not None and isinstance(employment_type, list):
            result = employment_type[0]
            reason = employment_type[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'matching':
                return {'score': random.randint(90, 100), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}
    
def score_location(location):
    """
    This function is used to generate a score for location comparison
    :param location: list - contains location comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if location is not None and isinstance(location, list):
            result = location[0]
            reason = location[1]
            if result.strip().lower() == 'information not available' or result.strip().lower() == 'job location not mentioned':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            if result.strip().lower() == 'matching':
                return {'score': random.randint(80, 90), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except Exception as e:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_domain_expertise(domain_expertise):
    """
    This function is used to generate a domain expertise score
    :param domain_expertise: list - contains domain expertise comparison result and reason
    :return: Dictionary containing the score and analysis
    """
    try:
        if domain_expertise is not None and isinstance(domain_expertise, list):
            result = domain_expertise[0]
            reason = domain_expertise[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'complete match':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'partial match':
                return {'score': random.randint(40, 70), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except Exception as e:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_salary_expectation(salary_expectation):
    """
    Used to generate salary expectation score
    :param salary_expectation: list - contains salary expectation comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if salary_expectation is not None and isinstance(salary_expectation, list):
            result = salary_expectation[0]
            reason = salary_expectation[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'matching':
                return {'score': random.randint(90, 100), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(30, 40), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}


def score_roles_and_responsibilities(roles_and_responsibilities):
    """
    Used to generate salary expectation score
    :param roles_and_responsibilities: list - contains roles and responsibilities comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """    
    try:
        if roles_and_responsibilities is not None and isinstance(roles_and_responsibilities, list):
            result = roles_and_responsibilities[0]
            reason = roles_and_responsibilities[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'Complete Match':
                return {'score': random.randint(80, 90), 'analysis': reason}
            if result.strip().lower() == 'Partial Match':
                return {'score': random.randint(40, 45), 'analysis': reason}
            else:
                return {'score': random.randint(5, 10), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_cultural_fit(cultural_fit):
    """
    This function is used to generate the cultural fit score
    :param cultural_fit: list - contains cultural fit comparison result and reason
    :return: Success/Failure - dictionary containing score and analysis
    """
    try:
        if cultural_fit is not None and isinstance(cultural_fit, list):
            result = cultural_fit[0]
            reason = cultural_fit[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if 'complete match' in result.strip().lower():
                return {'score': random.randint(85, 100), 'analysis': reason}
            if 'partial match' in result.strip().lower():
                return {'score': random.randint(60, 70), 'analysis': reason}
            if 'poor match' in result.strip().lower():
                return {'score': random.randint(20, 30), 'analysis': reason}
            if 'not matching' in result.strip().lower():
                return {'score': random.randint(10, 15), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_experience_in_similar_companies(exp_in_similar_companies):
    """
    This function generates the score for 'Experience in Similar Companies'.
    :param exp_in_similar_companies: list - contains comparison result and reason for experience in similar companies
    :return: Dictionary containing the score and analysis
    """
    try:
        if exp_in_similar_companies is not None and isinstance(exp_in_similar_companies, list):
            result = exp_in_similar_companies[0]
            reason = exp_in_similar_companies[1]
            
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            
            # Define scoring based on different match scenarios
            if result.strip().lower() == 'matching':
                return {'score': random.randint(80, 100), 'analysis': reason}
            if result.strip().lower() == 'not match':
                return {'score': random.randint(10, 25), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except Exception as e:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def score_certifications_and_licenses(certifications_and_licenses):
    """
    This function is used to generate the score for certifications and licenses comparison
    :param certifications_and_licenses: list - contains certifications and licenses comparison result and reason
    :return: Dictionary containing the score and analysis
    """
    try:
        if certifications_and_licenses is not None and isinstance(certifications_and_licenses, list) and len(certifications_and_licenses) >= 2:
            result = certifications_and_licenses[0]
            reason = certifications_and_licenses[1]
            if result.strip().lower() == 'information not available':
                return {'score': 'Information Not Available', 'analysis': reason}
            if result.strip().lower() == 'complete match':
                return {'score': random.randint(85, 100), 'analysis': reason}
            if result.strip().lower() == 'partial match':
                return {'score': random.randint(40, 70), 'analysis': reason}
            if result.strip().lower() == 'not matching':
                return {'score': random.randint(10, 20), 'analysis': reason}
            else:
                return {'score': random.randint(0, 5), 'analysis': reason}
        else:
            return {'score': random.randint(0, 5), 'analysis': 'Information Not Clearly Specified'}
    except Exception as e:
        return {'score': 'Information Not Clearly Specified', 'analysis': 'Information Not Clearly Specified'}

def calculate_maayu_score(scored_analysis):
    """
    This function is used to calculate the final maayu score
    :param scored_analysis: dictionary - containing keys and list for each of the keys
    :return: integer - maayu score
    """
    try:
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            weight_dict = config.get('weights')
            numerator = 0
            denominator = 0

            for field in scored_analysis:
                if scored_analysis[field]['score'] not in ['Information Not Clearly Specified',
                                                        'Information Not Available'] and weight_dict.get(field) is not None:
                    numerator = numerator + (scored_analysis[field]['score'] * weight_dict[field])
                    denominator = denominator + weight_dict[field]

            maayu_score = numerator // denominator
            return maayu_score
    except Exception as e:
        logger.error(f"Error occurred while calculating Maayu score: {e}", exc_info=True)

    # FinalScore = ((Score1 * Weight1) + (Score2 * Weight2) + (Score3 * Weight3) + (Score4 * Weight4)) / (
    #             Weight1 + Weight2 + Weight3 + Weight4)
    # print(FinalScore)


def validate_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    This function is used to validate the API credentials
    :param credentials: object - containing username, password
    :return: On Success - dict, On Failure - HTTP Exception
    """
    try:
        # encode the credentials to compare
        input_user_name = credentials.username.encode("utf-8")
        input_password = credentials.password.encode("utf-8")

        stored_username = b'maayu'
        stored_password = b'maayu@123'

        if input_user_name == stored_username and input_password == stored_password:
            return {"auth message": "authentication successful"}

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Basic"})
    except Exception as e:
        logger.error(f"Error occured during valdation: {e}", exc_info=True)
        raise


def prepare_insights_for_db(maayu_score, maayu_feedback, positive_feedback):
    """
    This function is used to the format the analysis result to be stored in DB
    :param maayu_score: str - Maayu generated score
    :param maayu_feedback: dict - contains all generated insights
    :param positive_feedback: string - Positive feedback if applicable
    :return: dict - prepared response as dictionary
    """
    try:
        analysis_dict = {"maayu_score": maayu_score,
                        "maayu_feedback": maayu_feedback,
                        "positive_feedback": positive_feedback}
        return analysis_dict
    except Exception as e:
        logger.error(f"Error occured while preparing insights for DB: {e}", exc_info=True)


def write_error_to_db(error, applicant_id=None):
    """
    This function is used to write error into the error table in DB
    :param error: str - Error
    :param applicant_id: str - Applicant ID
    :return: None
    """
    try:
        insert_query(MaayuErrors, [{"applicant_id": applicant_id, "error": error, "timestamp": datetime.now()}])
    except Exception as e:
        logger.error(f"Error occurred while writing error to DB: {e}", exc_info=True)


def filter_req_ui_col(resume_dict_string, jd_dict_string, insights_dict_string):
    """
    This function is used to filter only the required column needed in UI
    These required columns are configured in config.yaml
    :param resume_dict_string: str - resume entity string
    :param jd_dict_string: str - jd entity string
    :param insights_dict_string: str - insight dict string
    :return: resume, jd, insights after removing undesired columns
    """
    try:
        with open("config.yaml", 'r') as stream:
            config = yaml.safe_load(stream)
            ui_display_config = config.get('ui_display', {})
            resume_ui = ui_display_config.get('resume')
            jd_ui = ui_display_config.get('jd')
            insights_ui = ui_display_config.get('insights')
            maayu_feedback_ui = ui_display_config.get('maayu_feedback')

        insights_dict = ast.literal_eval(insights_dict_string)
        jd_dict = ast.literal_eval(jd_dict_string)
        resume_dict = ast.literal_eval(resume_dict_string)

        resume = str({key: value for key, value in resume_dict.items() if key in resume_ui})
        jd = str({key: value for key, value in jd_dict.items() if key in jd_ui})
        insights = {key: value for key, value in insights_dict.items() if key in insights_ui}
        if insights.get('maayu_feedback') is not None:
            maayu_feedback_dict = insights.get('maayu_feedback')
            maayu_feedback = {key: value for key, value in maayu_feedback_dict.items() if key in maayu_feedback_ui}
            # Temporary
            # maayu_feedback['certifications_and_licenses'] = 'Not Processed'
            insights['maayu_feedback'] = maayu_feedback

        return resume, jd, str(insights)

    except Exception as e:
        logger.error(f"Error occurred while filtering data for UI: {e}", exc_info=True)
        write_error_to_db(f"Error while filtering data needed for UI - {e}")
        return None, None, None
    