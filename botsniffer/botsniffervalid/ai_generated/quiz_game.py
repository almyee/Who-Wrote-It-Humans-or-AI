import time
import random

# Sample quiz questions
QUESTIONS = [
    {
        "question": "What is the capital of France?",
        "options": ["A) Madrid", "B) Berlin", "C) Paris", "D) Rome"],
        "answer": "C"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["A) Earth", "B) Mars", "C) Jupiter", "D) Saturn"],
        "answer": "B"
    },
    {
        "question": "Who developed the theory of relativity?",
        "options": ["A) Isaac Newton", "B) Albert Einstein", "C) Galileo Galilei", "D) Nikola Tesla"],
        "answer": "B"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["A) Atlantic Ocean", "B) Indian Ocean", "C) Arctic Ocean", "D) Pacific Ocean"],
        "answer": "D"
    },
    {
        "question": "Which gas do plants use for photosynthesis?",
        "options": ["A) Oxygen", "B) Carbon Dioxide", "C) Nitrogen", "D) Hydrogen"],
        "answer": "B"
    }
]

def ask_question(question_data):
    """Asks a question and returns True if answered correctly, False otherwise."""
    print("\n" + question_data["question"])
    for option in question_data["options"]:
        print(option)
    
    start_time = time.time()
    answer = input("Your answer (A, B, C, or D): ").strip().upper()
    time_taken = time.time() - start_time

    if answer == question_data["answer"]:
        print("✅ Correct!")
        return True, time_taken
    else:
        print(f"❌ Wrong! The correct answer was {question_data['answer']}.")
        return False, time_taken

def quiz_game():
    """Runs the quiz game with scoring and time tracking."""
    print("🎉 Welcome to the Quiz Game! 🎉")
    print("You will be asked multiple-choice questions. Try to answer correctly!")
    
    random.shuffle(QUESTIONS)  # Shuffle questions for variation
    score = 0
    total_time = 0

    for question in QUESTIONS:
        correct, time_taken = ask_question(question)
        total_time += time_taken
        if correct:
            score += 1

    print("\nGame Over! 🏆")
    print(f"Your final score: {score}/{len(QUESTIONS)}")
    print(f"Total time taken: {total_time:.2f} seconds")
    
    if score == len(QUESTIONS):
        print("🎉 Perfect score! You're a quiz master! 🎉")
    elif score > len(QUESTIONS) // 2:
        print("👍 Good job! You did well.")
    else:
        print("😢 Better luck next time!")

if __name__ == "__main__":
    quiz_game()
