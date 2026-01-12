TEXT_FIELD_PROMPT = """
        Following the resume below, return the answer for the following question: {field_label}.
        \n resume: {resume_content}\n
        give positive answer as I want to get the interview for the job.
        make answer shortest. 
        if its \"yes / no\" quesion, return only yes or no.
        if its \"how many\" question or any request for numeric response, return only number.
        if its \"phone number\" question, return only digits.
        if its simple personal detail like \"first name\", \"last name\", \"email\", \"address\", \"linkedin\", \"github\", etc., return only the relevant value from the resume, without any additional words or characters.
        and for any other question, be specific and return only necessary details.
        you should act as you are filling job application form, you should answer only with the exact value to be filled.
        when you cant find the answer in the resume, return \"Not available\".
        do not explain when answer not found in resume, just return \"Not available\".
        do not include the label in your response.
    """

SELECT_FIELD_PROMPT = """
        Following the resume below, select the right option: {field_label}
        \n resume: {resume_content} \n
        be positive as I want to get the interview for the job.
        return only the text of the selected option and nothing else. 
    """

RADIO_FIELD_PROMPT ="""
        Following the resume below, choose the right option: {field_label}
        \n resume: {resume_content} \n
        be positive as I want to get the interview for the job.
        return only the text of the selected option and nothing else.
    """

@staticmethod
def get_prompt(field_label: str, resume_content: str) -> str:
    return TEXT_FIELD_PROMPT.format(
        field_label=field_label,
        resume_content=resume_content
    )