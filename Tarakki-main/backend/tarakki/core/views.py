import random
from django.shortcuts import redirect, render
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .models import StudentProfile
from .forms import SignInForm, SignUpForm
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import User, StudentProfile
import os
import csv
import logging
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from django.core.exceptions import ValidationError
import json
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
import json
import joblib
import pandas as pd

loaded_mlp = joblib.load('mlp_model.pkl')
scaler = joblib.load('scaler.pkl')
label_encoder = joblib.load('label_encoder.pkl')
logger = logging.getLogger(__name__)

import plotly.express as px
from datetime import datetime, timedelta
# Create your views here.
def home(request):
    return render(request,"landing/home.html")


def signin(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'landing/signin.html', {'error': 'Invalid email format'})
        
        # Check if user exists
        if not User.objects.filter(email=email).exists():
            return render(request, 'landing/signin.html', {'error': 'No account found with this email'})
        
        # Attempt authentication
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('/dash')  # Redirect to a home or dashboard page
        else:
            # At this point, the user exists but the password is wrong
            return render(request, 'landing/signin.html', {'error': 'Incorrect password'})
    
    return render(request, 'landing/signin.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save()
            # Optionally, create a student profile with additional data
            StudentProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            return redirect('home')  # Redirect to a home or dashboard page
        else:
            print("Form errors:", form.errors)  # Print form errors for debugging
    else:
        form = SignUpForm()
    return render(request, 'landing/signup.html', {'form': form})

# @login_required(login_url='/signin')
def dashboard_home(request):
    # Generate random data using plain Python
    prediction = makeprediction(request.user)
    print(prediction)
    days = [datetime(2024, 1, 1) + timedelta(days=i) for i in range(30)]
    temperatures = [random.randint(20, 35) for _ in range(30)]

# Create the line chart
    fig = px.line(
        x=days,
        y=temperatures,
        title="Random Temperature Data over 30 Days",
        labels={"x": "Date", "y": "Temperature (°C)"}
    )
    chart = fig.to_html(full_html=False, default_height=500, default_width=600)

    #pie chart
    data = {
    'section': ['Math', 'English', 'Reasoning', 'General Knowledge', 'Computer Science',
                'Logical Thinking', 'Data Interpretation', 'Quantitative Aptitude', 
                'Verbal Ability', 'Non-Verbal Reasoning'],
    'score': [85, 75, 90, 65, 80, 88, 77, 92, 84, 70],
    'time_allocated': [30, 25, 35, 20, 30, 30, 30, 40, 35, 25]  # Example of custom data
}
    df = pd.DataFrame(data)
    fig = px.pie(df, values='score', names='section',
             title='Aptitude Test Scores',
             hover_data=['time_allocated'], labels={'time_allocated': 'Time Allocated (min)'})
    pie_chart = fig.to_html(full_html=False, default_height=500, default_width=600)

    skill_data = {
    'Skill': ['Coding', 'Problem Solving', 'Communication', 'Teamwork', 'Creativity', 'Attention to Detail'],
    'Proficiency': [85, 90, 75, 80, 60, 88]
}
    df = pd.DataFrame(skill_data)
    fig = px.line_polar(df, r='Proficiency', theta='Skill', line_close=True, title="Skill Proficiency Radar Chart")
    radar_chart = fig.to_html(full_html=False, default_height=500, default_width=500)

    career_fit_data = {
    'Career': ['Data Scientist', 'Financial Analyst', 'Software Engineer', 'Marketing Specialist', 'Graphic Designer'],
    'Fit Score': [90, 85, 88, 75, 70]
}
    df = pd.DataFrame(career_fit_data)
    fig = px.bar(df, x='Career', y='Fit Score', title="Career Fit Based on Aptitude Test")
    bar_chart = fig.to_html(full_html=False, default_height=500, default_width=600)

    context = {'chart': radar_chart,"pie_chart":pie_chart,"bar_chart":bar_chart}
    return render(request, 'dashboard/dash-home.html',context)

def dashboard_roadmap(request):
    career = request.GET.get('career', None)
    print(career)
    if career:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Generate Roadmap for a student who wants to pursue a career in {career}"
            "in India, starting from 10th grade to graduation and add steps like subjects, skills, "
            "and extracurricular activities. Also suggests collegese and courses to pursue and the approximate cost for the education and duration. It should be in an array of Python dictionaries, "
            "each containing 'title', 'description', and a 'steps' field breaking down the "
            "description into further 'steps' in detail with array of dictionary 'title' and 'decription'.The description should be in detail for each steps.Strictly follow the format. The initial key should be 'roadmap' which contains the array. IMPORTANT: The output should be a valid JSON file. Don't use markdown formatting"
        )

        response = model.generate_content(prompt)
        print(response.text)

        try:
            # Remove the triple backticks and any leading/trailing spaces
            cleaned_response = response.text.strip('```json').strip('```').strip()
            
            # Parse the JSON response
            parsed_data = json.loads(cleaned_response)
            
            # Extract the roadmap content
            items = parsed_data.get('roadmap', [])  # Extract 'roadmap' key if it exists
            
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            items = []  # Fallback in case of parsing failure

        # Prepare context for rendering
        context = {'items': items}
        print(context)

        return render(request, 'dashboard/dash-roadmap.html', context)
    else:
        return render(request, 'dashboard/roadmap-empty.html')

