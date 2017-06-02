from eu.softfire.tub.entities.entities import UsedResource, ResourceStatus, ResourceMetadata
from eu.softfire.tub.entities.repositories import find
from eu.softfire.tub.exceptions.exceptions import ResourceAlreadyBooked


class CalendarManager(object):
    def __init__(self):
        pass

    @classmethod
    def check_availability_for_node(cls, used_resource):
        if not cls.check_overlapping_booking(used_resource):
            raise ResourceAlreadyBooked('Some resources where already booked, please check the calendar')

    @classmethod
    def check_overlapping_booking(cls, used_resource):
        """
        Check calendar availability of this resource

        :param used_resource: the used resource to book
         :type used_resource: UsedResource
        :return: True when availability is granted False otherwise
         :rtype: bool
        """
        resource_metadata = cls.get_metadata_from_usedresource(used_resource)
        # if the resource metadata associated has infinite cardinality return true
        if resource_metadata.cardinality <= 0:
            return True
        max_concurrent = resource_metadata.cardinality
        counter = 0
        # if not then i need to calculate the number of resource already booked for that period
        for ur in find(UsedResource):
            if ur.status == ResourceStatus.RESERVED.value:
                if ur.start_date <= used_resource.start_date <= ur.end_date:
                    counter += 1
                elif ur.start_date <= used_resource.end_date <= ur.end_date:
                    counter += 1
        if counter < max_concurrent:
            return True

        return False

    @classmethod
    def get_metadata_from_usedresource(cls, used_resource):
        return find(ResourceMetadata, _id=used_resource.resource_id)

    @classmethod
    def get_month(cls):
        result = []

        for ur in find(UsedResource):
            rm = find(ResourceMetadata, _id=ur.resource_id)
            if rm and rm.cardinality > 0:
                result.append({
                    "resource_id": ur.resource_id,
                    "start": ur.start_date,
                    "end": ur.end_date,
                })

        return result
