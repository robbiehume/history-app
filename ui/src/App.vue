<template>
  <div id="app" style="width: 90vw; max-width: 1000px">
        <h1 style="color:black">Learn About History!</h1>
        <div class="flex gap-2 justify-content-center mt-2">
          <InputText v-model="searchQuery" placeholder="Search for a topic, ask a question, look up a person, etc." @keyup.enter="searchTopic" style="width: 60%"/>
          <Button  @click="searchTopic" style="width: 50px">
            <ProgressSpinner v-if="gettingContent" style="width: 20px; height: 20px" />
            <i v-else class="pi pi-search" />
          </Button>
        </div>

    <div v-if="contentResponse" class="content flex flex-column align-items-center gap-3" style="color:black">
      <h1>{{ contentResponse.title }}</h1>

      <div class="flex flex-column">
        <h3>Summary</h3>
        <span>{{ contentResponse.summary }}</span>
      </div>

      <div class="flex flex-column ">
        <h3>Detailed Explanantion</h3>
        <span>{{ contentResponse.explanation }}</span>
      </div>
      
      <div v-if="contentResponse.key_events" class="flex flex-column align-items-start align-self-center justify-content-center"> 
        <h3>Key Events:</h3>
        <li v-for="event of contentResponse.key_events" :key="event" style="text-align:left">
          <b>{{ event.name }}</b> ({{ event.date }}): {{ event.description }}
        </li>
      </div>
      
      <div v-if="contentResponse.important_figures" class="flex flex-column align-items-start align-self-center justify-content-center">
        <h3>Important Figures:</h3>
        <li v-for="figure of contentResponse.important_figures" :key="figure" style="text-align:left">
          <b>{{ figure.name }}</b>: {{ figure.reason }}
        </li>
      </div>

      <div class="flex flex-column align-self-center justify-content-center" style="width: fit-content;">
        <h3>Related Topics:</h3>
        <ul style="columns:2; column-gap: 40px; width: fit-content;">
          <li v-for="topic in relatedTopics" :key="topic" @click="selectTopic(topic)" style="text-align:left; width:fit-content; cursor: pointer">
            {{ topic }}
          </li>
        </ul>
      </div>

      <Button class="align-self-center mt-2 flex justify-content-center" style="width: 130px" @click="startQuiz" >
        <div v-if="gettingQuiz">Generating...</div>
        <div v-else>Take Quiz</div>
      </Button>
    </div>

    <Dialog header="Quiz" v-model:visible="quizVisible" :modal="true" style="width:60vw; height: 70vh">
      <div v-if="currentQuestion" class="flex flex-column gap-2 align-items-center justify-content-center">
        <h3>Question {{ currentQuestionIndex + 1 }}</h3>
        <p>{{ currentQuestion.question }}</p>

        <div  class="flex flex-column gap-1 align-items-start">
          <div v-for="(option, index) in currentQuestion.options" :key="index" class="flex align-items-center gap-2">
            <RadioButton v-model="userAnswer" :value="option" />
            <label>{{ option }}</label>
          </div>
        </div>

        <div v-if="!answerChecked" class="mt-1">
          <p style="color:white">x</p>
          <Button class="mt-1" label="Check Answer" @click="checkAnswer" />
        </div>
        <div v-else class="flex flex-column align-items-center gap-1 mt-1">
          <p v-if="userAnswer === currentQuestion.answer">Correct!</p>
          <p v-else>Incorrect. The correct answer is: {{ currentQuestion.answer }}</p>
          <Button label="Next" @click="nextQuestion" />
        </div>
      </div>
      <div v-else class="flex flex-column align-items-center gap-1 mt-1">
        <h3>Quiz Complete!</h3>
        <p>You scored {{ score }} out of {{ quizQuestions.length }}</p>
        <Button label="Close" @click="closeQuiz" />
      </div>
    </Dialog>

    <Toast style="width: fit-content" />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import RadioButton from 'primevue/radiobutton';
import ProgressSpinner from 'primevue/progressspinner';
import Toast from 'primevue/toast'
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const gettingContent = ref(false);
const searchQuery = ref('');
const selectedTopic = ref(null);
const contentResponse = ref('');
const relatedTopics = ref([]);
const gettingQuiz = ref(false);
const quizVisible = ref(false);
const quizQuestions = ref([]);
const currentQuestionIndex = ref(0);
const currentQuestion = ref(null);
const userAnswer = ref(null);
const answerChecked = ref(false);
const score = ref(0);

const API_ENDPOINT = '/api'


function showError(message) {
    toast.add({ severity: 'error', detail: message, life: 3000, closable: false });
};

const searchTopic = async () => {
  gettingContent.value = true
  try {
    contentResponse.value = ''
    const response = await axios.post(`${API_ENDPOINT}/generate-content`, { query: searchQuery.value });
    contentResponse.value = response.data;
    relatedTopics.value = response.data.related_topics;
  } catch (error) {
    console.error('Error fetching topic data:', error);
    showError('Error fetching data from API')
  }
  gettingContent.value = false
};

const selectTopic = async (topic) => {
  selectedTopic.value = topic;
  searchQuery.value = topic;
  searchTopic()
};

const startQuiz = async () => {
  try {
    if (contentResponse.value) {
      // Fetch quiz questions from backend using the title from contentResponse
      gettingQuiz.value = true
      const response = await axios.post(`${API_ENDPOINT}/generate-quiz`, { topic: contentResponse.value.title });
      gettingQuiz.value = false
      quizQuestions.value = response.data.questions;
      currentQuestionIndex.value = 0;
      currentQuestion.value = quizQuestions.value[currentQuestionIndex.value];
      quizVisible.value = true;
      score.value = 0;
      answerChecked.value = false;
      userAnswer.value = null;
    } 
  }
  catch (error) {
    gettingQuiz.value = false
    console.error('Error fetching quiz data:', error);
    showError('Error fetching quiz data from API')
  }
};

const checkAnswer = () => {
  answerChecked.value = true;
  if (userAnswer.value === currentQuestion.value.answer) {
    score.value++;
  }
};

const nextQuestion = () => {
  currentQuestionIndex.value++;
  if (currentQuestionIndex.value < quizQuestions.value.length) {
    currentQuestion.value = quizQuestions.value[currentQuestionIndex.value];
    userAnswer.value = null;
    answerChecked.value = false;
  } else {
    currentQuestion.value = null;
  }
};

const closeQuiz = () => {
  quizVisible.value = false;
};

</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  margin: 20px;
}
.content {
  margin-top: 20px;
}

h1, h3 {
  align-self: center;
}

span {
  text-align: left;
}

.p-dialog-header {
  padding-bottom: 0px
}

.p-dialog-content { 
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.p-toast-detail {
  margin: 0;
}

.p-toast-message .p-toast-message-content {
  display: flex;
  align-items: center;
  gap: 10px; 
}

</style>
