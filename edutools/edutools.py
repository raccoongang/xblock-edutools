"""TO-DO: Write a description of what this XBlock is."""

from Crypto.Cipher import AES
from base64 import b64decode
import pkg_resources
from xblock.core import XBlock
from xblock.fields import Scope, String, Float, Boolean
from xblockutils.studio_editable import StudioEditableXBlockMixin
from web_fragments.fragment import Fragment

# Make '_' a no-op so we can scrape strings
_ = lambda text: text


class EduToolsXBlock(StudioEditableXBlockMixin, XBlock):
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

    submited = Boolean(
        scope=Scope.user_state,
        default=False
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
        notification_class = 'hidden'
        icon_class = ''
        msg = ''
        if self.submited and self.score:
            notification_class = 'success'
            icon_class = 'fa-check'
            msg = _('Correct ({grade}/{weight} point)').format(grade=self.score, weight=self.weight)
        elif self.submited:
            notification_class = 'error'
            icon_class = 'fa-close'
            msg = _('Incorrect ({grade}/{weight} point)').format(grade=self.score, weight=self.weight)

        html = self.resource_string("static/html/edutools.html")
        frag = Fragment(html.format(self=self, notification_class=notification_class, icon_class=icon_class, msg=msg))
        frag.add_css(self.resource_string("static/css/edutools.css"))
        frag.add_javascript(self.resource_string("static/js/src/edutools.js"))
        frag.initialize_js('EduToolsXBlock')
        return frag

    def student_view_data(self, context=None):
        return {
            'weight': self.weight,
            'file_url': self.grader_file,
        }

    @XBlock.json_handler
    def set_edutools_result(self, data, suffix=''):
        result = data.get('result')
        if not result:
            return {'success': False, 'msg': _('Result field is empty (0/{weight} point)'.format(weight=self.weight))}

        self.submited = True
        try:
            result = b64decode(result)
            salt = result[:AES.block_size]
            aes = AES.new(self.scope_ids.usage_id.block_id, AES.MODE_CBC, salt)
            grade = float(aes.decrypt(result[AES.block_size:]))
        except Exception:
            return {'success': False, 'msg': _('Result contain a wrong data (0/{weight} point)'.format(weight=self.weight))}
        else:
            self.score = grade > self.weight and self.weight or grade
            self.runtime.publish(
                self,
                'grade',
                {
                    'value': self.score,
                    'max_value': self.weight,
                }
            )
            if self.score:
                return {'success': True, 'msg': _('Correct ({grade}/{weight} point)'.format(grade=grade, weight=self.weight))}
            else:
                return {'success': True, 'msg': _('Incorrect (0/{weight} point)'.format(weight=self.weight))}

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
