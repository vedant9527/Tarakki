import random
import sqlite3
import csv
import logging
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('aptitude1.db')
    cursor = conn.cursor()

    # Create the questions table if it doesn't exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        parameter TEXT NOT NULL,
                        question_text TEXT NOT NULL,
                        option_a TEXT NOT NULL,
                        option_b TEXT NOT NULL,
                        option_c TEXT NOT NULL,
                        option_d TEXT NOT NULL,
                        correct_option TEXT NOT NULL
                      )''')

    # Load questions from the CSV file
    with open('your_data_2.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            cursor.execute('''INSERT INTO questions 
                              (parameter, question_text, option_a, option_b, option_c, option_d, correct_option) 
                              VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                              (row['parameter'], row['question_text'], row['A'], row['B'], 
                               row['C'], row['D'], row['correct_option']))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

logging.basicConfig(level=logging.INFO)

@app.route('/start_test', methods=['POST'])
def start_test():
    conn = sqlite3.connect('aptitude1.db')
    cursor = conn.cursor()

    test_id = random.randint(1, 10000)
    questions = {}
    parameters = [
        'O_score', 'C_score', 'E_score', 'A_score', 'N_score',
        'Numerical_Aptitude', 'Spatial_Aptitude', 'Perceptual_Aptitude',
        'Abstract_Reasoning', 'Verbal_Reasoning'
    ]

    for parameter in parameters:
        cursor.execute("SELECT * FROM questions WHERE parameter = ?", (parameter,))
        rows = cursor.fetchall()
        logging.info(f'Number of questions for {parameter}: {len(rows)}')

        if len(rows) < 10:
            logging.warning(f'Not enough questions for {parameter}. Skipping this parameter.')
            continue

        # Ensure unique selection of questions
        selected_questions = random.sample(rows, 10)
        questions[parameter] = [
            {
                'id': row[0],
                'text': row[2],
                'options': [row[3], row[4], row[5], row[6]]
            }
            for row in selected_questions
        ]

    conn.close()

    return jsonify({'test_id': test_id, 'questions': questions})

@app.route('/submit_test', methods=['POST'])
def submit_test():
    data = request.json
    test_id = data['test_id']
    answers = data['answers']
    logging.info(f'Submitted Answers: {answers}')

    conn = sqlite3.connect('aptitude1.db')
    cursor = conn.cursor()

    scores = {param: 0 for param in [
        'O_score', 'C_score', 'E_score', 'A_score', 'N_score',
        'Numerical_Aptitude', 'Spatial_Aptitude', 'Perceptual_Aptitude',
        'Abstract_Reasoning', 'Verbal_Reasoning'
    ]}
    
    # for question_id, answer in answers.items():
    #     cursor.execute("SELECT parameter, correct_option FROM questions WHERE id = ?", (question_id,))
    #     result = cursor.fetchone()
    #     if result:
    #         parameter, correct_option = result
    #         # Assuming options are always "A", "B", "C", "D"
    #         score = calculate_score(answer, correct_option)
    #         scores[parameter] += score

    for question_id, answer in answers.items():
        cursor.execute("SELECT parameter, correct_option, option_a, option_b, option_c, option_d FROM questions WHERE id = ?", (question_id,))
        result = cursor.fetchone()
        if result:
            parameter, correct_option, option_a, option_b, option_c, option_d = result
            # Pass the options list to the scoring function
            options = [option_a, option_b, option_c, option_d]
            score = calculate_score(answer, correct_option, options)
            scores[parameter] += score


    # Map the scores to a job field
    job_field = map_scores_to_job(scores)  # Implement this function as needed
    qualities = determine_qualities(scores)
    conn.close()

    return jsonify({'job_field': job_field, 'scores': scores, 'qualities':qualities})


