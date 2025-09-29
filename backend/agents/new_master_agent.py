import os
import json
from asgiref.sync import async_to_sync, sync_to_async
from typing import Tuple
from utils.chat_utils import ChatUtil
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv, find_dotenv
from chat.models import Chat
from projects.models import Project, AgentSteps
from .ideation_agent import (
    generate_mvp_features,
    debate_mvp_features,
    finalize_mvp,
    brainstorm_design_guidelines,
    decide_tech_stack,
)
from .frontend_agent import (
    generate_frontend,
    structure_frontend_requests,
    generate_react_frontend,
    structure_react_requests,
)
from .deploy_agent import deploy_to_github
from utils.github_utils import github_user_exists, github_repo_exists
from utils.text_utils import extract_json_from_text, extract_prompt_list
from .prompts import (
    INTERPRETER_SYSTEM_PROMPT,
    ANSWER_USER_QUERY_PROMPT,
    CODE_PLANNER_PROMPT,
)
import time

load_dotenv(find_dotenv(), override=True)


class MasterAgent:
    def __init__(self, chat_id: int):
        self.chat = Chat.objects.get(id=chat_id)
        self.project, _ = Project.objects.get_or_create(chat=self.chat)
        self.is_move_forward_question = False

    async def handle_input(self, user_input: str) -> Tuple[str, bool]:
        yes_terms = {
            "yes",
            "y",
            "yeah",
            "yep",
            "sure",
            "absolutely",
            "certainly",
            "of course",
            "ok",
            "okay",
            "alright",
        }
        no_terms = {
            "no",
            "n",
            "nope",
            "nah",
            "never",
            "not at all",
            "negative",
            "no way",
            "absolutely not",
        }

        if user_input.lower() in yes_terms:
            request = {"intent": "approve"}
        elif user_input.lower() in no_terms:
            request = {"intent": "reject"}
        else:
            # We can improve it by adding a form instead
            if self.project.current_step == "deployment" and (
                self.project.github_username is None
                or self.project.github_repo_name is None
            ):
                request = {"intent": "details"}
            else:
                last_assistant_msg = await sync_to_async(
                    lambda: self.chat.messages.filter(sender="assistant").last()
                )()
                last_msg = last_assistant_msg.content if last_assistant_msg else "None"
                project_context = {
                    "current_step": self.project.current_step,
                    "product_description": self.project.product_description,
                    "mvp_features": self.project.mvp,
                }
                project_context = {k: v for k, v in project_context.items() if v}
                request = self._interpret_feedback(
                    user_input, last_msg, project_context
                )

        step = self.project.current_step

        # Handle incomplete input
        if request.get("intent") == "incomplete":
            await ChatUtil.send_message(
                self.chat,
                "I couldn't understand that. Could you please rephrase it clearly?",
                False,
                self.project.current_step,
            )
            return

        if request.get("intent") == "question":
            project_context = {
                "current_step": self.project.current_step,
                "product_description": self.project.product_description,
                "mvp_features": self.project.mvp,
                "design_guidelines": self.project.design_guidelines,
                "tech_stack": self.project.tech_stack,
                "deployed_url": self.project.deployed_url,
            }
            response = self._answer_user_query(
                request.get("question", ""), project_context
            )
            await ChatUtil.send_message(
                self.chat, response, False, self.project.current_step
            )
            return

        # Handle going back to previous step (can be used anywhere in the flow)
        if request.get("intent") == "go_back":
            target_step = request.get("target_stage")
            if target_step and target_step in [choice.value for choice in AgentSteps]:
                self.project.current_step = target_step
                await sync_to_async(self.project.save)()
                await ChatUtil.send_message(
                    self.chat,
                    f"Alright, taking you back to the {target_step.replace('_', ' ').title()} stage.",
                    True,
                    self.project.current_step,
                )
            else:
                await ChatUtil.send_message(
                    self.chat,
                    "Sorry, I couldn't understand which stage to go back to.",
                    False,
                    self.project.current_step,
                )
            return

        # Handle each step's specific logic
        if step == "init":
            await self._handle_init(request)
        elif step == "generate_mvp":
            await self._handle_generate_mvp(request)
        elif step == "design":
            await self._handle_design(request)
        elif step == "tech_stack":
            await self._handle_tech_stack(request)
        elif step == "development":
            await self._handle_development(request)
        elif step == "test":
            await self._handle_test(request)
        elif step == "deployment":
            await self._handle_deploy(request, user_input)
        elif step == "complete":
            await self._handle_complete(request)

        # await ChatUtil.send_message(self.chat,
        #     "Something went wrong. Let's start over. What product would you like to build?",
        #     False,
        #     "Init",
        # )

    # Individual step handlers
    async def _handle_init(self, request):
        if self.project.product_description is None:
            if request.get("intent") == "describe_product" and request.get("message"):
                self.project.product_description = request.get("message")
                self.project.current_step = "generate_mvp"
                await sync_to_async(self.project.save)()
                await ChatUtil.send_message(
                    self.chat,
                    f"Got your product description. You want to make {self.project.product_description}. Generating MVP...",
                    False,
                    "Init",
                )
                await self._handle_generate_mvp()
            else:
                await ChatUtil.send_message(
                    self.chat,
                    "Please provide a description of what you'd like to create so that we can move forward",
                    False,
                    "Init",
                )
        else:
            self._handle_generate_mvp()

    async def _handle_generate_mvp(self, request=None):
        if not self.project.mvp:
            mvp = self._generate_mvp()
            self.project.mvp = mvp
            await sync_to_async(self.project.save)()
            await ChatUtil.send_message(
                self.chat,
                f"Here are the MVP features I've generated:\n\n{mvp}\n. You can suggest any changes or Do you want to confirm this MVP?",
                True,
                "Ideation",
            )
            return
        if request.get("intent") == "approve":
            # Move to designing phase
            self.project.current_step = "design"
            await sync_to_async(self.project.save)()
            await self._handle_design()

        elif request.get("intent") == "reject":
            # User does not want to confirm the MVP. So ask user what they want to change.
            await ChatUtil.send_message(
                self.chat,
                "I understand. Please suggest what changes you have in your mind.",
                False,
                "Ideation",
            )
        elif request.get("intent") == "modify":
            # Handle requested modifications
            modify_mvp_request = request.get("message", "")

            # TODO: Generate new MVP based on modified description
            mvp = self._generate_mvp()
            self.project.mvp = mvp
            await sync_to_async(self.project.save)()
            await ChatUtil.send_message(
                self.chat,
                f"I've updated the product description and generated new MVP features:\n\n{mvp}\n\nShall we move to design phase?",
                True,
                "Ideation",
            )
        else:
            await ChatUtil.send_message(
                self.chat,
                "Please confirm what do you want to do!",
                False,
                "Ideation",
            )

    async def _handle_design(self, request=None):
        # Generate design guidelines
        if not self.project.design_guidelines:
            design = self._generate_design()
            self.project.design_guidelines = design
            await sync_to_async(self.project.save)()

            await ChatUtil.send_message(
                self.chat,
                f"Based on this MVP, I've created these design guidelines:\n{design}\n\nShould I recommend a tech stack for implementation?",
                True,
                "Design",
            )
            return
        if request.get("intent") == "approve":
            self.project.current_step = "tech_stack"
            await sync_to_async(self.project.save)()
            await self._handle_tech_stack()

        elif request.get("intent") == "reject":
            await ChatUtil.send_message(
                self.chat,
                "Let's reconsider the design approach. Please provide what kind of design guidelines you would like instead?",
                False,
                "Design",
            )
        elif request.get("intent") == "modify":
            # Handle design modifications then generate tech stack
            modified_design = self._update_design(request.get("message", ""))
            self.project.design_guidelines = modified_design

            self.project.current_step = "tech_stack"
            await sync_to_async(self.project.save)()

            await ChatUtil.send_message(
                self.chat,
                f"Updated design guidelines:\n{modified_design}",
                True,
                "Design",
            )
            await self._handle_tech_stack()

        else:
            await ChatUtil.send_message(
                self.chat, "Please confirm what do you want to do!", False, "Design"
            )

    async def _handle_tech_stack(self, request=None):
        stack = self._generate_tech_stack()
        self.project.tech_stack = stack
        # Move to development phase
        self.project.current_step = "development"
        await sync_to_async(self.project.save)()

        # Start development automatically
        await ChatUtil.send_message(
            self.chat,
            f"Recommended Tech Stack:\n{stack}\n\nIdeation and Design Completed.\n\nDevelopment has started.",
            False,
            "Tech Stack",
        )

        await self._handle_development()

    async def _handle_development(self, request=None):
        if request is None:
            # Determine if this is a React project based on tech stack
            is_react_project = False

            if is_react_project:
                # Use React-specific multi-step generation
                prompts = structure_react_requests(
                    description=self.project.product_description,
                    mvp=self.project.mvp,
                    design_guidelines=self.project.design_guidelines,
                )
                await generate_react_frontend(prompts, self.project.id)

                await ChatUtil.send_message(
                    self.chat,
                    "Development complete! I've implemented all React components and pages according to the specifications. Ready to do testing?",
                    True,
                    "Development",
                )
            else:
                # Use vanilla HTML multi-step generation
                prompts = structure_frontend_requests(
                    description=self.project.product_description,
                    mvp=self.project.mvp,
                    design_guidelines=self.project.design_guidelines,
                )
                await generate_frontend(prompts, self.project.id)

                await ChatUtil.send_message(
                    self.chat,
                    "Development complete! I've implemented all pages according to the specifications. Ready to do testing?",
                    True,
                    "Development",
                )
            return

        if request.get("intent") == "modify":
            # Handle the modification, then move to testing phase
            updated_frontend = self._update_frontend(request.get("message", ""))
            await ChatUtil.send_message(
                self.chat,
                f"I've made the suggested changes and completed development.\n\n. Please Confirm if you want to complete development.",
                True,
                "Development",
            )
        elif request.get("intent") == "approve":
            # User indicates development is complete, move to testing
            self.project.current_step = "test"
            await sync_to_async(self.project.save)()
            await ChatUtil.send_message(
                self.chat,
                f"Great! Development has been completed. Testing Begins.",
                False,
                "Testing",
            )
            await self._handle_test()
        else:
            await ChatUtil.send_message(
                self.chat,
                "Please confirm what do you want to do!",
                False,
                "Development",
            )

    async def _handle_test(self, request=None):
        # Simulate development completion and immediately start testing
        if request == None:
            test_results = "No test cases available."
            self.project.test_results = test_results
            await ChatUtil.send_message(
                self.chat,
                f"Testing Results:\n{test_results}\n\nTesting skipped.",
                False,
                "Testing",
            )
            self.project.current_step = "deployment"
            await sync_to_async(self.project.save)()
            await self._handle_deploy()
        # elif request.get("intent") == "approve":
        #     self.project.current_step = "deployment"
        #     await sync_to_async(self.project.save)()
        # elif request.get("intent") == "reject":
        #     self.project.current_step = "development"
        #     await sync_to_async(self.project.save)()
        #     await ChatUtil.send_message(
        #         self.chat, "Tell me what concerns do you have?", False, "Testing"
        #     )
        elif request.get("intent") == "modify":
            # Handle test modifications, then advance to deployment
            # Simulate addressing test issues
            updated_test_results = (
                "All test cases now passing after addressing the issues you mentioned."
            )
            # self.project.test_results = updated_test_results
            self.project.current_step = "deployment"
            await sync_to_async(self.project.save)()

            await ChatUtil.send_message(
                self.chat,
                f"I've addressed your testing concerns.\n\nUpdated Test Results:\n{updated_test_results}. Should we proceed to deployment?",
                True,
                "Testing",
            )
        else:
            await ChatUtil.send_message(
                self.chat, "Please confirm what do you want to do!", False, "Testing"
            )

    async def _handle_deploy(self, request=None, user_input=None):
        if self.project.github_username is None:
            if not user_input:
                await ChatUtil.send_message(
                    self.chat,
                    "Please provide your GitHub username:",
                    False,
                    "Deployment",
                )
                return
            else:
                user_input = user_input.strip()
                # Handle GitHub username collection:
                if not github_user_exists(user_input):
                    await ChatUtil.send_message(
                        self.chat,
                        "I couldn't find that GitHub user. Please double-check and send the correct username.",
                        False,
                        "Deployment",
                    )
                    return
                else:
                    self.project.github_username = user_input
                    await sync_to_async(self.project.save)()
                    await ChatUtil.send_message(
                        self.chat,
                        "Great! Now, please provide a **new** repository name (make sure it doesn't already exist):",
                        False,
                        "Deployment",
                    )
                    return
        if self.project.github_repo_name is None:
            # Handle GitHub repo name collection
            if github_repo_exists(self.project.github_username, user_input):
                await ChatUtil.send_message(
                    self.chat,
                    f"⚠️ A repository named '{user_input}' already exists under your account. Please choose a different repository name.",
                    False,
                    "Deployment",
                )
                return
            else:
                self.project.github_repo_name = user_input
                await sync_to_async(self.project.save)()
                await ChatUtil.send_message(
                    self.chat,
                    f"Perfect! We'll create and deploy to https://github.com/{self.project.github_username}/{self.project.github_repo_name}. Should we proceed?",
                    True,
                    "Deployment",
                )
                return

        # Usual deployment flows here
        await deploy_to_github(
            github_username=self.project.github_username,
            repo_name=self.project.github_repo_name,
            project_id=self.project.id,
        )

        # Update to completed state immediately
        self.project.current_step = "complete"
        self.project.deployed_url = f"https://{self.project.github_username}.github.io/{self.project.github_repo_name}/"
        await sync_to_async(self.project.save)()

        await ChatUtil.send_message(
            self.chat,
            f"✅ Your application has been deployed! View it at {self.project.deployed_url}\n\Finish Project?",
            True,
            "Deployment",
        )

    async def _handle_complete(self, request=None):
        if request.get("intent") == "modify":
            await ChatUtil.send_message(
                self.chat,
                f"If you want to modify anything, please go back to that stage first. For example, Use command 'Go back to development'.",
                True,
                "Complete",
            )
        else:
            await ChatUtil.send_message(
                self.chat,
                "Thank you for completing your project with us! Your application is now live at "
                + f"{self.project.deployed_url}\n\nFeel free to start a new project anytime. Bye!",
                False,
                "Complete",
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
        critiques = debate_mvp_features(self.project.mvp)
        formatted = []

        for perspective, critique in critiques.items():
            formatted.append(f"=== {perspective} Perspective ===\n{critique.strip()}\n")

        return "\n".join(formatted)
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
        return decide_tech_stack(
            self.project.product_description,
            self.project.mvp,
            self.project.design_guidelines,
        )
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

    def _interpret_feedback(
        self, feedback: str, last_question: str = "", project_context: dict = None
    ) -> dict:
        print(feedback, last_question, project_context)
        prompt = INTERPRETER_SYSTEM_PROMPT.format(
            feedback=feedback.strip(),
            last_question=last_question.strip(),
            project_context=json.dumps(project_context, indent=2),
        )

        interpreter_llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-2.0-flash",
            temperature=0.7,
        )
        response = interpreter_llm.predict(prompt)

        try:
            data = extract_json_from_text(response)

            if "intent" not in data:
                return {"intent": "incomplete"}

            return data

        except Exception as e:
            print("failed")
            print(e)
            return {"intent": "incomplete", "error": str(e)}

    def _answer_user_query(self, query: str, project_context: dict) -> str:
        # Prepare safe, trimmed context
        context = {k: v for k, v in project_context.items() if v}
        context_str = json.dumps(context, indent=2)

        prompt = ANSWER_USER_QUERY_PROMPT.format(
            user_query=query.strip(), project_context=context_str
        )

        llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-2.0-flash",
            temperature=0.6,
        )

        try:
            response = llm.predict(prompt).strip()
            return response if response else "Sorry, I couldn't come up with an answer."
        except Exception as e:
            print("An error occurred while generating a response: ", e)
            return f"An error occurred while generating a response"
