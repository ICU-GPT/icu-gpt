from autogen.agentchat import AssistantAgent,UserProxyAgent,GroupChat,GroupChatManager
from autogen.oai import config_list_from_models
from typing import Optional,List
import gradio as gr
import time
import os
from dotenv import load_dotenv
from .prompt import *
from ..db import db_conn,DBS
from ..utils import is_termination_msg

class ICU():
    def __init__(self,db_name='mimiciv',pg_user='postgres',pg_passwd='mimic',pg_server='mimic',llm_config=None,constom_template=None,model_list=["gpt-4","gpt-3.5"]):
       
       self.db_name = db_name
       self.pg_user = pg_user or  os.environ.get('PG_USER')
       self.pg_passwd = pg_passwd or os.environ.get('PG_PASSWD')
       self.pg_server = pg_server or os.environ.get('PG_SERVER')
       self.dbconn = db_conn(self.db_name,self.pg_user,self.pg_passwd,self.pg_server)
       self.llm_config = llm_config or {
            "temperature": 0,
            "config_list": config_list_from_models(model_list=model_list),
        }  
       ## use for store gen SQL
       self.sql = ''
       self.prompt_template = constom_template if constom_template else POSTGRES_PROMPT
 
       self.user_proxy = UserProxyAgent(
        name="ICUagent",
        system_message=USER_PROXY_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        )
    # SQl gen agent - generates the sql query
       self.sql_agent = AssistantAgent(
        name="sql-agent",
        llm_config=llm_config,
        system_message=DB_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        )
    # SQl query agent - generates the sql query data
       self.expert_agent=AssistantAgent(
        name="expert_agent",
        llm_config=llm_config,
        system_message=EXPERT_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        )

    @property
    def show_sql(self):
        ## show gen sql
        return self.sql

        # chat for gen sql   
    def sql_chat(self,prompt,tables:Optional[List[str]] = None):
        # Obtain table structure information
        table_info =self.dbconn.get_table_info(tables)
        prompt= self.prompt_template.format(input=prompt,table_info=table_info)
        groupchat = GroupChat(
            agents=[self.user_proxy,self.sql_agent, self.expert_agent],
            messages=[],
            max_round=10,
        )
        manager = GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)
        self.user_proxy.initiate_chat(manager, clear_history=True, message=prompt)
        self.sql = self.user_proxy._oai_messages[manager][-2]['content']
        print(self.sql)
        return self.sql

    @classmethod
    def from_env(cls,db_name,pg_user,pg_passwd,pg_server,model_list=["gpt-4","gpt-3.5"]):
        load_dotenv()
        llm_config = {
            "temperature": 0,
            "config_list": config_list_from_models(model_list=model_list),
        }
        return cls(db_name,pg_user,pg_passwd,pg_server,llm_config)

    def db_change(self,db_name):
        self.dbconn,_ = db_conn(db_name,self.pg_user,self.pg_passwd,self.pg_server)
        tables = self.dbconn.get_table_names()   
        return gr.update(choices=tables)    
    
    def respond(self,message,chat_history,tables):
        print(tables)
        bot_message = self.sql_chat(prompt=message,tables=tables)
        chat_history.append((message, bot_message))
        time.sleep(2)
        return "", chat_history
    
    def load_gradio(self,height=1500,server_port=8099,bot_height=400):
        with gr.Blocks(theme = gr.themes.Soft(),css=".markdown-img { max-width: 100px;max-height: 100px;}" ) as app:
            with gr.Row():
                gr.Markdown("""![](./img/logo.png)
                            """,elem_classes='markdown-img')
                gr.Markdown("""
                            &nbsp;
                            &nbsp;
                            # Beijing Tiantan Hospital Critical Care Database Analysis System 
                            """)
            with gr.Tab("SQL"):  
                with gr.Row():
                    db = gr.Dropdown(choices=DBS, label="Database")
                    tb = gr.Dropdown(choices=[],interactive=True,multiselect=True,label="Tables")
                    db.change(self.db_change,db,tb)
                with gr.Row():    
                    chatbot = gr.Chatbot(label='SQLbot',height=bot_height)
                with gr.Row():      
                    message = gr.Textbox(label='Prompt',placeholder="input you prompt...")
                with gr.Row():
                    submit = gr.Button("Submit")
                    submit.click(self.respond, inputs=[message,chatbot,tb], outputs=[message,chatbot])
                    gr.ClearButton([message, chatbot],value='Clear')    
        app.launch(height=height,server_port=server_port)