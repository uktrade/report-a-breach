# TODO: should this be a single json object which holds all question data? If so, should we specify a schema?

FULL_NAME = {
    "text": "What is your full name?",
    "helper": "",
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
        ("owner", "I'm an owner, officer or employee of the company, or I am the person"),
        (
            "acting",
            "I do not work for the company, but I'm acting on their behalf to make a voluntary declaration",
        ),
        (
            "third_party",
            "I work for a third party with a legal responsibility to make a mandatory declaration",
        ),
        (
            "no_professional_relationship",
            "I do not have a professional relationship with the company or person or I no longer have a professional relationship with them",
        ),
    ),
}

ADDITIONAL_INFORMATION = {"text": "Tell us about the suspected breach", "helper": ""}
WHAT_WERE_THE_GOODS = {
    "text": "What were the goods or services, or what was the technological assistance or technology?",
    "helper": "",
}
