"""
Module that contains the openedx_filters pipeline steps.
"""
import logging
import pkg_resources

from django.template import Context, Template
from openedx_filters import PipelineStep

logger = logging.getLogger(__name__)


class AddVerticalBlockSkillVerificationSection(PipelineStep):
    """
    Adds extra HTML to the fragment.

    Example Usage:

    .. code-block::

        "OPENEDX_FILTERS_CONFIG": {
            "org.openedx.learning.vertical_block.render.completed.v1": {
                "fail_sliently": false,
                "pipeline": [
                    "skill_tagging.pipeline.AddVerticalBlockSkillVerificationSection"
                ]
            }
        }
    """
    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def fetch_related_skills(self, block):
        has_verified_tags = getattr(block, "has_verified_tags", None)
        if has_verified_tags is None or has_verified_tags is True:
            return []
        fetch_tags = getattr(block, "fetch_skill_tags", None)
        if fetch_tags is None:
            return []
        tags = fetch_tags()
        return tags

    def run_filter(self, block, fragment, context, view):
        """Pipeline Step implementing the Filter"""

        skills = self.fetch_related_skills(block)
        if not skills:
            return {"block": block, "fragment": fragment, "context": context, "view": view}
        verify_tags_url = block.runtime.handler_url(block, "verify_tags")
        html = self.resource_string("static/tagging.html")
        css = self.resource_string("static/tagging.css")
        js = self.resource_string("static/tagging.js")
        image = self.resource_string("static/brainstorming.svg")
        data = {
            "skills": skills,
            "verify_tags_url": verify_tags_url,
            "image": image,
        }
        template_str = f'<style type="text/css">{css}</style>{html}<script>{js}</script>'
        template = Template(template_str)
        context = Context(data)
        tags_div = template.render(context)
        fragment.content = f"{fragment.content}{tags_div}"
        return {"block": block, "fragment": fragment, "context": context, "view": view}
