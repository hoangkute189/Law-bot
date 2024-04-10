import openai
import os
# import IPython
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
import json

def intent_classification(ques):
    PROMPT = '''
    Bạn là một người phân loại câu hỏi chuyên nghiệp. Nhiệm vụ của bạn là phân loại cho tôi câu truy vấn này thuộc vào
    chủ đề nào trong 4 chủ đề sau: Chào hỏi, Hỏi đáp pháp luật, Câu hỏi lý thuyết, hoặc Chủ đề khác. Trong đó:
    
    - Chào hỏi: là các câu mang tính chào hỏi, hỏi tên, nguồn gốc.
    - Hỏi đáp pháp luật: là các câu hỏi có chủ đề liên quan đến pháp luật.
    - Câu hỏi lý thuyết: là các câu hỏi lý thuyết rõ ràng, có thể liên quan đến lý thuyết pháp luật.
    - Chủ đề khác: là các câu không liên quan đến các chủ đề trên, những câu thô tục, bạo lực, hoặc không rõ ràng.

    # Định dạng trả lời: Định dạng trả lời mà bạn đưa cho tôi sẽ có dạng là một dictionary với key có tên là response và value là nhãn mà bạn đã phân loại. Giống ví dụ sau: {"response": 'pháp luật'}
    '''

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
               "role": "system",
               "content": PROMPT
            },
            {
               "role": "user",
               "content": ques
            }
         ],
        temperature=0,
    )


    return response.choices[0].message.content
 

intent = intent_classification(ques="Bạn là ai?")
print(intent)

# with open('data_simple_rag.json', 'r') as file:
#         # Load JSON data from the file
#         data_list= json.load(file)

# intent = []
# for ques in data_list:
#    output = {
#       "question": ques['question'],
#       "answer": intent_classification(ques=ques['question'])
#    }
#    intent.append(output)
   
# print(intent)
    