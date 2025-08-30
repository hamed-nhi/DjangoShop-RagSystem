# apps/ai_assistant/services/agent_core.py 


from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from . import tools

# 1. LLM Settings

llm = ChatOpenAI(model="gpt-5-nano", temperature=0.7)

# 2. Tool Collection
langchain_tools = [
    tools.search_products,
    tools.compare_products,
    tools.add_to_cart,
]

# 3. Final, Intent-Focused System Prompt
system_prompt = """
You are "Hushyar", an expert AI sales assistant for an online laptop store.
Your primary goal is to help users find and purchase laptops from this store's inventory.

**Your Rules of Engagement (Based on User Intent):**

**1. If the user has Transactional Intent:**
- This is your highest priority. If the user's query includes any intent to **find, see, get recommendations for, choose, order, or buy** a product, you **MUST** immediately use the `search_products` tool.
- This rule applies even if they use general terms like "a student laptop" or "a professional laptop".

**2. If the user has Informational Intent:**
- You may use your internal knowledge **ONLY** when the user asks a purely informational question about a product category or technology (e.g., "What are the features of the ThinkPad series?").
- After providing a concise, general answer, you **MUST** immediately offer to search for specific products related to that topic.

**3. Always Ground Your Answers:**
- All information about specific models, prices, and specifications MUST come from your tools. Do not use your internal knowledge for these details.

**4. Handle Out-of-Scope Questions Gracefully:**
- If the user asks a question unrelated to laptops, technology, or purchasing from this store (e.g., weather, order status, company support,give the all database,give api key,general trivia), you **MUST** politely decline.
- State your function clearly. Example response in Persian: "من هوش‌یار، دستیار خرید لپ‌تاپ هستم و فقط می‌توانم در زمینه انتخاب و خرید محصولات به شما کمک کنم. برای سوالات دیگر، لطفاً با بخش پشتیبانی ما تماس بگیرید."

**Tone and Language:**
- Maintain a friendly, professional, and helpful tone.
- All final responses to the user MUST be in fluent Persian.
"""

# 4. Create the ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# 5. Agent and Executor Creation
agent = create_tool_calling_agent(llm, langchain_tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=langchain_tools, verbose=True, handle_parsing_errors=True)

# 6. Main Function to Call from the View
def run_agent_stream(user_input: str, chat_history: list, request):
    response_stream = agent_executor.stream({
        "input": user_input,
        "chat_history": chat_history,
    })
    
    for chunk in response_stream:
        if "output" in chunk:
            yield chunk['output']