def determine_qualities(scores):
    qualities = []

    # 1. Innovative Thinker
    if scores['O_score'] > 8 and scores['Abstract_Reasoning'] > 8 and scores['Verbal_Reasoning'] > 7:
        qualities.append('Innovative Thinker')
    
    # 2. Analytical
    if scores['Numerical_Aptitude'] > 8 and scores['C_score'] > 8 and scores['Abstract_Reasoning'] > 7:
        qualities.append('Analytical')
    
    # 3. Practical Problem-Solver
    if scores['N_score'] > 7 and scores['Spatial_Aptitude'] > 8 and scores['Perceptual_Aptitude'] > 6:
        qualities.append('Practical Problem-Solver')
    
    # 4. Communicative Leader
    if scores['E_score'] > 8 and scores['Verbal_Reasoning'] > 8 and scores['A_score'] > 6:
        qualities.append('Communicative Leader')

    # 5. Creative Visionary
    if scores['O_score'] > 8 and scores['Spatial_Aptitude'] > 7 and scores['Abstract_Reasoning'] > 8:
        qualities.append('Creative Visionary')

    # 6. Detail-Oriented
    if scores['C_score'] > 8 and scores['Perceptual_Aptitude'] > 7:
        qualities.append('Detail-Oriented')

    # 7. Strategic Thinker
    if scores['Abstract_Reasoning'] > 8 and scores['Verbal_Reasoning'] > 7 and scores['Numerical_Aptitude'] > 7:
        qualities.append('Strategic Thinker')

    # 8. Technically Proficient
    if scores['Numerical_Aptitude'] > 8 and scores['Spatial_Aptitude'] > 7:
        qualities.append('Technically Proficient')

    # 9. Adaptive
    if scores['O_score'] > 7 and scores['A_score'] > 7:
        qualities.append('Adaptive')

    # 10. Logical Thinker
    if scores['Numerical_Aptitude'] > 8 and scores['C_score'] > 8:
        qualities.append('Logical Thinker')

    # 11. Collaborative
    if scores['E_score'] > 7 and scores['A_score'] > 7:
        qualities.append('Collaborative')

    # 12. Resilient
    if scores['N_score'] > 8 and scores['A_score'] > 6:
        qualities.append('Resilient')

    # Consider secondary or overlapping qualities
    if scores['O_score'] > 7 and scores['C_score'] > 7:
        qualities.append('Balanced')

    if scores['A_score'] > 8 and scores['N_score'] < 6:
        qualities.append('Emotionally Stable')
    
    if not qualities:
        qualities.append("Balanced")  # Default if no specific qualities match
    
    return qualities



def validate_option(option):
    return option in ["A", "B", "C", "D"]

def calculate_score(answer, correct_option, options):
    logging.info(f'Answer: {answer}, Correct Option: {correct_option}, Options: {options}')
    
    if not validate_option(answer) or not validate_option(correct_option):
        logging.error(f'Invalid option detected - Answer: {answer}, Correct Option: {correct_option}')
        return 0

    # Check if the options are in the specified order
    if options == ["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"]:
        score_map = {
            "A": {"A": 1, "B": 0.75, "C": 0.5, "D": 0.25},
            "B": {"A": 0.25, "B": 1, "C": 0.75, "D": 0.5},
            "C": {"A": 0.25, "B": 0.5, "C": 1, "D": 0.75},
            "D": {"A": 0.25, "B": 0.5, "C": 0.75, "D": 1}
        }
        return score_map.get(correct_option, {}).get(answer, 0)
    else:
        # If options are different or not in the specified order
        return 1 if answer == correct_option else 0


def map_scores_to_job(scores):
    with open('Data_final.csv', mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            match = True
            for key in scores.keys():
                if abs(scores[key] - float(row[key])) > 0.0:  # Example threshold
                    match = False
                    break
            if match:
                return row['job_field']
    
    return "No exact match found"

if __name__ == '__main__':
    init_db()  # Initialize the database and load questions from CSV
    app.run(debug=True)
