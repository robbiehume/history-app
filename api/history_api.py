#!python3

from flask import Flask, request, jsonify
from openai import OpenAI
import json
import os
from time import sleep

from flask_cors import CORS
app = Flask(__name__)
cors = CORS(app)

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Endpoint to generate content based on user query
@app.route('/generate-content', methods=['POST'])
def generate_content():
    data = request.json
    query = data.get('query', '')
    #sleep(2)

    #return {"title":"The American Revolution","summary":"The American Revolution (1775-1783) was a conflict between the thirteen American colonies and Great Britain, resulting in the founding of the United States of America.","explanation":"The American Revolution was a colonial revolt against British rule. Growing discontent among the colonies due to taxation without representation, restrictions on colonial trade, and the influence of Enlightenment ideas led to escalating tensions. The war began in 1775 with the Battles of Lexington and Concord and culminated in the signing of the Treaty of Paris in 1783, which recognized the independence of the United States.\n\nKey factors contributing to the revolution included: \n- Enlightenment ideas about democracy and rights.\n- Increased taxation and regulation imposed by Britain (e.g., Stamp Act, Tea Act).\n- The influence of revolutionary leaders and groups, such as the Sons of Liberty.\n- Escalating protests, including the Boston Tea Party and the Intolerable Acts.\n\nThe revolution also had significant global implications, inspiring other countries in their struggles for independence.","key_events":[{"date":"1775-04-19","event":"Battles of Lexington and Concord"},{"date":"1776-07-04","event":"Declaration of Independence"},{"date":"1777-10-17","event":"Battle of Saratoga"},{"date":"1781-10-19","event":"Surrender at Yorktown"},{"date":"1783-09-03","event":"Treaty of Paris Signed"}],"important_figures":[{"name":"George Washington","role":"Commander-in-Chief of the Continental Army"},{"name":"Thomas Jefferson","role":"Principal author of the Declaration of Independence"},{"name":"Benjamin Franklin","role":"Diplomat and key negotiator with France"},{"name":"John Adams","role":"Advocate for independence and second President of the U.S."},{"name":"King George III","role":"King of Great Britain during the revolution"}],"related_topics":[{"topic":"The Enlightenment"},{"topic":"French Revolution"},{"topic":"The Articles of Confederation"},{"topic":"The Constitution of the United States"},{"topic":"The War of Independence in other countries"}],"response_messages":"Feel free to ask about specific events, figures, or related topics for a deeper understanding!"}


    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
          {"role": "system", "content": f"I'd like you to help me learn more about history. When I give you a historical topic or ask a specific question, please provide a short summary and 2 paragraphs (with indentation and line breaks) of an in-depth explanation. Format the response with clear sections including the explanation, 3-5 key events (each with a name, date, and short description field), 3-5 important figures (each with a name and reason field), and a few related topics I might want to explore. Use bullet points or numbered lists where appropriate. Please format your whole response in JSON format, with separate keys for the title, summary, explanation, key_events, important_figures, related_topics,  and any other response messages"},
        {"role": "system", "content": query}

      ],
      response_format={'type': 'json_object'},
      temperature=1,
      max_tokens=4096,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    #content = response.choices[0].text.strip()
    #content  = json.loads(dict(response)['choices'][0].message.content)
    content  = dict(response)['choices'][0].message.content
    print(content)

    # Mocking related topics for simplicity
    related_topics = [
        {"id": 1, "title": f"Background of {query}"},
        {"id": 2, "title": f"Impact of {query}"},
        {"id": 3, "title": f"Notable Figures in {query}"}
    ]

    return content

    #return jsonify({
    #    "response": content,
    #    "title": content.get('title', content.get('historical_topic')), 
    #    "overview": content.get('overview'),
    #    "key_events": content.get('key_events'),
    #    "important_figures": content.get('important_figures'),
    #    "relatedTopics": related_topics
    #})


# Endpoint to generate related topics (in case of specific dynamic needs)
@app.route('/related-topics', methods=['POST'])
def related_topics():
    data = request.json
    topic = data.get('topic', '')

    #response = openai.Completion.create(
    #    engine="text-davinci-003",
    #    prompt=f"Provide a list of topics related to the following historical event: {topic}",
    #    max_tokens=100
    #)

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        #{"role": "system", "content": ""},
        {"role": "user", "content": f"Provide a list of topics related to the following historical event: {topic}"}
      ],
      #response_format={'type': 'json_object'},
      temperature=1,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    #related = response.choices[0].text.strip().split("\n")
    related  = dict(response)['choices'][0].message.content.strip().split('\n')

    related_topics = [{"id": i, "title": related_topic} for i, related_topic in enumerate(related) if related_topic]

    return jsonify({
        "relatedTopics": related_topics
    })

# Endpoint to generate a quiz based on the selected topic
@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    data = request.json
    topic = data.get('topic', '')

    #return {"questions":[{"question":"What was the primary cause of the American Revolution?","options":["Taxation without representation","Desire for more land","Support for British monarchy","Religious conflict"],"answer":"Taxation without representation"},{"question":"Which document formally ended the American Revolution?","options":["The Constitution","The Articles of Confederation","The Treaty of Paris","The Declaration of Independence"],"answer":"The Treaty of Paris"},{"question":"Who was the commander of the Continental Army during the American Revolution?","options":["Thomas Jefferson","George Washington","Benjamin Franklin","John Adams"],"answer":"George Washington"}]}


    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": f"When I give you a topic, please generate a quiz with one to three multiple-choice questions (depending how broad the topic is) about the topic. Format your response as a JSON object list with key questions, where each question is an object that has the fields question, options, and answer. The options and answer should just be the content, no numbers or letters"},
        {"role": "user", "content": f"{topic}"},
      ],
      response_format={'type': 'json_object'},
      temperature=1,
      max_tokens=300,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

    #quiz_text = response.choices[0].text.strip().split("\n\n")
    quiz_text  = dict(response)['choices'][0].message.content
    print(quiz_text)

    return quiz_text

    questions = []
    for i, question_block in enumerate(quiz_text):
        lines = question_block.split("\n")
        if len(lines) >= 2:
            question_text = lines[0]
            options = lines[1:]
            answer = options[0]  # Assuming first option is correct in this case
            questions.append({
                "text": question_text,
                "options": options,
                "answer": answer
            })

    return jsonify({
        "questions": questions
    })

# Run the Flask app
if __name__ == '__main__':
    app.run(port=5001, debug=True)

