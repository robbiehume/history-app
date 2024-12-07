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

    content  = dict(response)['choices'][0].message.content
    print(content)

    return content


# Endpoint to generate related topics (in case of specific dynamic needs)
@app.route('/related-topics', methods=['POST'])
def related_topics():
    data = request.json
    topic = data.get('topic', '')

    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "user", "content": f"Provide a list of topics related to the following historical event: {topic}"}
      ],
      temperature=1,
      max_tokens=100,
      top_p=1,
      frequency_penalty=0,
      presence_penalty=0
    )

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

    quiz_text  = dict(response)['choices'][0].message.content
    #print(quiz_text)

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

