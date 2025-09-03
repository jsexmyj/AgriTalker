用langgragh来构建agent
目前初步采用的workflow的方式，但是本项目LLM是重点，所以这部分的checkpoint，记忆功能这些都需要考虑的

class AgentState(TypedDict):
    messages: List[BaseMessage]  # 对话历史
    # 可以添加更多字段，如 user_info, file_path 等