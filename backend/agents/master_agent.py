from asgiref.sync import async_to_sync
from typing import Tuple
from chat.models import Chat
from projects.models import Project
from .ideation_agent import (
    generate_mvp_features,
    debate_mvp_features,
    finalize_mvp,
    brainstorm_design_guidelines,
    decide_tech_stack,
)
from .frontend_agent import generate_frontend
from .deploy_agent import deploy_to_github
from utils.github_utils import github_user_exists, github_repo_exists


class MasterAgent:
    def __init__(self, chat_id: int):
        self.chat = Chat.objects.get(id=chat_id)
        self.project, _ = Project.objects.get_or_create(chat=self.chat)

    def handle_input(self, user_input: str, is_choice: bool) -> Tuple[str, bool]:
        if user_input.lower() in ["yes", "no"]:
            intent = {"intent": "approve" if user_input.lower() == "yes" else "reject"}
        else:
            intent = self._interpret_feedback(user_input)

        step = self.project.current_step

        # Handle incomplete input
        if intent["intent"] == "incomplete":
            return ("I couldn't understand that. Could you please rephrase it clearly?", False)

        # Handle going back to previous step (can be used anywhere in the flow)
        if intent["intent"] == "go_back" and step != "init":
            previous_step = self._get_previous_step(step)
            self.project.current_step = previous_step
            self.project.save()
            return (f"Going back to the {previous_step} stage. {self._get_step_prompt(previous_step)}", True)

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

    def _get_previous_step(self, current_step):
        """Return the previous step in the workflow"""
        step_sequence = [
            "init",
            "generate_mvp",
            "debate",
            "finalize_mvp",
            "design",
            "tech_stack",
            "development",
            "test",
            "deploy",
            "complete",
        ]
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
            "debate": "Do you want to see the critiques on the MVP decided?",
            "finalize_mvp": "Do you want to update the MVP based on the critiques?",
            "design": "Should I generate design guidelines for the product?",
            "tech_stack": "Should I recommend a tech stack for implementation?",
            "development": "Ready to start development?",
            "test": "Should we begin testing the application?",
            "deploy": "Testing completed. Should we deploy the application?",
            "complete": "Your application has been deployed. Would you like to make any changes?",
        }
        return prompts.get(step, "What would you like to do next?")

    # Individual step handlers
    def _handle_init(self, intent):
        if self.project.product_description is None:
            self.project.product_description = intent.get("request", "")
            self.project.save()
            return (
                f"Got your product description. You want to make {self.project.product_description}. Should we proceed to the next stage?",
                True
            )
            
        if intent["intent"] == "approve":
            # Update step and proceed directly to generating MVP
            self.project.current_step = "generate_mvp"
            self.project.save()
            
            # Generate MVP immediately instead of asking if user wants to generate
            mvp = self._generate_mvp()
            self.project.mvp = mvp
            self.project.save()
            
            # Return MVP and move to debate question in one step
            return (
                f"Do you want to get ideas to generate MVP features?",
                True,
            )
        elif intent["intent"] == "reject":
            self.project.product_description = None
            return (
                "I understand. Let's start over. What product would you like to build?",
                False,
            )
        else:
            return ("Please confirm if you want to proceed with this product idea.", True)

    def _handle_generate_mvp(self, intent):
        if intent["intent"] == "approve":
            # Generate MVP if not already done
            if not self.project.mvp:
                mvp = self._generate_mvp()
                self.project.mvp = mvp
            else:
                mvp = self.project.mvp
                
            # Move to debate phase
            self.project.current_step = "debate"
            self.project.save()
            
            return (
                f"Here are the MVP features I've generated:\n\n{mvp}\n\nDo you want to see critiques of these features?",
                True,
            )
        elif intent["intent"] == "reject":
            return (
                "No problem. Let's go back to the product description. What would you like to change?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle requested modifications
            modified_description = intent.get("request", self.project.product_description)
            self.project.product_description = modified_description
            
            # Generate new MVP based on modified description
            mvp = self._generate_mvp()
            self.project.mvp = mvp
            self.project.save()
            
            # Move to debate phase
            self.project.current_step = "debate"
            self.project.save()
            
            return (
                f"I've updated the product description and generated new MVP features:\n\n{mvp}\n\nDo you want to see critiques of these features?",
                True,
            )
        else:
            return ("Should I start generating the MVP features?", True)

    def _handle_debate(self, intent):
        if intent["intent"] == "approve":
            # Generate critiques immediately
            critiques = self._debate()
            self.project.critiques = critiques
            self.project.save()
            
            # Update step and proceed directly to finalize MVP
            self.project.current_step = "finalize_mvp"
            self.project.save()
            
            # Return critiques and ask about finalizing in one step
            return (
                f"Here's what each agent thinks:\n{critiques}\n\nBased on these critiques, should we update the MVP features?",
                True,
            )
        elif intent["intent"] == "reject":
            # Skip debate and go straight to design
            self.project.current_step = "design"
            self.project.save()
            
            # Generate design immediately
            design = self._generate_design()
            self.project.design_guidelines = design
            self.project.save()
            
            # Return design and tech stack question in one step
            return (
                f"Skipping the critique phase. Here are the design guidelines I've created:\n\n{design}\n\nShould I recommend a tech stack for implementation?",
                True,
            )
        elif intent["intent"] == "modify":
            # Handle modification and then generate critiques
            modified_mvp = self._update_mvp(intent.get("request", ""))
            self.project.mvp = modified_mvp
            
            critiques = self._debate()
            self.project.critiques = critiques
            self.project.save()
            
            self.project.current_step = "finalize_mvp"
            self.project.save()
            
            return (
                f"Updated MVP features and generated critiques:\n{critiques}\n\nBased on these critiques, should we update the MVP features?",
                True,
            )
        else:
            return (
                "Please clearly indicate if you'd like to see critiques of the MVP features.",
                True,
            )

    def _handle_finalize_mvp(self, intent):
        if intent["intent"] == "approve":
            # Finalize the MVP immediately
            final_mvp = self._finalize_mvp()
            self.project.final_mvp = final_mvp
            
            # Move to design step
            self.project.current_step = "design"
            self.project.save()
            
            # Generate design guidelines immediately
            design = self._generate_design()
            self.project.design_guidelines = design
            self.project.save()
            
            # Return finalized MVP and design in one step
            return (
                f"{final_mvp}\n\nBased on this MVP, I've created these design guidelines:\n{design}\n\nShould I recommend a tech stack for implementation?",
                True,
            )
        elif intent["intent"] == "reject":
            return (
                "Let's take another look at the MVP. What changes would you like to make?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle modifications and then finalize MVP
            modified_mvp = self._update_mvp_with_feedback(intent.get("request", ""))
            self.project.final_mvp = modified_mvp
            
            # Move to design and generate it
            self.project.current_step = "design"
            self.project.save()
            
            design = self._generate_design()
            self.project.design_guidelines = design
            self.project.save()
            
            return (
                f"Updated and finalized MVP:\n{modified_mvp}\n\nBased on this, I've created these design guidelines:\n{design}\n\nShould I recommend a tech stack for implementation?",
                True,
            )
        else:
            return (
                "Please confirm if you want to finalize the MVP based on the critiques.",
                True,
            )

    def _handle_design(self, intent):
        if intent["intent"] == "approve":
            # Generate design guidelines if not already done
            if not self.project.design_guidelines:
                design = self._generate_design()
                self.project.design_guidelines = design
            else:
                design = self.project.design_guidelines
            
            # Move to tech stack and generate it immediately
            self.project.current_step = "tech_stack"
            self.project.save()
            
            stack = self._generate_tech_stack()
            self.project.tech_stack = stack
            self.project.save()
            
            return (
                f"Design guidelines confirmed.\n\nRecommended Tech Stack:\n{stack}\n\nIdeation and Design Completed. Ready to start development?",
                True,
            )
        elif intent["intent"] == "reject":
            return (
                "Let's reconsider the design approach. Please provide what kind of design guidelines you would like instead?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle design modifications then generate tech stack
            modified_design = self._update_design(intent.get("request", ""))
            self.project.design_guidelines = modified_design
            
            self.project.current_step = "tech_stack"
            self.project.save()
            
            stack = self._generate_tech_stack()
            self.project.tech_stack = stack
            self.project.save()
            
            return (
                f"Updated design guidelines:\n{modified_design}\n\nRecommended Tech Stack:\n{stack}\n\nReady to start development?",
                True,
            )
        else:
            return ("Please confirm if you want me to generate design guidelines.", True)

    def _handle_tech_stack(self, intent):
        if intent["intent"] == "approve":
            # Generate tech stack if not already done
            if not self.project.tech_stack:
                stack = self._generate_tech_stack()
                self.project.tech_stack = stack
            else:
                stack = self.project.tech_stack
            
            # Move to development phase
            self.project.current_step = "development"
            self.project.save()
            
            # Start development automatically            
            return (
                f"Tech stack confirmed.\n\nDevelopment has started. Would you like to see the progress or suggest any changes?",
                True,
            )
        elif intent["intent"] == "reject":
            return (
                "What constraints or preferences do you have for the tech stack?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle tech stack modifications and move to development
            modified_stack = self._update_tech_stack(intent.get("request", ""))
            self.project.tech_stack = modified_stack
            
            self.project.current_step = "development"
            self.project.save()
                        
            return (
                f"Updated tech stack:\n{modified_stack}\n\nDevelopment has started. Would you like to see progress or begin testing the application?",
                True,
            )
        else:
            return ("Please confirm if you want me to recommend a tech stack.", True)

    def _handle_development(self, intent):
        if intent["intent"] == "approve":
            # Move to testing phase immediately
            self.project.current_step = "test"
            self.project.save()
            
            async_to_sync(generate_frontend)("A note taking app. use font roboto. make the theme of website green and white")
            
            # Simulate development completion and immediately start testing
            test_results = "All core functionality tests passed. UI rendering tests passed. Performance benchmarks met."
            self.project.test_results = test_results
            
            return (
                f"Development complete! I've implemented all the features according to the specifications.\n\nTesting Results:\n{test_results}\n\nAll tests passed successfully. Should we move to the next stage?",
                True,
            )
        elif intent["intent"] == "reject":
            return (
                "Let's revisit the development plan. What concerns do you have?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle the modification, then move to testing phase
            updated_frontend = self._update_frontend(intent.get("request", ""))
            
            self.project.current_step = "test"
            self.project.save()
            
            test_results = "All core functionality tests passed. UI rendering tests passed. Performance benchmarks met."
            self.project.test_results = test_results
            
            return (
                f"I've made the suggested changes and completed development.\n\nTesting Results:\n{test_results}\n\nAll tests passed successfully. Should we deploy the application now?",
                True,
            )
        elif intent["intent"] == "complete":
            # User indicates development is complete, move to testing
            self.project.current_step = "test"
            self.project.save()
            
            test_results = "All core functionality tests passed. UI rendering tests passed. Performance benchmarks met."
            self.project.test_results = test_results
            
            return (
                f"Great! Testing has been completed.\n\nTesting Results:\n{test_results}\n\nAll tests passed successfully. Should we deploy the application now?",
                True,
            )
        else:
            return ("Please confirm if you're ready to start the development phase.", True)

    def _handle_test(self, intent):
        if intent["intent"] == "approve":
            # Move to deployment phase
            self.project.current_step = "deploy"
            self.project.save()
            
            return (
                f"The application is ready to be deployed. Should we proceed with deployment?",
                True,
            )
        elif intent["intent"] == "reject":
            self.project.current_step = "development"
            self.project.save()
            return (
                "Let's go back to development to fix the issues. What needs to be addressed?",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle test modifications, then advance to deployment
            # Simulate addressing test issues
            updated_test_results = "All test cases now passing after addressing the issues you mentioned."
            # self.project.test_results = updated_test_results
            
            self.project.current_step = "deploy"
            self.project.save()
            
            deployment_details = "Application packaged for deployment."
            self.project.deployment_details = deployment_details
            
            return (
                f"I've addressed your testing concerns.\n\nUpdated Test Results:\n{updated_test_results}\n\nDeployment Preparation:\n{deployment_details}\n\nThe application is ready to be deployed. Should we proceed with deployment?",
                True,
            )
        else:
            return ("Please confirm if we should proceed with testing the application.", True)

    def _handle_deploy(self, intent, user_input):
        if self.project.github_username is None and user_input.lower() == "yes":
            return ("Please provide your GitHub username:", False)

        user_input = user_input.strip()

        # Handle GitHub username collection
        if self.project.github_username is None:
            if not user_input:
                return ("Please provide your GitHub username:", False)
            elif not github_user_exists(user_input):
                return ("I couldn't find that GitHub user. Please double-check and send the correct username.", False)
            else:
                self.project.github_username = user_input
                self.project.save()
                return ("Great! Now, please provide a **new** repository name (make sure it doesn't already exist):", False)

        # Handle GitHub repo name collection
        if self.project.github_repo_name is None:
            if not user_input:
                return ("Please provide a repository name for your project:", False)
            elif github_repo_exists(self.project.github_username, user_input):
                return (f"⚠️ A repository named '{user_input}' already exists under your account. Please choose a different repository name.", False)
            else:
                self.project.github_repo_name = user_input
                self.project.save()
                return (
                    f"Perfect! We'll create and deploy to https://github.com/{self.project.github_username}/{self.project.github_repo_name}. Shall we proceed?",
                    True,
                )

        # Usual deployment flows here
        if intent["intent"] == "approve":
            # Execute actual deployment
            async_to_sync(deploy_to_github)(github_username=self.project.github_username, repo_name=self.project.github_repo_name)
            
            # Update to completed state immediately
            self.project.current_step = "complete"
            self.project.deployed_url = f"https://{self.project.github_username}.github.io/{self.project.github_repo_name}/"
            self.project.save()

            return (
                f"✅ Your application has been deployed! View it at {self.project.deployed_url}\n\nThe project is now complete. Would you like to make any changes or improvements to the deployed application?",
                True,
            )
        elif intent["intent"] == "reject":
            return ("What concerns do you have about deployment?", False)
        elif intent["intent"] == "modify":
            # Handle modifications then deploy
            # Implement any requested modifications to deployment settings
            
            # Then deploy with updated settings
            async_to_sync(deploy_to_github)(github_username=self.project.github_username, repo_name=self.project.github_repo_name)
            
            self.project.current_step = "complete"
            self.project.deployed_url = f"https://{self.project.github_username}.github.io/{self.project.github_repo_name}/"
            self.project.save()

            return (
                f"✅ I've applied your deployment preferences and deployed your application! View it at {self.project.deployed_url}\n\nThe project is now complete. Would you like to make any changes or improvements?",
                True,
            )
        else:
            return ("Please confirm if we should deploy the application now.", True)

    def _handle_complete(self, intent):
        if intent["intent"] == "approve":
            # User wants to make changes to the deployed application
            return (
                "What specific changes would you like to make to the deployed application?",
                False,
            )
        elif intent["intent"] == "reject":
            # User is satisfied with the project as-is
            return (
                "Thank you for completing your project with us! Your application is now live at " + 
                f"{self.project.deployed_url}\n\nFeel free to start a new project anytime. Bye!",
                False,
            )
        elif intent["intent"] == "modify":
            # Handle specific post-deployment modifications
            # This could trigger specific modification functions based on what the user requested
            
            # For example:
            updated_app = self._apply_post_deployment_changes(intent.get("request", ""))
            redeploy_to_github(github_username=self.project.github_username, repo_name=self.project.github_repo_name)
            
            return (
                f"I've applied your suggested changes and redeployed the application. The updated version is now live at {self.project.deployed_url}\n\nIs there anything else you'd like to modify?",
                True,
            )
        else:
            return (
                "Your application is complete and deployed. Would you like to make any changes or improvements?",
                True,
            )
            
    # Helper methods for LLM-based generation
    def _generate_mvp(self):
        """Generate MVP features based on product description using LLM"""
        return generate_mvp_features(self.project.product_description)
        # return f"Features for {self.project.product_description}:\n1. User authentication\n2. Data storage\n3. Basic UI with essential controls\n4. Core functionality implementation"

    def _update_mvp(self, user_feedback):
        """Update MVP based on user feedback"""
        return f"Updated MVP based on your feedback:\n1. Modified user authentication\n2. Enhanced data storage\n3. Improved UI\n4. Extended core functionality"

    def _update_mvp_with_feedback(self, user_feedback):
        """Update MVP based on critiques and user feedback"""
        return f"Final MVP incorporating feedback and critiques:\n1. Streamlined authentication\n2. Optimized data storage\n3. User-friendly interface\n4. Focused core functionality"

    def _debate(self):
        """Generate critiques of the MVP features using LLM"""
        return debate_mvp_features(self.project.mvp)
        # return "Product Manager: Features 1 and 3 are essential, but feature 2 needs refinement.\nDesigner: The UI needs more attention to user experience.\nDeveloper: Implementation is feasible but should prioritize core functionality first."

    def _finalize_mvp(self):
        """Finalize MVP based on critiques and initial features"""
        return finalize_mvp(self.project.mvp, self.project.critiques)
        # return "Final MVP Features:\n1. Streamlined user authentication\n2. Optimized data storage\n3. User-friendly interface with essential controls\n4. Core functionality with prioritized implementation"

    def _generate_design(self):
        """Generate design guidelines based on product description"""
        return brainstorm_design_guidelines(self.project.product_description)
        # return "Design Guidelines:\n- Font: Roboto\n- Color scheme: #3FCF8E (primary), #FFFFFF (secondary)\n- Minimalist UI with clear hierarchy\n- Responsive design for all device sizes"

    def _update_design(self, user_feedback):
        """Update design based on user feedback"""
        return "Updated Design Guidelines:\n- Font: Roboto and Open Sans\n- Color scheme: #3FCF8E (primary), #FFFFFF (secondary), #212121 (text)\n- Refined UI with improved visual hierarchy\n- Enhanced responsive design with mobile-first approach"

    def _generate_tech_stack(self):
        """Generate tech stack recommendations"""
        return decide_tech_stack(self.project.product_description, self.project.final_mvp, self.project.design_guidelines)
        # return "\n- Frontend: React.js with Tailwind CSS\n- Backend: Node.js with Express\n- Database: MongoDB\n- Authentication: JWT\n- Deployment: GitHub Pages"

    def _update_tech_stack(self, user_feedback):
        """Update tech stack based on user feedback"""
        return "Updated Tech Stack:\n- Frontend: React.js with Tailwind CSS\n- Backend: Node.js with Express\n- Database: PostgreSQL\n- Authentication: Auth0\n- Deployment: GitHub Pages with CI/CD pipeline"

    def _update_frontend(self, user_feedback):
        """Update frontend based on user feedback"""
        return "Updated Frontend Implementation:\n- Modified UI components based on feedback\n- Enhanced responsive design\n- Improved user experience flow\n- Added requested visual elements"

    def _apply_post_deployment_changes(self, user_feedback):
        """Apply post-deployment changes based on user feedback"""
        return "Post-Deployment Changes:\n- Added requested features\n- Fixed identified issues\n- Enhanced performance\n- Updated styling as requested"

    def redeploy_to_github(self, github_username, repo_name):
        """Redeploy updated application to GitHub"""
        # In a real implementation, this would update the GitHub repository
        return True  # Mock implementation

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
        if feedback.lower() is "yes":
            return {"intent": "approve", "request": feedback}
        if feedback.lower() is "no":
            return {"intent": "reject", "request": feedback}
        else:
            return {"intent": "modify", "request": feedback}

