IOF XML v3.0 Elements
=====================

Main Elements
-------------

- BaseMessageElement

CompetitorList
~~~~~~~~~~~~~~

- CompetitorList
    - Competitor
        - Person
        - Organisation
        - ControlCard
        - Class
        - Score
        - Extensions
    - Extensions


OrganisationList
~~~~~~~~~~~~~~~~

- OrganisationList
    - Organisation
    - Extensions


EventList
~~~~~~~~~

- EventList
    - Event
    - Extensions


ClassList
~~~~~~~~~

- ClassList
    - Class
    - Extensions


EntryList
~~~~~~~~~

- EntryList
    - Event
    - TeamEntry
        - Id
        - Name → xsd:string
        - Organisation
        - TeamEntryPerson
            - Person
            - Organisation
            - Leg → xsd:integer
            - LegOrder → xsd:integer
            - ControlCard
            - Score
            - AssignedFee
            - Extensions
        - Class
        - Race → xsd:integer
        - AssignedFee
        - ServiceRequest
        - StartTimeAllocationRequest
        - ContactInformation → xsd:string
        - EntryTime → xsd:dateTime
        - Extensions
    - PersonEntry
        - Id
        - Person
        - Organisation
        - ControlCard
        - Score
        - Class
        - RaceNumber → xsd:integer
        - AssignedFee
        - ServiceRequest
        - StartTimeAllocationRequest
        - EntryTime → xsd:dateTime
        - Extensions
    - Extensions

- StartTimeAllocationRequest
    - Organisation
    - Person


CourseData
~~~~~~~~~~

- CourseData
    - Event
    - RaceCourseData
        - Map
            - Id
            - Image
            - Scale → xsd:double
            - MapPositionTopLeft → MapPosition
            - MapPositionBottomRight → MapPosition
            - Extensions
        - Control
        - Course
            - Id
            - Name → xsd:string
            - CourseFamily → xsd:string
            - Length → xsd:double
            - Climb → xsd:double
            - CourseControl
                - Control → xsd:string
                - MapText → xsd:string
                - MapTextPosition → MapPosition
                - LegLength → xsd:double
                - Score → xsd:double
                - Extensions
            - MapId → xsd:integer
            - Extensions
        - ClassCourseAssignment
            - ClassId
            - ClassName → xsd:string
            - AllowedOnLeg → xsd:integer
            - CourseName → xsd:string
            - CourseFamily → xsd:string
            - Extensions
        - PersonCourseAssignment
            - EntryId
            - BibNumber → xsd:string
            - PersonName → xsd:string
            - ClassName → xsd:string
            - CourseName → xsd:string
            - CourseFamily → xsd:string
            - Extensions
        - TeamCourseAssignment
            - BibNumber → xsd:string
            - TeamName → xsd:string
            - ClassName → xsd:string
            - TeamMemberCourseAssignment
                - EntryId
                - BibNumber → xsd:string
                - Leg → xsd:integer
                - LegOrder → xsd:integer
                - TeamMemberName → xsd:string
                - CourseName → xsd:string
                - CourseFamily → xsd:string
                - Extensions
            - Extensions
        - Extensions
    - Extensions


StartList
~~~~~~~~~

- StartList
    - Event
    - ClassStart
        - Class
        - Course → SimpleRaceCourse
        - StartName
        - PersonStart
            - EntryId
            - Person
            - Organisation
            - Start → PersonRaceStart
                - BibNumber → xsd:string
                - StartTime → xsd:dateTime
                - Course → SimpleCourse
                - ControlCard
                - AssignedFee
                - ServiceRequest
                - Extensions
            - Extensions
        - TeamStart
            - EntryId
            - Name → xsd:string
            - Organisation
            - BibNumber → xsd:string
            - TeamMemberStart
                - EntryId
                - Person
                - Organisation
                - Start → TeamMemberRaceStart
                    - Leg → xsd:integer
                    - LegOrder → xsd:integer
                    - BibNumber → xsd:string
                    - StartTime → xsd:dateTime
                    - Course → SimpleCourse
                    - ControlCard
                    - AssignedFee
                    - ServiceRequest
                    - Extensions
                - Extensions
            - AssignedFee
            - ServiceRequest
            - Extensions
        - Extensions
    - Extensions


ResultList
~~~~~~~~~~

- ResultList
    - Event
    - ClassResult
        - Class
        - Course → SimpleRaceCourse
        - PersonResult
            - EntryId
            - Person
            - Organisation
            - PersonRaceResult
                - BibNumber → xsd:string
                - StartTime → xsd:dateTime
                - FinishTime → xsd:dateTime
                - Time → xsd:double
                - TimeBehind → xsd:double
                - Position → xsd:integer
                - Status → ResultStatus
                - Score
                - OverallResult
                - Course → SimpleCourse
                - SplitTime
                - ControlAnswer
                - Route
                - ControlCard
                - AssignedFee
                - ServiceRequest
                - Extensions
            - Extensions
        - TeamResult
            - EntryId
            - Name → xsd:string
            - Organisation
            - BibNumber → xsd:string
            - TeamMemberResult
                - EntryId
                - Person
                - Organisation
                - Result → TeamMemberRaceResult
                    - Leg → xsd:integer
                    - LegOrder → xsd:integer
                    - BibNumber → xsd:string
                    - StartTime → xsd:dateTime
                    - FinishTime → xsd:dateTime
                    - Time → xsd:double
                    - TimeBehind
                    - Position
                    - Status → ResultStatus
                    - Score
                    - OverallResult
                    - Course → SimpleCourse
                    - SplitTime
                    - ControlAnswer
                    - Route
                    - ControlCard
                    - AssignedFee
                    - ServiceRequest
                    - Extensions
                - Extensions
            - AssignedFee
            - ServiceRequest
            - Extensions
        - Extensions
    - Extensions

