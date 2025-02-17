```
__init__.py
ad_domain.py
class ADDomain:
class ADTrustedDomain:

ad_kerberos_keys.py
class RawKerberosKey:
class GssKerberosKey:

ad_objects.py
class ADObject:
class ADComputer(ADObject):
class ADUser(ADObject):
class ADPosixUser(ADUser):
class ADGroup(ADObject):
class ADPosixGroup(ADGroup):
class ADDomainContainerObject(ADObject):
class ADOrganizationalUnit(ADObject):
class ADGroupPolicy(ADObject):

ad_session.py
class ADSession:

managed_ad_objects.py
class ManagedADObject:
class ManagedADComputer(ManagedADObject):
class ManagedADUser(ManagedADObject):

``