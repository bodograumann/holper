from typing import Annotated

from pydantic_xml import element
from typing_extensions import Doc

from .common import BaseMessageElement, Event, IOFBaseModel, Organisation, Person, ServiceRequest


class PersonServiceRequest(IOFBaseModel):
    """Service requests made by a person."""

    person: Annotated[Person, element(tag="Person"), Doc("The person that made the requests.")]
    service_requests: Annotated[list[ServiceRequest], element(tag="ServiceRequest"), Doc("The service requests.")]


class OrganisationServiceRequest(IOFBaseModel):
    """Service requests made by an organisation."""

    organisation: Annotated[Organisation, element(tag="Organisation"), Doc("The organisation that made the requests.")]
    service_requests: Annotated[
        list[ServiceRequest],
        element(tag="ServiceRequest"),
        Doc("The service requests that the organisation made."),
    ] = []
    person_service_requests: Annotated[
        list[PersonServiceRequest],
        element(tag="PersonServiceRequest"),
        Doc("The service requests made by persons representing the organisation."),
    ] = []


class ServiceRequestList(BaseMessageElement):
    """A list of service requests."""

    event: Annotated[Event, element(tag="Event"), Doc("The event that the service requests are valid for.")]
    organisation_service_requests: Annotated[
        list[OrganisationServiceRequest],
        element(tag="OrganisationServiceRequest"),
        Doc("Service requests made by organisations."),
    ] = []
    person_service_requests: Annotated[
        list[PersonServiceRequest],
        element(tag="PersonServiceRequest"),
        Doc("Service requests made by persons."),
    ] = []
