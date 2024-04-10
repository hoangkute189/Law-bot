from dotenv import load_dotenv
load_dotenv()

import json

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

from .chat_engine.chat import ChatEngine, generate_queries
# from .chat_engine.intent import intent_classification
from .chat_engine.testIntent import intent_classification
import time

chatEngine = ChatEngine()


class ChatEngineView(APIView):
    
    def post(self, request ,format=None):
        question = request.data.get('question', None)

        if question is None:
            return Response({'response': 'Không nhận được câu hỏi!!!'}, status=status.HTTP_400_BAD_REQUEST)

        intent = json.loads(intent_classification(question))
        print("INTENT:")
        print(intent)

        if intent['response'] == "Chào hỏi":
            return Response({'response': "Xin chào, tôi là trợ lý ảo có thể trả lời các câu hỏi về pháp luật, tôi có thể giúp gì cho bạn?"}, status=status.HTTP_200_OK)
        elif intent['response'] == "Chủ đề khác":
            return Response({'response': "Câu hỏi của bạn không hợp lệ, hoặc không liên quan đến Pháp Luật. Vui lòng kiểm tra lại và cung cấp thêm thông tin cho tôi"}, status=status.HTTP_200_OK)
        else:

            start_time = time.time()
            queries = generate_queries(question)
            end_rewrite_query_time = time.time()
            elapsed_rewrite_time = end_rewrite_query_time - start_time

            response, references = chatEngine.chat_en(queries, question)
            end_total_time = time.time()
            elapsed_total_time = end_total_time - start_time

            print(f"Query expansion time: {elapsed_rewrite_time}")
            print(f"Total time: {elapsed_total_time}")
            return Response({'response': response, 'references': references}, status=status.HTTP_200_OK)
    # def post(self, request ,format=None):
    #     question = request.data.get('question', None)

    #     if question is None:
    #         return Response({'response': 'Không nhận được câu hỏi!!!'}, status=status.HTTP_400_BAD_REQUEST)

    #     queries = generate_queries(question)
    #     response = ChatEngine()
    #     response, references = response.chat_en(queries, question)

    #     return Response({'response': response}, status=status.HTTP_200_OK)


def get_template(request):
    if request.method == 'POST':
        question = request.data.get('question', None)

        if question is None:
            return render(request, 'engine/component.html', {'response':"Không nhận được câu trả lời!!!"})

        queries = generate_queries(question)
        response = ChatEngine()
        response = response.chat_en(queries, question)
        return render(request, 'engine/component.html', {'response':response})

    return render(request, 'engine/component.html', {'response':"ERROR!!!"})