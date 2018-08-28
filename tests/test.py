from unittest import TestCase

import sqlalchemy
import io

from holper import iofxml2, iofxml3, sportsoftware, model, tools

class TestModel(TestCase):
    session = None

    @classmethod
    def setUpClass(cls):
        engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
        tools.fix_sqlite_engine(engine)
        model.Base.metadata.create_all(engine)

        Session = sqlalchemy.orm.sessionmaker(bind=engine)
        session = Session()
        cls.session = session

    def setUp(self):
        self.session.begin_nested()

    def tearDown(self):
        self.session.rollback()

    @classmethod
    def tearDownClass(cls):
        cls.session.rollback()

    def test_event(self):
        event1 = model.Event(event_id=1, name='event1', form=model.EventForm.RELAY)
        self.session.add(event1)

        event1a = self.session.merge(model.Event(event_id=1, name='event1a'))

        self.assertIs(event1, event1a)



class TestImport(TestCase):
    def test_detect(self):
        modules = [iofxml2, iofxml3, sportsoftware]
        files = {
                'tests/IOFv2/ClubList1.xml':       iofxml2,
                'tests/IOFv2/CompetitorList1.xml': iofxml2,
                'tests/IOFv2/EntryList1.xml':      iofxml2,
                'tests/IOFv2/EntryList2.xml':      iofxml2,
                'tests/IOFv2/EntryList3.xml':      iofxml2,
                'tests/IOFv2/EntryList4.xml':      iofxml2,
                'tests/IOFv2/EventList1.xml':      iofxml2,
                'tests/IOFv2/RankList1.xml':       iofxml2,
                'tests/IOFv2/ResultList1.xml':     iofxml2,
                'tests/IOFv2/ResultList2.xml':     iofxml2,
                'tests/IOFv2/ResultList3.xml':     iofxml2,
                'tests/IOFv2/StartList1.xml':      iofxml2,
                'tests/IOFv2/StartList2.xml':      iofxml2,

                'tests/IOFv3/ClassList.xml':                   iofxml3,
                'tests/IOFv3/ClassList_Individual_Step1.xml':  iofxml3,
                'tests/IOFv3/ClassList_Relay_Step1.xml':       iofxml3,
                'tests/IOFv3/CompetitorList.xml':              iofxml3,
                'tests/IOFv3/CourseData_Individual_Step2.xml': iofxml3,
                'tests/IOFv3/CourseData_Individual_Step4.xml': iofxml3,
                'tests/IOFv3/CourseData_Relay_Step2.xml':      iofxml3,
                'tests/IOFv3/CourseData_Relay_Step4.xml':      iofxml3,
                'tests/IOFv3/EntryList1.xml':                  iofxml3,
                'tests/IOFv3/EntryList1.xml':                  iofxml3,
                'tests/IOFv3/EntryList2.xml':                  iofxml3,
                'tests/IOFv3/EntryList2.xml':                  iofxml3,
                'tests/IOFv3/Event_name_and_start_time.xml':   iofxml3,
                'tests/IOFv3/OrganisationList.xml':            iofxml3,
                'tests/IOFv3/ResultList1.xml':                 iofxml3,
                'tests/IOFv3/ResultList2.xml':                 iofxml3,
                'tests/IOFv3/ResultList3.xml':                 iofxml3,
                'tests/IOFv3/ResultList4.xml':                 iofxml3,
                'tests/IOFv3/StartList1.xml':                  iofxml3,
                'tests/IOFv3/StartList2.xml':                  iofxml3,
                'tests/IOFv3/StartList3.xml':                  iofxml3,
                'tests/IOFv3/StartList4.xml':                  iofxml3,
                'tests/IOFv3/StartList_Individual_Step3.xml':  iofxml3,
                'tests/IOFv3/StartList_Relay_Step3.xml':       iofxml3,

                'tests/SportSoftware/OE_11.0_EntryList1.csv':  sportsoftware,
                'tests/SportSoftware/OE_11.0_EntryList2.csv':  sportsoftware,
                'tests/SportSoftware/OS_11.0_EntryList1.csv':  sportsoftware,
                'tests/SportSoftware/OS_11.0_EntryList2.csv':  sportsoftware,
                'tests/SportSoftware/OS_11.0_EntryList3.csv':  sportsoftware,
                'tests/SportSoftware/OT_10.2_EntryList.csv':   sportsoftware
                }
        for filename in files:
            with open(filename, 'rb') as f:
                for module in modules:
                    with self.subTest(filename=filename, module=module.__name__):
                        if module is files[filename]:
                            self.assertTrue(module.detect(f))
                        else:
                            self.assertFalse(module.detect(f))
                        self.assertFalse(f.closed)
                        f.seek(0)

    def test_iofxml3_person_entry_list(self):
        with open('tests/IOFv3/EntryList1.xml', 'rb') as f:
            generator = iofxml3.read(f)
            event = next(generator)
            entries = list(generator)
            self.assertEqual(len(entries), 3)

            for entry in entries:
                self.assertIsInstance(entry, model.Entry)

            self.assertIs(entries[0].category_requests[0], entries[1].category_requests[0])
            self.assertEqual(entries[0].competitors[0].organisation.country.ioc_code, 'GBR')

    def test_iofxml3_team_entry_list(self):
        with open('tests/IOFv3/EntryList2.xml', 'rb') as f:
            generator = iofxml3.read(f)
            event = next(generator)
            entries = list(generator)
            self.assertEqual(len(entries), 2)

            for entry in entries:
                self.assertIsInstance(entry, model.Entry)

            self.assertEqual(len(entries[0].competitors), 5)

    def test_sportsoftware_oe_entries(self):
        with open('tests/SportSoftware/OE_11.0_EntryList1.csv', 'rb') as f:
            generator = sportsoftware.read(f)
            entries = list(generator)
            for entry in entries:
                self.assertIsInstance(entry, model.Entry)

    def test_sportsoftware_os_entries(self):
        with open('tests/SportSoftware/OS_11.0_EntryList1.csv', 'rb') as f:
            generator = sportsoftware.read(f)
            entries = list(generator)
            for entry in entries:
                self.assertIsInstance(entry, model.Entry)

    def test_sportsoftware_ot_entries(self):
        with open('tests/SportSoftware/OT_10.2_EntryList.csv', 'rb') as f:
            generator = sportsoftware.read(f)
            entries = list(generator)
            for entry in entries:
                self.assertIsInstance(entry, model.Entry)


class TestExport(TestCase):
    def setUp(self):
        self.buffer = io.BytesIO()

    def tearDown(self):
        del self.buffer

    def test_sportsoftware_oe_entries(self):
        event = model.Event(form=model.EventForm.INDIVIDUAL)

        sportsoftware.write(self.buffer, event)

        self.buffer.seek(0)
        self.assertEqual(sportsoftware._detect_type(self.buffer), 'OE11')

    def test_sportsoftware_os_entries(self):
        event = model.Event(form=model.EventForm.RELAY)

        sportsoftware.write(self.buffer, event)

        self.buffer.seek(0)
        self.assertEqual(sportsoftware._detect_type(self.buffer), 'OS11')


    def test_sportsoftware_ot_entries(self):
        event = model.Event(form=model.EventForm.TEAM)

        sportsoftware.write(self.buffer, event)

        self.buffer.seek(0)
        self.assertEqual(sportsoftware._detect_type(self.buffer), 'OT10')

