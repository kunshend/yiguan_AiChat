import streamlit as st
import os
from openai import OpenAI
from datetime import datetime
import json

from pyarrow.lib import large_list

# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide", # 布局
    initial_sidebar_state="expanded", # 控制的是侧边栏的状态
    menu_items={}
)

# 生成会话标识函数
def generate_session_name():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 构建新的会话对象
        session_data = {
            "nick_name": st.session_state.nick_name,
            "nature": st.session_state.nature,
            "current_session": st.session_state.current_session,
            "messages": st.session_state.messages
        }

        # 如果 sessions 目录不存在, 则创建
        if not os.path.exists("sessions"):
            os.mkdir("sessions")

        # 保存会话数据
        with open(f"sessions/{st.session_state.current_session}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

# 加载所有的会话列表信息
def load_sessions():
    session_list = []
    # 加载sessions目录下的文件
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
    session_list.sort(reverse=True) # 排序, 降序排列
    return session_list

# 加载指定的会话信息
def load_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            # 读取会话数据
            with open(f"sessions/{session_name}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
                st.session_state.current_session = session_name
    except Exception:
        st.error("加载会话失败!")

# 删除会话信息函数
def delete_session(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json") # 删除文件
            # 如果删除的是当前会话, 则需要更新消息列表
            if session_name == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_name()
    except Exception:
        st.error("删除会话失败!")



# 大标题
st.title("易观AI数据分析专家")

# Logo
st.logo("./resource/易观分析图标.png")

# 系统提示词
system_prompt = """
      你是一名专业、严谨、高效的【易观分析 数据分析专家】。
你的名字是：%s

你的定位：服务于易观分析公司内部数据分析部门，专注于业务分析、数据解读、报表逻辑、指标体系、用户行为分析、数据可视化建议、数据结论输出。

你的工作规则（必须严格遵守）：
1. 只输出**专业、简洁、可落地**的数据分析内容，不闲聊、不编造数据。
2. 回答风格：正式、商务、逻辑清晰、结构分明，适合职场汇报。
3. 擅长领域：
   - 用户行为分析（易观分析核心业务）
   - 指标体系搭建、DAU/MAU/留存/转化/漏斗分析
   - 数据报表解读、异常波动定位
   - SQL 逻辑、数据口径解释
   - 业务问题分析思路
   - 数据可视化方案建议
4. 遇到业务问题，优先从**数据角度**给出推理过程。
5. 若涉及易观分析产品相关知识，保持专业、中立、内部顾问口吻。
6. 不生成无关内容，不扮演其他角色，专注数据分析工作支持。

你永远记住：
你是【易观分析 内部数据分析助手】，为数据部门提供专业支持。
你的最擅长的是：%s
    """

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []
# 昵称
if "nick_name" not in st.session_state:
    st.session_state.nick_name = "易观分析的AI助手"
# 性格
if "nature" not in st.session_state:
    st.session_state.nature = "擅长用户和业务分析"
# 会话标识
if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

# 展示聊天信息
st.text(f"会话名称: {st.session_state.current_session}")
for message in st.session_state.messages: # {"role": "user", "content": prompt}
    st.chat_message(message["role"]).write(message["content"])

# 创建与AI大模型交互的客户端对象 (DEEPSEEK_API_KEY 环境变量的名字, 值就是DeepSeek的API_KEY的)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")


# 左侧的侧边栏 - with: streamlit中上下文管理器
with st.sidebar:
    # 会话信息
    st.subheader("易观分析的AI控制面板")

    # 新建会话
    if st.button("新建会话", width="stretch", icon="✏️"):
        # 1. 保存当前会话信息
        save_session()

        # 2. 创建新的会话
        if st.session_state.messages: # 如果聊天信息非空, True; 否则,  False
            st.session_state.messages = []
            st.session_state.current_session = generate_session_name()
            save_session()
            st.rerun()  # 重新运行当前页面


    # 会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
           # 加载会话信息
           # 三元运算符: 如果条件为真, 则返回第一个表达式的值; 否则, 返回第二个表达式的值 --> 语法: 值1 if 条件 else 值2
           if st.button(session, width="stretch", icon="📄", key=f"load_{session}", type="primary" if session == st.session_state.current_session else "secondary"):
               load_session(session)
               st.rerun()
        with col2:
            # 删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"delete_{session}"):
                delete_session(session)
                st.rerun()

    # 分割线
    st.divider()

    # 伴侣信息
    st.subheader("技能信息")
    # 昵称输入框



    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    # 性格输入框
    nature = st.text_area("功能", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature




# 消息输入框
prompt = st.chat_input("请输入您要问的问题")
if prompt: # 字符串会自动转换为布尔值, 如果字符串非空, 则为True; ""否则为False
    st.chat_message("user").write(prompt)
    print("----------> 调用AI大模型, 提示词: ", prompt)
    # 保存用户输入的提示词
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt % (st.session_state.nick_name, st.session_state.nature)},
            *st.session_state.messages
        ],
        stream=True
    )

    # 输出大模型返回的结果 (流式输出的解析方式)
    response_message = st.empty() # 创建一个空的组件, 用于展示大模型返回的结果

    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message("assistant").write(full_response)

    # 保存大模型返回的结果
    st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 保存会话信息
    save_session()