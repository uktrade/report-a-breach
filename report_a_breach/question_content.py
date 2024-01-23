# TODO: should this be a single json object which holds all question data? If so, should we specify a schema?

FULL_NAME = {
    "text": "What is your full name?",
    "helper": "Please enter your name as it appears on your passport",
}

EMAIL = {
    "text": "What is your email address?",
    "helper": "We need to send you an email to verify your email address",
}

VERIFY = {"text": "We've sent you an email", "helper": "Enter the 6 digit security code"}

RELATIONSHIP = {
    "text": "What is the professional relationship with the company or person suspected of breaching "
    "sanctions?",
    "choices": (
        "I'm an owner, officer or employee of the company, or I am the person",
        "I do not work for the company, but I'm acting on their behalf to make a voluntary declaration",
        "I work for a third party with a legal responsibility to make a mandatory declaration",
        "I do not have a professional relationship with the company or person or I no longer have a professional "
        "relationship with them",
    ),
}
