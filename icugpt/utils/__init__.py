"""
Purpose:
    Interact with the OpenAI API.
    Provide supporting prompt engineering functions.
"""

import sys
from typing import Any, Dict

# load .env file
# ------------------ helpers ------------------
       # create our terminate msg function
def is_termination_msg(content):
            have_content = content.get("content", None) is not None
            if have_content and "APPROVED" in content["content"]:
                return True
            return False