import openai
import os
# import IPython
from dotenv import load_dotenv
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def intent_classification(ques):
    PROMPT = '''
    Bạn là một người phân loại câu hỏi chuyên nghiệp. Nhiệm vụ của bạn là khi tôi cung cấp cho bạn một câu hỏi được kí hiệu bằng thẻ <QUES> bạn hãy phân loại cho tôi câu hỏi này thuộc vào
    chủ đề nào trong 3 chủ đề sau: Chào hỏi , hỏi đáp pháp luật, các chủ đề khác không liên quan đến chào hỏi.


    # Quy tắc trả lời: Khi bạn trả lời cho tôi hãy cho tôi biết nội dung câu hỏi mà tôi sẽ đưa cho bạn thuộc vào chủ đề nào và trả lời bằng các label tương ứng. Nếu nội dung câu hỏi thuộc
    về chủ đề chào hỏi hãy trả lời là 1, nếu nội dung câu hỏi thuộc về chủ đề pháp luật hãy trả lời là 2 và nếu nội dung câu hỏi thuộc về chủ đề khác hãy trả lời là 3.

    # Định dạng trả lời: Định dạng trả lời mà bạn đưa cho tôi sẽ có dạng là một dictionary với key có tên là response và value là nhãn mà bạn đã phân loại. Giống ví dụ sau: {"response": 1}


    Sau đây là câu hỏi mà tôi cung cấp cho bạn:
    <QUES>=```{ques}```
    '''

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": PROMPT},
        ],
        temperature=0,
    )


    return response.choices[0].message.content

