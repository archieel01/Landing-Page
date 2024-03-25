import streamlit as st
import os
import random
from PyPDF2 import PdfReader
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def extract_text_from_pdf(uploaded_file):
    text = ""
    pdf_reader = PdfReader(uploaded_file)
    num_pages = len(pdf_reader.pages)
    for page_number in range(num_pages):
        page = pdf_reader.pages[page_number]
        text += page.extract_text()
    return text

def generate_quiz(text, num_questions=10):
    # Split text into sentences
    sentences = text.split('.')
    # Randomly select sentences to use as questions
    selected_sentences = random.sample(sentences, min(len(sentences), num_questions))
    # Generate multiple-choice questions
    questions = []
    stop_words = set(stopwords.words('english'))
    for sentence in selected_sentences:
        words = word_tokenize(sentence)
        # Filter out stop words and punctuation
        words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
        # Ensure there are enough words to create a meaningful question
        if len(words) >= 5:
            # Randomly select a word to replace with a blank
            blank_word = random.choice(words)
            # Replace the word with a blank
            words[words.index(blank_word)] = '__________'
            question = ' '.join(words)
            # Generate multiple-choice options
            choices = [blank_word.capitalize()]  # Correct answer
            # Filter out words similar to the blank word
            for word in words:
                if word != blank_word and word not in choices:
                    choices.append(word.capitalize())
                    if len(choices) == 4:
                        break
            random.shuffle(choices)
            # Ensure there are exactly 4 choices
            while len(choices) < 4:
                additional_choice = random.choice(words)
                if additional_choice.capitalize() not in choices:
                    choices.append(additional_choice.capitalize())
            random.shuffle(choices)
            questions.append((sentence.strip(), question, choices, blank_word))
    return questions



def grade_quiz(questions, selected_answers):
    num_correct = 0
    num_questions = len(questions)
    if num_questions == 0:
        return 0  # Return score of 0 if there are no questions
    for question, selected_option in zip(questions, selected_answers):
        correct_option = question[-1]  # Get the last element of the tuple as the correct option
        if selected_option[0].capitalize() == correct_option.capitalize():  # Access the first element of the tuple and capitalize it
            num_correct += 1
    score = (num_correct / num_questions) * 100
    return score

def main():
     # Add CSS for black background
    st.markdown(
        """
        <style>
        body {
            background-color: #000000;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("PDF to Quiz Generator")

    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        # Extract text from uploaded PDF
        extracted_text = extract_text_from_pdf(uploaded_file)
        # Generate quiz questions
        questions = generate_quiz(extracted_text, num_questions=20)  # Generate 20 questions
        # Display questions
        st.subheader("Quiz Questions")
        selected_answers = []
        for i, (original_sentence, question, choices, _) in enumerate(questions, start=1):
            st.write(f"Question {i}:")
            st.write(f"Question: {question}")
            selected_option = st.radio("Select the correct word for the blank:", choices)
            selected_answers.append((question, selected_option, choices))
        
        # Grade the quiz
        score = grade_quiz(questions, selected_answers)
        st.write(f"Your Score: {score}%")

if __name__ == "__main__":
    main()
