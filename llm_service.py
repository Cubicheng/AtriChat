from langchain_core.prompts import PromptTemplate
from langchain.schema.runnable import RunnableSequence
from langchain_community.chat_models import ChatZhipuAI
from config_init import atri_chinese_prompt

chatglm = ChatZhipuAI(model="glm-4", temperature=0.5)

# 创建 PromptTemplate
prompt = PromptTemplate(
    template=atri_chinese_prompt,
    input_variables=["current_scene", "user_input"]
)

# 使用 RunnableSequence 替代 LLMChain
chat_llm = RunnableSequence(prompt | chatglm)

# 定义生成回复的函数
def generate_atri_response(user_input, current_scene="日常对话"):
    # 调用 RunnableSequence 生成回复
    response = chat_llm.invoke({
        "current_scene": current_scene,
        "user_input": user_input
    }).content
    print(f"ATRI: {response}")
    return response