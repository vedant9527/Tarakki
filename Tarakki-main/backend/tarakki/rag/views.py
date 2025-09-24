from django.shortcuts import render
import google.generativeai as genai
import os
# Create your views here.
genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def chat(request):
    bot_response = ""
    user_input = ""

    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content('you are a career counsellign bot for based in india and now answer this question: '+user_input)
        bot_response = response.text


        return render(request, 'partials/chat-box.html', {'user_input': user_input, 'bot_response': bot_response})

    return render(request, 'chatbot.html', {'user_input': user_input, 'bot_response': bot_response})