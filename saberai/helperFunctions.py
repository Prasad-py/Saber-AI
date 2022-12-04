import random
import json
from bson import json_util
from saberai import GPT_Engine, openai

def get_prompt(query_dict):
    service = query_dict["service"] if "service" in query_dict else None
    title = query_dict["title"] if "title" in query_dict else None
    keywords = query_dict["keywords"] if "keywords" in query_dict else None
    # prev_email = query_dict["prev_email"] if "prev_email" in query_dict else None
    # bullet_points = query_dict["bullet_points"] if "bullet_points" in query_dict else None
    query = query_dict["query"] if "query" in query_dict else None
    purpose = query_dict["purpose"] if "purpose" in query_dict else None
    language = query_dict["language"] if "language" in query_dict else None
    company_name = query_dict["company_name"] if "company_name" in query_dict else None

    prompts_dict = {
        "blog-article": f"Title:\n{title}\nKeywords:\n{keywords}\nWrite a long blog article for the above title using the given keywords:\nArticle:\n",
        "social-media": f"Subject of the Advertisement:\n{query}\nWrite a long and clever Advertisement on the given subject:\nAd:\n",
        "cold-emails": f"Services:\n{title}\nA company named {company_name} provides the above services.\nWrite a cold email to advertise its services:\nEmail:\n",
        "tweet-ideas": f"Description:\n{title}\nWrite a long and clever tweet for the above decription:\nTweet:\n",
        #     "email-gen": 
        "code-gen": f"Usecase of the Code:\n{purpose}\nWrite a {language} function for the above usecase:\nCode:\n",
    }
    
    return prompts_dict[service]

def get_gpt3_response(query_dict):
    raw_response = openai.Completion.create(
                engine=GPT_Engine,
                prompt= get_prompt(query_dict),
                temperature=0.7,
                max_tokens=500,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
    return raw_response

def generate_code():
    code = random.choice(range(100000, 999999))  # generating 6 digit random code
    return code

def returns_estimated_number_of_tokens_used(text_input):
    number_of_words_in_input = len(text_input.split())
    total_words_processed_by_gpt = 4 * number_of_words_in_input
    tokens_used_up = total_words_processed_by_gpt/2.5
    return tokens_used_up

def parse_json(data):
    return json.loads(json_util.dumps(data))

def get_subscriptions():
    freeTierPlan = {
        "title": "Saber's Free Plan Verification",
        "includes": ["We charge a fee of Rs.2 from your account for verification of your identity.",
                    "This amount will be refunded back to your account in the next 48 hrs. ",
                    "This step is done to weed out the Bots."]
    }
    saberToothPlan = {
        "title": "Saber's Sabertooth Plan",
        "includes": ["Access to all tokens.",
                    "30,000 tokens on a monthly basis."]
    }
    mammothPlan = {
        "title": "Saber's Mammoth Plan",
        "includes": ["Unlimited Access to all Services.",
                    "Unlimited number of tokens to use.*",
                    "(Max limited to 1 lakh tokens)"]
    }
    subscriptions = [freeTierPlan,saberToothPlan,mammothPlan]
    return subscriptions