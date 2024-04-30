import openai
import yaml
from retrying import retry
from datetime import datetime
from database import MaayuInsights, create_tables, insert_query, select_query, update_query
from sqlalchemy import select, update
from fastapi import BackgroundTasks
from utils import (extract_dict, score_education, score_employment_type, score_work_authorization,
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          score_technical_skills, score_years_of_experience, score_domain_expertise, calculate_maayu_score, prepare_insights_for_db,
                   write_error_to_db, filter_req_ui_col, score_salary_expectation, score_roles_and_responsibilities, score_location, 
                   score_experience_in_similar_companies, score_cultural_fit, score_certifications_and_licenses, score_job_title)
import logging
from Logging import setup_logging

# Initialize logger
logger = setup_logging()

class ProcessJdResume:
    def __init__(self):
        try:
            with open('config.yaml', 'r') as file:
                config = yaml.safe_load(file)

                self.api_key = config['open_ai']['api_key']
                self.model_name = config['open_ai']['model_name']
                self.entity_extraction_temperature = config['open_ai']['entity_extraction_temperature']
                self.feedback_temperature = config['open_ai']['feedback_temperature']
                self.analysis_temperature = config['open_ai']['analysis_temperature']
                self.resume_header = config['prompts']['resume_header']
                self.resume_entity_extraction_prompt = config['prompts']['resume_entity_extraction_prompt']
                self.job_description_header = config['prompts']['job_description_header']
                self.job_description_entity_extraction_prompt = config['prompts'][
                    'job_description_entity_extraction_prompt']
                self.comparison_header = config['prompts']['comparison_header']
                self.comparison_analysis_prompt = config['prompts']['comparison_analysis_prompt']
                self.technical_skill_header = config['prompts']['technical_skill_header']
                self.technical_skill_prompt = config['prompts']['technical_skill_prompt']
                self.positive_highlight_header = config['prompts']['positive_highlight_header']
                self.positive_highlights_prompt = config['prompts']['positive_highlights_prompt']
                self.work_eligibility = config['work_eligibility']
                self.tables = config['tables']
        except Exception as e:
                logger.error(f"Error initializing ProcessJdResume: {e}", exc_info=True)
                raise

    @retry(stop_max_attempt_number=3)
    def process_resume(self, resume):
        """
        This function is used to analyze and extract entities from the input resume
        :return resume_entities: dictionary - extracted resume entities
        """
        try:
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.resume_header},
                    {"role": "user", "content": self.resume_entity_extraction_prompt % (resume)}
                ],
                temperature=self.entity_extraction_temperature
            )
            resume_entities = extract_dict(completion['choices'][0]['message']['content'], self.api_key)
            print("TOKENS USED ====> ", dict(completion)['usage']['total_tokens'])
            # print(resume_entities)
            logger.info("Resume processed successfully.")
            return resume_entities
        except Exception as error:
            logger.error(f"Error processing resume: {error}", exc_info=True)
            raise

    @retry(stop_max_attempt_number=3)
    def process_job_description(self, job_description):
        """
        This function is used to analyze and extract from the input job description
        :param job_description - string - job description input
        :return jd_entities - dictionary - extracted jd entities
        """
        try:
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.job_description_header},
                    {"role": "user", "content": self.job_description_entity_extraction_prompt % job_description}
                ],
                temperature=self.entity_extraction_temperature
            )
            jd_entities = extract_dict(completion['choices'][0]['message']['content'], self.api_key)
            print("TOKENS USED ====> ", dict(completion)['usage']['total_tokens'])
            # print(jd_entities)
            logger.info("Job description processed successfully.")
            return jd_entities
        except Exception as error:
            logger.error(f"Error processing job description: {error}", exc_info=True)
            raise

    @retry(stop_max_attempt_number=3)
    def compare_jd_resume(self, jd_entities, resume_entities):
        """
        This function is used to compare the resume entities and job description entities
        :param jd_entities: dictionary - Extracted job description entities
        :param resume_entities: dictionary - Extracted resume entities
        :return comparison_analysis: dictionary
        """
        try:
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.comparison_header},
                    {"role": "user", "content": self.comparison_analysis_prompt % (jd_entities, resume_entities)}
                ],
                temperature=self.analysis_temperature
            )
            comparison_analysis = extract_dict(completion['choices'][0]['message']['content'], self.api_key)
            print("TOKENS USED ====> ", dict(completion)['usage']['total_tokens'])
            # print(comparison_analysis)
            logger.info("Resume and job description compared successfully.")
            return comparison_analysis
        except Exception as error:
            logger.error(f"Error comparing resume and job description: {error}", exc_info=True)
            raise

    @retry(stop_max_attempt_number=3)
    def generate_technical_skills_match(self, jd_entities, comparison_analysis):
        """
        Used to compare technical skills extracted from resume and jd
        :param jd_entities: dict - extracted entities from JD
        :param comparison_analysis: dict - all analysed results
        :return: Success - comparison_analysis - dict, Failure - raise exception
        """
        try:
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.technical_skill_header},
                    {"role": "user",
                     "content": self.technical_skill_prompt % (jd_entities.get('technical_skills'),
                                                               comparison_analysis.get('technical_skills'))}
                ],
                temperature=self.feedback_temperature
            )
            technical_skill_match_val = completion['choices'][0]['message']['content']
            comparison_analysis['technical_skills'] = [technical_skill_match_val,
                                                             comparison_analysis['technical_skills']]
            print("TOKENS USED ====> ", dict(completion)['usage']['total_tokens'])
            logger.info("Technical skills matched successfully.")
            return comparison_analysis
        except Exception as error:
            logger.error(f"Error generating technical skills match: {error}", exc_info=True)
            raise

    def process_analysis(self, comparison_analysis, resume_entities, jd_entities):
        """
        Used to score each insight generated using custom scoring logic
        :param comparison_analysis: dict - all analysed insights
        :return: maayu_score - str, scored_analysis - each insight and their corresponding score
        """

        # JOB TITLE
        job_title = comparison_analysis.get('job_title')
        job_title_score = score_job_title(job_title)
        job_title_score['relevant_section_from_Resume'] = resume_entities.get("job_title")
        job_title_score['relevant_section_from_JD'] = jd_entities.get("job_title")
        
        # EDUCATION
        education = comparison_analysis.get('education')
        education_score = score_education(education)
        education_score['relevant_section_from_Resume'] = resume_entities.get("education")
        education_score['relevant_section_from_JD'] = jd_entities.get("education")

        # TECHNICAL SKILLS
        technical_skills = comparison_analysis.get('technical_skills')
        technical_skills_score = score_technical_skills(technical_skills)
        technical_skills_score['relevant_section_from_Resume'] = resume_entities.get("technical_skills")
        technical_skills_score['relevant_section_from_JD'] = jd_entities.get("technical_skills")

        # YEARS OF EXPERIENCE
        years_of_experience = comparison_analysis.get('years_of_experience')
        years_of_experience_score = score_years_of_experience(years_of_experience)
        years_of_experience_score['relevant_section_from_Resume'] = resume_entities.get("years_of_experience")
        years_of_experience_score['relevant_section_from_JD'] = jd_entities.get("years_of_experience")

        # WORK AUTHORIZATION
        work_authorization = comparison_analysis.get('work_authorization')
        work_authorization_score = score_work_authorization(work_authorization)
        work_authorization_score['relevant_section_from_Resume'] = resume_entities.get("work_authorization")
        work_authorization_score['relevant_section_from_JD'] = jd_entities.get("work_authorization")

        # EMPLOYMENT TYPE
        employment_type = comparison_analysis.get('employment_type')
        employment_type_score = score_employment_type(employment_type)
        employment_type_score['relevant_section_from_Resume'] = resume_entities.get("employment_type")
        employment_type_score['relevant_section_from_JD'] = jd_entities.get("employment_type")

        # SALARY EXPECTATION
        salary_expectations = comparison_analysis.get('salary_expectations')
        salary_expectations_score = score_salary_expectation(salary_expectations)
        salary_expectations_score['relevant_section_from_Resume'] = resume_entities.get("salary_expectations")
        salary_expectations_score['relevant_section_from_JD'] = jd_entities.get("salary_expectations")

        # ROLES AND RESPONSIBILITIES
        roles_and_responsibilities = comparison_analysis.get('roles_and_responsibilities')
        roles_and_responsibilities_score = score_roles_and_responsibilities(roles_and_responsibilities)
        roles_and_responsibilities_score['relevant_section_from_Resume'] = resume_entities.get("roles_and_responsibilities")
        roles_and_responsibilities_score['relevant_section_from_JD'] = jd_entities.get("roles_and_responsibilities")

        # LOCATION SCORE
        location = comparison_analysis.get('location')
        location_score = score_location(location) 
        location_score['relevant_section_from_Resume'] = resume_entities.get("location")
        location_score['relevant_section_from_JD'] = jd_entities.get("location")

        # DOMAIN EXPERTISE SCORE
        domain_expertise = comparison_analysis.get('domain_expertise')
        domain_expertise_score = score_domain_expertise(domain_expertise)
        domain_expertise_score['relevant_section_from_Resume'] = resume_entities.get("domain_expertise")
        domain_expertise_score['relevant_section_from_JD'] = jd_entities.get("domain_expertise")

        # EXPERIENCE IN COMPANIES
        experience_in_similar_companies = comparison_analysis.get('experience_in_companies')
        experience_in_similar_companies_score = score_experience_in_similar_companies(experience_in_similar_companies)
        experience_in_similar_companies_score['relevant_section_from_Resume'] = resume_entities.get("experience_in_companies")
        experience_in_similar_companies_score['relevant_section_from_JD'] = jd_entities.get("experience_in_companies")

        # CULTURAL FIT
        cultural_fit = comparison_analysis.get('cultural_fit')
        cultural_fit_score = score_cultural_fit(cultural_fit)
        cultural_fit_score['relevant_section_from_Resume'] = resume_entities.get("cultural_fit")
        cultural_fit_score['relevant_section_from_JD'] = jd_entities.get("cultural_fit")

        # CERTIFICATION
        certifications_and_licenses =  comparison_analysis.get('certifications_and_licenses')
        certifications_and_licenses_score = score_certifications_and_licenses(certifications_and_licenses)
        certifications_and_licenses_score['relevant_section_from_Resume'] = resume_entities.get("certifications_and_licenses")
        certifications_and_licenses_score['relevant_section_from_JD'] = jd_entities.get("certifications_and_licenses")

        scored_analysis = {"job_title":job_title_score, "education": education_score, "years_of_experience": years_of_experience_score,
                           "technical_skills": technical_skills_score, "work_authorization": work_authorization_score,
                           "employment_type": employment_type_score, "salary_expectations": salary_expectations_score,
                           "roles_and_responsibilities": roles_and_responsibilities_score, "location": location_score, 
                           "domain_expertise": domain_expertise_score, 
                           "experience_in_similar_companies":experience_in_similar_companies_score, "cultural_fit":cultural_fit_score, "certifications_and_licenses":certifications_and_licenses_score}
        maayu_score = calculate_maayu_score(scored_analysis)
        logger.info("Analysis processed successfully.")
        return maayu_score, scored_analysis
        
    @retry(stop_max_attempt_number=3)
    def generate_positive_highlights(self, comparison_analysis):
        """
        This function is used to generate highlighting features of the resume
        :param comparison_analysis: dictionary - analyzed information open comparing resume and job description
        :return positive_highlights: text - paragraph having key highlighting features
        """
        try: 
            openai.api_key = self.api_key
            completion = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.positive_highlight_header},
                    {"role": "user", "content": self.positive_highlights_prompt % comparison_analysis}
                ],
                temperature=self.feedback_temperature
            )
            positive_highlights = completion['choices'][0]['message']['content']
            print("TOKENS USED ====> ", dict(completion)['usage']['total_tokens'])
            logger.info("Positive highlights generated successfully.")
            return positive_highlights
        except Exception as error:
            logger.error(f"Error generating positive highlights: {error}", exc_info=True)
            raise
    
    def background_processing_tasks(self):
        """
        Used to process the analysis generation operation in the background
        :return:
        """
        try:
            fetched_results = select_query(select(MaayuInsights.applicant_id, MaayuInsights.resume,
                                                  MaayuInsights.job_description)
                                           .where(MaayuInsights.status == 'queued'))
            for result in fetched_results:
                try:
                    update_query(update(MaayuInsights).where(MaayuInsights.applicant_id == result.applicant_id)
                                 .values(status='processing'))
                    resume_entities = self.process_resume(result.resume)
                    update_query(update(MaayuInsights).where(MaayuInsights.applicant_id == result.applicant_id)
                                 .values(resume_entities=str(resume_entities)))
                    jd_entities = self.process_job_description(result.job_description)
                    update_query(update(MaayuInsights).where(MaayuInsights.applicant_id == result.applicant_id)
                                 .values(jd_entities=str(jd_entities)))
                    comparison_analysis = self.compare_jd_resume(jd_entities, resume_entities)
                    comparison_analysis = self.generate_technical_skills_match(jd_entities, comparison_analysis)
                    maayu_score, maayu_feedback = self.process_analysis(comparison_analysis, resume_entities, jd_entities)
                    positive_feedback = "None"
                    if maayu_score >= 50:
                        positive_feedback = self.generate_positive_highlights(comparison_analysis)
                    generated_insights = prepare_insights_for_db(maayu_score, maayu_feedback, positive_feedback)
                    update_query(update(MaayuInsights).where(MaayuInsights.applicant_id == result.applicant_id)
                                 .values(insights=str(generated_insights), status='processed', response_timestamp=datetime.now()))
                except Exception as error:
                    update_query(update(MaayuInsights).where(MaayuInsights.applicant_id == result.applicant_id)
                                 .values(status='error'))
                    write_error_to_db(f"Error in processing ID :  {result.applicant_id}, Error : {error}",
                                      result.applicant_id)

        except Exception as error:
            write_error_to_db(f"Error in processing background task : {error}", "generic")

    def get_analysed_insights(self, applicant_id):
        """
        This function is fetch the insights fromDB for GET API
        :param applicant_id: string - Applicant ID to be fetched from DB
        :return status, insights - str, str - status column and insights column present in DB
        """
        try:
            fetched_results = select_query(select(MaayuInsights.insights, MaayuInsights.status,
                                                  MaayuInsights.resume_entities, MaayuInsights.jd_entities)
                                           .where(MaayuInsights.applicant_id == applicant_id))
            for result in fetched_results:
                resume, jd, insights = filter_req_ui_col(result.resume_entities, result.jd_entities, result.insights)
                logger.info(f"Insights fetched successfully for ID: {applicant_id}")
                return result.status, insights, resume, jd
            
            return None, None, None, None
        except Exception as error:
            logger.error(f"Error fetching analysed insights for ID {applicant_id}: {error}", exc_info=True)
            raise

    def run(self, request):
        """
        Used to create tables and insert input to DB
        :param request: dict - containing resume, jd, applicant_id
        :return: Success - None, Failure - raise exception
        """
        try:
            create_tables(self.tables)
            insert_query(MaayuInsights, [{"applicant_id": request.request_id, "resume": request.resume,
                                      "job_description": request.job_description, "request_timestamp": datetime.now(),
                                      "status": "queued", "resume_entities": None, "jd_entities": None, 
                                      "insights": None, "response_timestamp": None}])
            logger.info("Data inserted into DB successfully.")
        except Exception as error:
            logger.error(f"Error writing data to DB: {error}", exc_info=True)
            raise