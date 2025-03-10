import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import OpenAI from "openai";
import { createClient } from "redis";

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

const redisClient = createClient({
  url: process.env.REDIS_URL || "redis://localhost:6379",
});

await redisClient.connect();

redisClient.on("error", (err) => console.error("Redis Client Error", err));

const CACHE_TTL = 14 * 24 * 3600;  // 2 week cache expiration in seconds (1,209,600)

app.post("/generate-content", async (req, res) => {
  const { query = "" } = req.body;
  const cacheKey = `content:${query}`.toLowerCase();

  let cachedContent;
  try {
    cachedContent = await redisClient.get(cacheKey);
    if (cachedContent) {
      return res.send(cachedContent);
    }
  } catch (err) {
    console.error('Redis error (get):', err);
  }

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content: `I'd like you to help me learn more about history. When I give you a historical topic or ask a specific question, please provide a short summary and long in-depth and detailed explanation. Format the response with clear sections including the explanation, 3-5 key events (each with a name, date, and short description field), 3-5 important figures (each with a name and reason field), and a few related topics I might want to explore. The output should be formatted like: {"title":"Example Title","summary":"Example summary","explanation":"Example explanation","key_events":[{"name":"Example Event","date":"Example Date","description":"Example description"}],"important_figures":[{"name":"Example Person","reason":"Example reason"}],"related_topics":["Example Related Topic"]}`,
        },
        { role: "user", content: query },
      ],
      store: true,
      temperature: 0,
      max_tokens: 4096,
      top_p: 1,
      frequency_penalty: 0,
      presence_penalty: 0,
    });

    const content = completion.choices[0].message.content;
    //console.log('content:', content);
    
    try {
      const title = JSON.parse(content).title.toLowerCase()
      await redisClient.set(title, content, { EX: CACHE_TTL });
      await redisClient.set(cacheKey, content, { EX: CACHE_TTL });
    } catch (err) {
      console.error("Redis error (set):", err);
    }

    res.send(content);

  } catch (error) {
    console.error("Error in /generate-content:", error);
    res.status(500).json({ error: error.message });
  }
});


app.post("/generate-quiz", async (req, res) => {
  const { topic = "" } = req.body;

  try {
    const completion = await openai.chat.completions.create({
      model: "gpt-4o-mini",
      messages: [
        {
          role: "system",
          content:
            'When I give you a topic, please generate a quiz with one to three multiple-choice questions (depending on how broad the topic is) about the topic. Format your response as a JSON object list with key questions, where each question is an object that has the fields question, options, and answer. The options and answer should just be the content, no numbers or letters. For example, it should be {"questions": [{"question": "question1", "options": ["option1", "option2", "option3", "option4"], "answer": "option1"}, {"question": "question2", "options": ["option1", "option2", "option3", "option4"], "answer": "option1"}]}',
        },
        { role: "user", content: topic },
      ],
      store: true,
      temperature: 0.5,
      max_tokens: 300,
      top_p: 1,
      frequency_penalty: 0,
      presence_penalty: 0,
    });

    const questions = completion.choices[0].message.content;
    //console.log('questions:', questions);

    res.send(questions);

  } catch (error) {
    console.error("Error in /generate-quiz:", error);
    res.status(500).json({ error: error.message });
  }
});


const PORT = process.env.PORT || 5001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

