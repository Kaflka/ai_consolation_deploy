from sparkai.llm.llm import ChatSparkLLM
from sparkai.core.messages import ChatMessage
from Cxk import Cxk_text
from DingZhen import DingZhen_text
from LeiJun import LeiJun_text
from XueJie import ADXueJie_text
from CCTV import CCTV_text

class SparkChatAI:
    def __init__(self, app_id, api_secret, api_key, model_name):
        # 初始化SparkLLM
        self.spark = ChatSparkLLM(
            spark_api_url='wss://spark-api.xf-yun.com/v4.0/chat',
            spark_app_id=app_id,
            spark_api_key=api_key,
            spark_api_secret=api_secret,
            spark_llm_domain='4.0Ultra',
            streaming=False,
        )
        # 初始化消息记录列表
        self.messages = []
        self.max_history_length = 20  # 限制对话历史轮数
        self.model_name = model_name  # 保存模型名称

        # 根据模型名称选择系统模板
        if model_name == "雷军":
            self.system_template_text = LeiJun_text
        elif model_name == "丁真":
            self.system_template_text = DingZhen_text
        elif model_name == "学姐":
            self.system_template_text = ADXueJie_text
        elif model_name == "央视配音":
            self.system_template_text = CCTV_text
        else:
            self.system_template_text = Cxk_text

        # 添加系统初始消息
        self.messages.append(ChatMessage(role="system", content=self.system_template_text))

    def get_response(self, user_input):
        # 添加用户输入到对话历史
        self.messages.append(ChatMessage(role="user", content=user_input))

        # 限制消息历史长度
        if len(self.messages) > self.max_history_length * 2 + 1:
            self.messages = [self.messages[0]] + self.messages[-self.max_history_length * 2:]

        # 调用模型生成回答
        response = self.spark.generate([self.messages])

        # 获取模型回复内容
        answer = response.generations[0][0].message.content

        # 将模型回复添加到对话历史
        self.messages.append(ChatMessage(role="assistant", content=answer))

        return answer

    def reset_memory(self):
        """重置对话历史，用于清空 AI 的记忆"""
        self.messages = [ChatMessage(role="system", content=self.system_template_text)]