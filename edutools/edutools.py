"""TO-DO: Write a description of what this XBlock is."""

from Crypto.Cipher import AES
from base64 import b64decode
import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, String, Integer, Float
from xblockutils.studio_editable import StudioEditableXBlockMixin
from web_fragments.fragment import Fragment

# Make '_' a no-op so we can scrape strings
_ = lambda text: text


class EduToolsXBlock(StudioEditableXBlockMixin, XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    display_name = String(
        display_name=_("Display Name"),
        help=_("Display name for this module"),
        default="EduTools",
        scope=Scope.settings,
    )

    grader_file = String(
        display_name=_("EduTools grader file link"),
        scope=Scope.settings,
    )

    description = String(
        multiline_editor='html',
        display_name=_("EduTools problem description"),
        default="Please run JetBtrains IDE for answer"
    )

    score = Float(
        scope=Scope.user_state,
        default=0
    )

    weight = Float(
        display_name=_("Problem weight"),
        default=1,
        scope=Scope.settings
    )

    encrypted_result = String(
        scope=Scope.settings,
    )

    editable_fields = ('display_name', 'grader_file', 'description', 'weight')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the EduToolsXBlock, shown to students
        when viewing courses.
        """
        html = self.resource_string("static/html/edutools.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/edutools.css"))
        frag.add_javascript(self.resource_string("static/js/src/edutools.js"))
        frag.initialize_js('EduToolsXBlock')
        return frag

    def student_view_data(self):
        return {
            'weight': self.weight,
            'file_url': self.grader_file,
        }

    @XBlock.json_handler
    def set_edutools_result(self, data, suffix=''):
        result = data.get('result')
        if not result:
            return {'success': False}

        try:
            salt = result[:16]
            result = b64decode(result[16:])
            aes = AES.new(self.scope_ids.usage_id.block_id, AES.MODE_CFB, salt)
            grade = float(aes.decrypt(result[16:]))
        except Exception:
            return {'success': False}
        else:
            self.runtime.publish(
                self,
                'grade',
                {
                    'value': grade,
                    'max_value': self.weight,
                }
            )
            return {'success': True}

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("EduToolsXBlock",
             """<edutools/>
             """),
            ("Multiple EduToolsXBlock",
             """<vertical_demo>
                <edutools/>
                <edutools/>
                <edutools/>
                </vertical_demo>
             """),
        ]
