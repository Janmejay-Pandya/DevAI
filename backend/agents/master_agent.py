from typing import Tuple
from chat.models import Chat
from projects.models import Project

class MasterAgent:
    def __init__(self, chat_id: int):
        self.chat = Chat.objects.get(id=chat_id)
        self.project, _ = Project.objects.get_or_create(chat=self.chat)

    def handle_input(self, user_input: str, is_choice: bool) -> Tuple[str, bool]:
        if not is_choice:
            intent = self._interpret_feedback(user_input)
        else:
            intent = {"intent": "approve" if user_input.lower() == "yes" else "reject"}

        step = self.project.current_step

        # Handle incomplete input
        if intent["intent"] == "incomplete":
            return "I couldn't understand that. Could you please rephrase it clearly?"

        # Handle going back to previous step (can be used anywhere in the flow)
        if intent["intent"] == "go_back" and step != "init":
            previous_step = self._get_previous_step(step)
            self.project.current_step = previous_step
            self.project.save()
            return f"Going back to the {previous_step} stage. {self._get_step_prompt(previous_step)}"

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
            return self._handle_deploy(intent)
        elif step == "complete":
            return self._handle_complete(intent)
        
        return ("Something went wrong. Let's start over. What product would you like to build?", False)

    def _get_previous_step(self, current_step):
        """Return the previous step in the workflow"""
        step_sequence = ["init", "generate_mvp", "debate", "finalize_mvp", "design", "tech_stack", "development", "test", "deploy", "complete"]
        try:
            current_index = step_sequence.index(current_step)
            if current_index > 0:
                return step_sequence[current_index - 1]
            return "init"
        except ValueError:
            return "init"

    def _get_step_prompt(self, step):
        """Return a prompt relevant to the current step"""
        prompts = {
            "init": "What product would you like to build?",
            "generate_mvp": "Should I start generating the MVP features?",
            "debate": "Shall we get critiques on the MVP features?",
            "finalize_mvp": "Let's finalize the MVP based on these critiques. Proceed?",
            "design": "Should I generate design guidelines for the product?",
            "tech_stack": "Should I recommend a tech stack for implementation?",
            "development": "Ready to start development?",
            "test": "Should we begin testing the application?",
            "deploy": "Testing completed. Should we deploy the application?",
            "complete": "Your application has been deployed. Would you like to make any changes?"
        }
        return prompts.get(step, "What would you like to do next?")

    # Individual step handlers
    def _handle_init(self, intent):
        if intent["intent"] == "describe_product" or intent["intent"] == "approve":
            self.project.product_description = intent.get("request", "")
            self.project.current_step = "generate_mvp"
            self.project.save()
            return (f"Got your product description. You want to make {intent.get('request', '')}. {self._get_step_prompt('generate_mvp')}", True)
        elif intent["intent"] == "reject":
            return ("I understand. Let's start over. What product would you like to build?", False)
        else:
            return ("Please describe the product you want to build.", False)

    def _handle_generate_mvp(self, intent):
        if intent["intent"] == "approve":
            mvp = self._generate_mvp()
            self.project.mvp = mvp
            self.project.current_step = "debate"
            self.project.save()
            return (f"MVP Feature List:\n{mvp}\n\n{self._get_step_prompt('debate')}", True)
        elif intent["intent"] == "reject":
            return (f"Let's reconsider the MVP. Would you like to modify the product description?", False)
        elif intent["intent"] == "modify":
            self.project.product_description = intent.get("value", self.project.product_description)
            self.project.save()
            return ("Updated description. Regenerating MVP... Should I continue with this updated description?", True)
        else:
            return ("Should I proceed with generating the MVP features based on your description?", True)

    def _handle_debate(self, intent):
        if intent["intent"] == "approve":
            critiques = self._debate()
            self.project.critiques = critiques
            self.project.current_step = "finalize_mvp"
            self.project.save()
            return (f"Here's what each agent thinks:\n{critiques}\n\n{self._get_step_prompt('finalize_mvp')}", True)
        elif intent["intent"] == "reject":
            self.project.current_step = "generate_mvp"
            self.project.save()
            return ("Let's go back and revise the MVP features first. Can you tell me what changes you want or Should I regenerate them?", True)
        elif intent["intent"] == "modify":
            # Handle specific modification to the MVP before debate
            return ("I've noted your modifications to the MVP. Should we proceed with getting critiques now?", True)
        else:
            return ("Should we proceed with debating the MVP features to get different perspectives?", True)

    def _handle_finalize_mvp(self, intent):
        if intent["intent"] == "approve":
            final = self._finalize_mvp()
            self.project.final_mvp = final
            self.project.current_step = "design"
            self.project.save()
            return (f"Finalized MVP:\n{final}\n\n{self._get_step_prompt('design')}", True)
        elif intent["intent"] == "reject":
            return ("Let's take another look at the MVP. What changes would you like to make?", False)
        elif intent["intent"] == "modify":
            # Handle modifications to the critiques or MVP before finalizing
            return ("I've noted your suggestions. Should we finalize the MVP now with these considerations?", True)
        else:
            return ("Should we finalize the MVP based on the critiques we've received?", True)

    def _handle_design(self, intent):
        if intent["intent"] == "approve":
            design = self._generate_design()
            self.project.design_guidelines = design
            self.project.current_step = "tech_stack"
            self.project.save()
            return (f"Design guidelines:\n{design}\n\n{self._get_step_prompt('tech_stack')}", True)
        elif intent["intent"] == "reject":
            return ("Let's reconsider the design approach. Please provide what kind of design guidelines you would like instead?", False) 
        elif intent["intent"] == "modify":
            # Handle design modifications
            return ("I've noted your design preferences. Would you like me to incorporate these and continue?", True)
        else:
            return ("Should I generate design guidelines for the product?", True)

    def _handle_tech_stack(self, intent):
        if intent["intent"] == "approve":
            stack = self._generate_tech_stack()
            self.project.tech_stack = stack
            self.project.current_step = "development"
            self.project.save()
            return (f"Recommended Tech Stack:\n{stack}.\n\nIdeation and Design Completed. {self._get_step_prompt('development')}", True)
        elif intent["intent"] == "reject":
            return ("What constraints or preferences do you have for the tech stack?", False)
        elif intent["intent"] == "modify":
            # Handle tech stack modifications
            return ("I've noted your tech stack preferences. Would you like me to recommend a tech stack based on these?", True)
        else:
            return ("Should I recommend a tech stack for implementation?", True)

    def _handle_development(self, intent) -> Tuple[str, bool]:
        if intent["intent"] == "approve":
            self.project.current_step = "test"
            self.project.save()
            return ("I've started development on Features A and C. Do you have any specific changes you'd like to see?", True)
        elif intent["intent"] == "reject":
            return ("Let's revisit the development plan. What concerns do you have?", False)
        elif intent["intent"] == "modify":
            return ("I've made the suggested changes. Do you have any more changes you'd like to make?", True)
        elif intent["intent"] == "complete":
            self.project.current_step = "test"
            self.project.save()
            return (f"Great. {self._get_step_prompt('test')}", False)
        else:
            return ("Should we start the development phase now?", True)

    def _handle_test(self, intent):
        if intent["intent"] == "approve":
            self.project.current_step = "deploy"
            self.project.save()
            return (f"Testing completed. All test cases passed. {self._get_step_prompt('deploy')}", True)
        elif intent["intent"] == "reject":
            self.project.current_step = "development"
            self.project.save()
            return ("Let's go back to development to fix the issues. What needs to be addressed?", False)
        elif intent["intent"] == "modify":
            # Handle test modifications
            return ("I've noted your testing suggestions. Should we proceed with these adjustments?", True)
        else:
            return ("Should we proceed with testing the application?", True)

    def _handle_deploy(self, intent):
        if intent["intent"] == "approve":
            self.project.current_step = "complete"
            self.project.save()
            return ("Your application has been deployed! You can view it at http://localhost:3000", False)
        elif intent["intent"] == "reject":
            return ("What concerns do you have about deployment?", False)
        elif intent["intent"] == "modify":
            # Handle deployment modifications
            return ("I've noted your deployment preferences. Should we proceed with deployment?", True)
        else:
            return ("Should we deploy the application now?", True)

    def _handle_complete(self, intent):
        if intent["intent"] == "modify":
            # Handle post-deployment modifications
            return ("What specific changes would you like to make to the deployed application?", False)
        if intent["intent"] == "reject":
            return ("Thank you! Bye Bye!", False)
        else:
            return ("Your application is complete and deployed. Would you like to make any changes?", True)

    # Helper methods (same as original)
    def _generate_mvp(self):
        # return generate_mvp_features(self.project.product_description)
        return "Features: A, B and C"

    def _debate(self):
        # return debate_mvp_features(self.project.mvp)
        return "We should do A and C and not B"

    def _finalize_mvp(self):
        # return finalize_mvp(self.project.mvp, self.project.critiques)
        return "A and C"

    def _generate_design(self):
        # return brainstorm_design_guidelines(self.project.product_description)
        return "Font: Roboto."

    def _generate_tech_stack(self):
        # return decide_tech_stack(self.project.product_description, self.project.final_mvp, self.project.design_guidelines)
        return "react app."

    def _interpret_feedback(self, feedback: str) -> dict:
        """
        Interpret user feedback and classify the intent.
        Return a dict like {"intent": "describe_product", "request": "user's request"} or
        {"intent": "modify", "request": "user's suggested changes"}
        Or {"intent": "approve"} / {"intent": "reject"} / {"intent": "incomplete"} / {"intent": "go_back"}
        """
        prompt = f"""
        User said: "{feedback}"
        
        Interpret the user's intent. Is the user giving instruction, approving, rejecting, requesting to go back, or modifying something?
        Return JSON like:
        {{
            "intent": "modify",
            "request": "I want the font to be Roboto",
            "value": "Roboto font"
        }}
        """
        # In a real implementation, you would use an LLM to interpret the intent
        # return json.loads(some_llm.predict(prompt))
        
        # For now, just return a dummy response for demonstration
        return {"intent": "approve", "request": feedback}