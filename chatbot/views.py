from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from groq import Groq
import logging
import re

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the Groq client with API key (consider using environment variables)
client = Groq(api_key="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")

class ChatQuery(View):
    def get(self, request):
        # Render the HTML template for the chatbot
        return render(request, 'chatbot.html', {'history': request.session.get('chat_history', [])})

    def post(self, request):
        data = request.POST
        user_query = data.get("query", "")  # Get the user's query

        try:
            # Generate chat completion
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that answers positive questions, and your name is WetaAI."
                    },
                    {
                        "role": "user",
                        "content": user_query,
                    },
                ],
                model="llama3-8b-8192",
                temperature=0.5,
                max_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )

            # Prepare response
            bot_response = chat_completion.choices[0].message.content
            
            # Format response to handle lists and code blocks
            formatted_response = self.format_response(bot_response)

            # Update session history
            chat_history = request.session.get('chat_history', [])
            chat_history.append({'role': 'user', 'content': user_query})
            chat_history.append({'role': 'bot', 'content': formatted_response})
            request.session['chat_history'] = chat_history  # Store updated history

            # Return response as JSON
            return JsonResponse({'response': formatted_response})

        except Exception as e:
            logger.error(f"Error processing chat query: {e}")
            return JsonResponse({'error': 'Failed to get a response from the chat service.'}, status=500)

    def format_response(self, response):
        # Format lists with line breaks
        response = re.sub(r'^\s*-\s+', '<br>', response, flags=re.MULTILINE)
        response = re.sub(r'^\s*\*\s+', '<br>', response, flags=re.MULTILINE)

        # Replace triple backticks with HTML <pre> and <code> tags for code blocks
        response = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', response, flags=re.DOTALL)

        # Replace single backticks with <code> for inline code
        response = re.sub(r'`([^`]+)`', r'<code>\1</code>', response)

        # Format lists into HTML <ul> or <ol>
        response = self.format_list(response)

        return response

    def format_list(self, response):
        lines = response.split('\n')
        formatted_response = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                if not in_list:
                    formatted_response.append('<ul>')
                    in_list = True
                formatted_response.append(f'<li>{line[2:]}</li>')  # Remove '- ' or '* '
            elif line and line[0].isdigit() and line[1] == '.':
                if not in_list:
                    formatted_response.append('<ol>')
                    in_list = True
                formatted_response.append(f'<li>{line[line.index(".") + 1:].strip()}</li>')  # Get the content after the number
            else:
                if in_list:
                    formatted_response.append('</ul>' if line.startswith('- ') or line.startswith('* ') else '</ol>')
                    in_list = False
                formatted_response.append(line)  # Regular text
        
        if in_list:
            formatted_response.append('</ul>' if line.startswith('- ') or line.startswith('* ') else '</ol>')

        return '\n'.join(formatted_response)

def index(request):
    return render(request, 'index.html')
