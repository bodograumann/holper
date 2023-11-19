from importlib.resources import files
from unittest import TestCase

from holper import iof

from . import IOFv3


class TestCourseImport(TestCase):
    def test_iof_models(self):
        with (files(IOFv3) / "CourseData_Individual_Step2.xml").open("rb") as file:
            xml_data = file.read()
        course_data = iof.CourseData.from_xml(xml_data)

        assert course_data.iof_version == "3.0"
