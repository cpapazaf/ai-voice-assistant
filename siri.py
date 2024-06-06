from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain_community.llms import Ollama
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from speech_recognition import Microphone, Recognizer, UnknownValueError
import contextlib
with contextlib.redirect_stdout(None):
    import pygame
from gtts import gTTS
from io import BytesIO


class MySiri:
    def __init__(self, model):
        self.chain = self._create_inference_chain(model)
        pygame.init()
        pygame.mixer.init()

    def answer(self, prompt):
        if not prompt:
            return

        self._gtts(f"You asked me: {prompt}. Let me think for a while.")

        response = self.chain.invoke(
            {"prompt": prompt},
            config={"configurable": {"session_id": "unused"}},
        ).strip()

        if response:
            self._gtts(response)

    def stop():
        pygame.display.quit()
        pygame.quit()

    def _gtts(self, response):
        tts = gTTS(text=response, lang='en', slow=False)

        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        pygame.mixer.music.load(fp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def _create_inference_chain(self, model):
        SYSTEM_PROMPT = """
        You are a witty assistant that will use the chat history 
        provided by the user to answer its questions. Your name is Siri.

        Use few words on your answers. Go straight to the point. Do not use any
        emoticons or emojis. Do not ask the user any questions.

        Be friendly and helpful. Show some personality. Do not be too formal.
        """

        prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", [{"type": "text", "text": "{prompt}"},],),
            ]
        )

        chain = prompt_template | model | StrOutputParser()

        chat_message_history = ChatMessageHistory()
        return RunnableWithMessageHistory(
            chain,
            lambda _: chat_message_history,
            input_messages_key="prompt",
            history_messages_key="chat_history",
        )

model = Ollama(
    model="llama3"
)

my_siri = MySiri(model)

def audio_callback(recognizer, audio):
    try:
        prompt = recognizer.recognize_whisper(audio, model="base", language="english")
        if prompt and prompt.strip().lower().startswith('hi siri'):
            my_siri.answer(prompt.strip().replace("."," ... "))
    except UnknownValueError:
        print("[ERROR] There was an error processing the audio.")


recognizer = Recognizer()
microphone = Microphone()
with microphone as source:
    recognizer.adjust_for_ambient_noise(source)

stop_listening = recognizer.listen_in_background(microphone, audio_callback)

while True:
    choice = input("Enter Q to quit!\n")
    if choice.lower() == "q":
        break

stop_listening(wait_for_stop=False)
my_siri.stop()