- OverallResult
    - Time → xsd:double
    - TimeBehind → xsd:double
    - Position → xsd:integer
    - Status → ResultStatus
    - Score
    - Extensions

- ControlAnswer
    - Answer → xsd:string
    - CorrectAnswer → xsd:string
    - Time → xsd:double
    - Extensions

- SplitTime
    - ControlCode → xsd:string
    - Time → xsd:double
    - Extensions

- Route


ServiceRequestList
~~~~~~~~~~~~~~~~~~

- ServiceRequestList
    - Event
    - OrganisationServiceRequest
        - Organisation
        - ServiceRequest
        - PersonServiceRequest
    - PersonServiceRequest
    - Extensions

- PersonServiceRequest
    - Person
    - ServiceRequest


ControlCardList
~~~~~~~~~~~~~~~

- ControlCardList
    - Owner → xsd:string
    - ControlCard
    - Extensions


Common Elements
---------------

These elements are used in multiple main elements or their descendents.

- Id

- Person
    - Id
    - Name → PersonName
        - Family → xsd:string
        - Given → xsd:string
    - BirthDate → xsd:date
    - Nationality → Country
    - Address
    - Contact
    - Extensions

- ControlCard

- Score

- Organisation
    - Id
    - Name → xsd:string
    - ShortName → xsd:string
    - MediaName → xsd:string
    - ParentOrganisationId → xsd:integer
    - Country
    - Address
    - Contact
    - Position → GeoPosition
    - Account
    - Role
    - Logotype → Image
    - Extensions

- Role
    - Person

- Event
    - Id
    - Name → xsd:string
    - StartTime → DateAndOptionalTime
    - EndTime → DateAndOptionalTime
    - Status → EventStatus
    - Classification → EventClassification
    - Form → EventForm
    - Organiser → Organisation
    - Official → Role
    - Class
    - Race
        - RaceNumber → xsd:integer
        - Name → xsd:string
        - StartTime → DateAndOptionalTime
        - EndTime → DateAndOptionalTime
        - Status → EventStatus
        - Classification → EventClassification
        - Position → GeoPosition
        - Discipline → RaceDiscipline
        - Organiser → Organisation
        - Official → Role
        - Service
        - URL → EventURL
        - Extensions
    - EntryReceiver
        - Address
        - Contact
    - Service
    - Account
    - URL → EventURL
    - Information → InformationItem
    - Schedule
        - StartTime → xsd:dateTime
        - EndTime → xsd:dateTime
        - Name → xsd:string
        - Venue → xsd:string
        - Position → GeoPosition
        - Details → xsd:string
    - News → InformationItem
    - Extensions

- EventURL

- InformationItem
    - Title → xsd:string
    - Content → xsd:string

- Class
    - Id
    - Name → xsd:string
    - ShortName → xsd:string
    - ClassType
        - Id
        - Name → xsd:string
    - Leg
        - Name → xsd:string
        - Extensions
    - TeamFee
    - Fee
    - Status → EventClassStatus
    - RaceClass
        - PunchingSystem → xsd:string
        - TeamFee
        - Fee
        - FirstStart → xsd:dateTime
        - Status → RaceClassStatus
        - Course → SimpleCourse
        - OnlineControl
        - Extensions
    - TooFewEntriesSubstituteClass
    - TooManyEntriesSubstituteClass
    - Extensions

- Fee
    - Id
    - Name → LanguageString
    - Amount
    - TaxableAmount
    - Percentage → xsd:double
    - TaxablePercentage → xsd:double
    - ValidFromTime → xsd:dateTime
    - ValidToTime → xsd:dateTime
    - FromDateOfBirth → xsd:date
    - ToDateOfBirth → xsd:date
    - Extensions

- AssignedFee
    - Fee
    - PaidAmount
    - Extensions

- Amount

- Control
    - Id
    - PunchingUnitId
    - Name → LanguageString
    - Position → GeoPosition
    - MapPosition
    - Extensions

- GeoPosition

- Image

- MapPosition

- SimpleCourse
    - Id
    - Name → xsd:string
    - CourseFamily → xsd:string
    - Length → xsd:double
    - Climb → xsd:double
    - NumberOfControls → xsd:integer

- SimpleRaceCourse

- Service
    - Id
    - Name → LanguageString
    - Fee
    - Description → LanguageString
    - MaxNumber → xsd:double
    - RequestedNumber → xsd:double
    - Extensions

- ServiceRequest
    - Id
    - Service
    - RequestedQuantity → xsd:double
    - DeliveredQuantity → xsd:double
    - Comment → xsd:string
    - AssignedFee
    - Extensions

- Account

- Address
    - CareOf → xsd:string
    - Street → xsd:string
    - ZipCode → xsd:string
    - City → xsd:string
    - State → xsd:string
    - Country

- Country

- Contact

- DateAndOptionalTime
    - Date → xsd:date
    - Time → xsd:time

- LanguageString

- Extensions
