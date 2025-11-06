from django.db import models
from chat.models import Chat


class AgentSteps(models.TextChoices):
    INIT = "init", "Initial Prompt"
    GENERATE_MVP = "generate_mvp", "Generate MVP"
    DEBATE = "debate", "Critique MVP"
    FINALIZE_MVP = "finalize_mvp", "Finalize MVP"
    DESIGN = "design", "Design Guidelines"
    TECH_STACK = "tech_stack", "Tech Stack Recommendation"
    DEVELOPMENT = "development", "Development"
    TESTING = "test", "Testing"
    DEPLOYMENT = "deployment", "Deployment"
    COMPLETE = "complete", "Completed"


class DevelopmentStage(models.Model):
    """
    Tracks development progress for a project.
    """

    project = models.OneToOneField(
        "Project", on_delete=models.CASCADE, related_name="development_stage"
    )
    pages_approved = models.BooleanField(default=False)
    pages = models.JSONField(blank=True, null=True, default=list)
    prompts = models.JSONField(blank=True, null=True)


class Project(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name="project")

    current_step = models.CharField(
        max_length=50, choices=AgentSteps.choices, default=AgentSteps.INIT
    )

    product_description = models.TextField(blank=True, null=True)
    mvp = models.TextField(blank=True, null=True)
    design_guidelines = models.TextField(blank=True, null=True)
    tech_stack = models.TextField(blank=True, null=True)
    github_username = models.CharField(max_length=100, blank=True, null=True)
    github_repo_name = models.CharField(max_length=100, blank=True, null=True)
    deployed_url = models.URLField(blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Project for {self.chat}"