def dashboard_settings(request):
    return render(request, 'dashboard/settings.html')





def load_questions():
    # Dictionary to store questions by parameter
    questions_by_param = {}
    csv_file_path = os.path.join(os.path.dirname(__file__), 'your_data_2.csv')  # Adjust path if needed

    # Reading the CSV and categorizing questions by parameter
    with open(csv_file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            param = row['parameter']
            if param not in questions_by_param:
                questions_by_param[param] = []
            questions_by_param[param].append({
                'parameter': param,
                'question_text': row['question_text'],
                'option_a': row['A'],
                'option_b': row['B'],
                'option_c': row['C'],
                'option_d': row['D'],
                'correct_option': row['correct_option']
            })

    # Select 10 random questions for each parameter
    selected_questions = []
    for param, questions in questions_by_param.items():
        selected_questions.extend(random.sample(questions, min(10, len(questions))))

    return selected_questions

def start_test(request):
    # This is where we start the test and display the questions
    if request.method == 'GET':
        questions = load_questions()
        test_id = str(uuid.uuid4())
        request.session['questions'] = questions  # In start_test
        # return render(request, 'dashboard/dash-test.html', {'questions': questions})
        return JsonResponse({'test_id': test_id,'questions': questions})  # Ensure this returns JSON
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
def validate_option(option,options):
    # valid_options = ["A", "B", "C", "D"]
    return option in options

def calculate_score(answers, correct_options, parameter, options):
    logger.info(f'Answers: {answers}, Correct Options: {correct_options}, Options: {options}')

    # score = 0
    # score_map = {
    #     "A": {"A": 1, "B": 0.75, "C": 0.5, "D": 0.25},
    #     "B": {"A": 0.25, "B": 1, "C": 0.75, "D": 0.5},
    #     "C": {"A": 0.25, "B": 0.5, "C": 1, "D": 0.75},
    #     "D": {"A": 0.25, "B": 0.5, "C": 0.75, "D": 1}
    # }
    # for answer, correct_option in zip(answers, correct_options):
    #     if answer is None:
    #         score+=0

    # for answer, correct_option in zip(answers, correct_options):
    #     if options == ["Strongly Disagree", "Disagree", "Agree", "Strongly Agree"]:
    #         score += score_map.get(correct_option, {}).get(answer, 0)
    #     else:
    #         score += 1 if answer == correct_option else 0

    # return score 
    use_score_map = parameter in ['O_score', 'C_score', 'E_score', 'A_score', 'N_score']
    score = 0
    
    if use_score_map:
        score_map = {
            "A": {"A": 1, "B": 0.75, "C": 0.5, "D": 0.25},
            "B": {"A": 0.25, "B": 1, "C": 0.75, "D": 0.5},
            "C": {"A": 0.25, "B": 0.5, "C": 1, "D": 0.75},
            "D": {"A": 0.25, "B": 0.5, "C": 0.75, "D": 1}
        }
        for answer, correct_option in zip(answers, correct_options):
            if answer is None:
                score+=0
            score += score_map.get(correct_option, {}).get(answer, 0)
    else:
        for answer, correct_option in zip(answers, correct_options):
            if answer is None:
                score+=0
            score += 1 if answer == correct_option else 0

    return score


def submit_test(request):
    if request.method == 'POST':
        questions = request.session.get('questions', [])
        if not questions:
            return JsonResponse({'error': 'No questions found in session'}, status=400)

        data = json.loads(request.body)
        print("Data: ",data)
        answers = data['answers']
        print("Answers: ",answers)

        if not answers:
            return JsonResponse({'error': 'No answers submitted'}, status=400)

        # Initialize scores for each parameter
        scores = {param: 0 for param in [
            'O_score', 'C_score', 'E_score', 'A_score', 'N_score',
            'Numerical_Aptitude', 'Spatial_Aptitude', 'Perceptual_Aptitude',
            'Abstract_Reasoning', 'Verbal_Reasoning'
        ]}

        correct_options_by_param = {param: [] for param in scores}
        answers_by_param = {param: [] for param in scores}

        # Group answers and correct options by parameter
        for i, question in enumerate(questions):
            param = question['parameter']
            correct_options_by_param[param].append(question['correct_option'])
            # answers_by_param[param].append(answers[i])
            if i < len(answers):
                answers_by_param[param].append(answers[i])
            else:
                answers_by_param[param].append(None)

        print("Answers by parameter: ",answers_by_param)
        print("Correct option by parameter: ",correct_options_by_param)
        # Calculate the score for each parameter separately
        for param in scores:
            scores[param] = calculate_score(
                answers_by_param[param],
                correct_options_by_param[param],
                param,
                ["A", "B", "C", "D","None"]
            )
        print("Scores: ",scores)
        qualities = determine_qualities(scores)
        print("Qualities: ",qualities)
        # Return only individual parameter scores (no total_score calculation)
        return JsonResponse({'scores': scores,'qualities':qualities})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)




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


def dashboard_test(request):
 
    return render(request, 'dashboard/dash-test.html')

def get_scores(user):
    try:
        # Fetch the student profile for the given user
        profile = StudentProfile.objects.get(user=user)
        # Retrieve the scores field from the profile
        scores_array = profile.scores
        return scores_array
    except StudentProfile.DoesNotExist:
        # If the profile does not exist, return an empty array or handle the error accordingly
        return []
    
def makeprediction(user):
    # Get scores from the student's profile
    scores_array = get_scores(user)

    # Check if the scores exist
    if scores_array is None:
        return "No scores available for this user."

    try:
        # Ensure the input matches the model's expected format
        sample_input = [scores_array]

        # Scale the input using the same scaler used during training
        sample_input_scaled = scaler.transform(sample_input)

        # Make the prediction
        predicted_career = loaded_mlp.predict(sample_input_scaled)

        # Decode the predicted label back to the original class
        predicted_career_label = label_encoder.inverse_transform(predicted_career)

        # Return the predicted career
        return f'Predicted Career: {predicted_career_label[0]}'
    except Exception as e:
        return f"Error in prediction: {str(e)}"
    

def interest(request):
    if request.method == 'POST':
        print("hello")
    else:
        return render(request, 'dashboard/dash-interest.html')
