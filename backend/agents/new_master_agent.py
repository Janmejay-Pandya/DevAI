import os
import json
from typing import Tuple
from chat.models import Chat
from projects.models import Project, AgentSteps


class MasterAgent:
    def __init__(self, chat_id: int):
        self.chat = Chat.objects.get(id=chat_id)
        self.project, _ = Project.objects.get_or_create(chat=self.chat)
        self.is_move_forward_question = False
    

    def handle_input(self, user_input: str, is_choice: bool) -> Tuple[str, bool]:
        yes_terms = {"yes", "y", "yeah", "yep", "sure", "absolutely", "certainly", "of course", "ok", "okay", "alright"}
        no_terms = {"no", "n", "nope", "nah", "never", "not at all", "negative", "no way", "absolutely not"}

        # if self.is_move_forward_question:
        #     if user_input.lower() in yes_terms:
        #         intent = {"intent": "approve"}
        #     elif user_input.lower() in no_terms:
        #         intent = {"intent": "reject"}
        
        request = {}

        step = self.project.current_step

        # Handle incomplete input
        if request["intent"] == "incomplete":
            return ("I couldn't understand that. Could you please rephrase it clearly?", False)

        if request["intent"] == "question":
            project_context = {
                "current_step": self.project.current_step,
                "product_description": self.project.product_description,
                "final_mvp": self.project.final_mvp,
                "design_guidelines": self.project.design_guidelines,
                "tech_stack": self.project.tech_stack,
                "deployed_url": self.project.deployed_url,
            }
            response = self._answer_user_query(intent.get("request", ""), project_context)
            return (response, False)
        
        # Handle going back to previous step (can be used anywhere in the flow)
        if request["intent"] == "go_back":
            target_step = intent.get("target_stage")
            if target_step and target_step in [choice.value for choice in AgentSteps]:
                self.project.current_step = target_step
                self.project.save()
                return (f"Alright, taking you back to the {target_step.replace('_', ' ').title()} stage.", True)
            else:
                return ("Sorry, I couldn't understand which stage to go back to.", False)

        # Handle each step's specific logic
        if step == "init":
            return self._handle_init(intent)
        elif step == "generate_mvp":
            return self._handle_generate_mvp(intent)
        elif step == "debate":
            return self._handle_debate(intent)
        elif step == "finalize_mvp":
            return self._handle_finalize_mvp(intent)
        elif step == "design":
            return self._handle_design(intent)
        elif step == "tech_stack":
            return self._handle_tech_stack(intent)
        elif step == "development":
            return self._handle_development(intent)
        elif step == "test":
            return self._handle_test(intent)
        elif step == "deploy":
            return self._handle_deploy(intent, user_input)
        elif step == "complete":
            return self._handle_complete(intent)

        return (
            "Something went wrong. Let's start over. What product would you like to build?",
            False,
        )
    
            # Individual step handlers
    
    def _handle_init(self, request):
        if self.project.product_description is None:
            if request["intent"] == "describe_product" and request.get("description"):
                self.project.product_description = request.get("description")
                self.project.save()
                return (
                    f"Got your product description. You want to make {self.project.product_description}. Should we proceed to the next stage?",
                    True
                )
            else:
                return ("Please provide a description of what you'd like to create so that we can move forward", False)
            
        if request["intent"] == "approve":
            # Update step and proceed directly to generating MVP
            self.project.current_step = "generate_mvp"
            self.project.save()
            
            # Generate MVP immediately
            generated_mvp_response = self._handle_generate_mvp()
            return generated_mvp_response
            
        elif request["intent"] == "reject":
            self.project.product_description = None
            return (
                "I understand. Let's start over. What product would you like to build?",
                False,
            )
        else:
            return ("Please confirm if you want to proceed with this product idea.", True)
