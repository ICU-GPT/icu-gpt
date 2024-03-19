import autogen
from autogen import ConversableAgent
from .prompt import *
from .f import run_sql
from ..utils import is_termination_msg
from functools import partial
from typing import Optional,List,Callable,Any

class ICU():
    def __init__(self,db_conn=None,llm_config=None,constom_sql=None,constom_template=None,show_sql=True):
       
       if db_conn is None:    
           raise ""
       self.conn = db_conn
       self.llm_config = llm_config
       self.sql = constom_sql if constom_sql else ''
       self.data = ''
       self.prompt_template = constom_template if constom_template else POSTGRES_PROMPT
       self.show_sql=show_sql
       self.user_proxy = autogen.UserProxyAgent(
        name="ICUagent",
        system_message=USER_PROXY_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        llm_config= self.llm_config,
        is_termination_msg=is_termination_msg,
        )
    # SQl gen agent - generates the sql query
       self.sql_agent = autogen.AssistantAgent(
        name="DB-agent",
        llm_config=self.llm_config,
        system_message=DB_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        )
    # SQl query agent - generates the sql query data
       self.data_agent = autogen.AssistantAgent(
        name="Data-agent",
        llm_config=self.llm_config,
        system_message=DATA_PROMPT,
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        )
    # Registry run_sql tools functions
       runsql = partial(run_sql,conn=self.self.conn,show_sql=self.show_sql)
       self.registry_tools(runsql,self.user_proxy,self.data_agent,"Use pandas run SQL")
    
    def sql_chat(self,input,tables:Optional[List[str]] = None):
        tables_info =self.conn.get_table_info(tables)
        prompt= self.prompt_template.format(input=input,tables_infos=tables_info)
        self.user_proxy.initiate_chat(self.sql_agent, clear_history=True, message=prompt)
        
    def data_chat(self,prompt,tables:Optional[List[str]] = None):
        tables_info =self.conn.get_table_info(tables)
        prompt= self.prompt_template.format(input=input,tables_infos=tables_info)
        groupchat = autogen.GroupChat(
            agents=[self.sql_agent, self.data_agent],
            messages=[],
            max_round=10,
        )
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=self.llm_config)
        self.user_proxy.initiate_chat(manager, clear_history=True, message=prompt)

    def registry_tools(f: Callable[..., Any],caller:ConversableAgent,executor:ConversableAgent, description: str) -> None:
          f = caller.register_for_llm(description=description)(f)
          executor.register_for_execution()(f)