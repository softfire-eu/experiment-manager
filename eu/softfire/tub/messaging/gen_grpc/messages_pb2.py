# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='messages.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0emessages.proto\"F\n\x0fRegisterMessage\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x02 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x03 \x01(\t\"3\n\x11UnregisterMessage\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08\x65ndpoint\x18\x02 \x01(\t\"X\n\x0eRequestMessage\x12\x17\n\x06method\x18\x01 \x01(\x0e\x32\x07.Method\x12\x0f\n\x07payload\x18\x02 \x01(\t\x12\x1c\n\tuser_info\x18\x03 \x01(\x0b\x32\t.UserInfo\"\xa9\x01\n\x0fResponseMessage\x12\x0e\n\x06result\x18\x01 \x01(\x05\x12.\n\rlist_resource\x18\x02 \x01(\x0b\x32\x15.ListResourceResponseH\x00\x12\x34\n\x10provide_resource\x18\x03 \x01(\x0b\x32\x18.ProvideResourceResponseH\x00\x12\x15\n\rerror_message\x18\x04 \x01(\tB\t\n\x07message\"<\n\x14ListResourceResponse\x12$\n\tresources\x18\x01 \x03(\x0b\x32\x11.ResourceMetadata\"7\n\x17ProvideResourceResponse\x12\x1c\n\tresources\x18\x01 \x03(\x0b\x32\t.Resource\"e\n\x10ResourceMetadata\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x65scription\x18\x02 \x01(\t\x12\x13\n\x0b\x63\x61rdinality\x18\x03 \x01(\x05\x12\x19\n\x07testbed\x18\x04 \x01(\x0e\x32\x08.Testbed\"\xbc\x01\n\x08UserInfo\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x15\n\rob_project_id\x18\x04 \x01(\t\x12\x36\n\x0ftestbed_tenants\x18\x05 \x03(\x0b\x32\x1d.UserInfo.TestbedTenantsEntry\x1a\x35\n\x13TestbedTenantsEntry\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"\'\n\x08Resource\x12\n\n\x02id\x18\x01 \x01(\t\x12\x0f\n\x07\x63ontent\x18\x02 \x01(\t*J\n\x06Method\x12\x12\n\x0eLIST_RESOURCES\x10\x00\x12\x15\n\x11PROVIDE_RESOURCES\x10\x01\x12\x15\n\x11RELEASE_RESOURCES\x10\x02*\x89\x01\n\x07Testbed\x12\n\n\x06SURREY\x10\x00\x12\t\n\x05\x46OKUS\x10\x01\x12\x06\n\x02\x44T\x10\x02\x12\x07\n\x03\x41\x44S\x10\x03\x12\x0c\n\x08\x45RICSSON\x10\x04\x12\x0e\n\nSURREY_DEV\x10\x05\x12\r\n\tFOKUS_DEV\x10\x06\x12\n\n\x06\x44T_DEV\x10\x07\x12\x0b\n\x07\x41\x44S_DEV\x10\x08\x12\x10\n\x0c\x45RICSSON_DEV\x10\t2}\n\x13RegistrationService\x12\x30\n\x08register\x12\x10.RegisterMessage\x1a\x10.ResponseMessage\"\x00\x12\x34\n\nunregister\x12\x12.UnregisterMessage\x1a\x10.ResponseMessage\"\x00\x32\x65\n\x0cManagerAgent\x12.\n\x07\x65xecute\x12\x0f.RequestMessage\x1a\x10.ResponseMessage\"\x00\x12%\n\x0b\x63reate_user\x12\t.UserInfo\x1a\t.UserInfo\"\x00\x42\x02H\x03\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_METHOD = _descriptor.EnumDescriptor(
  name='Method',
  full_name='Method',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='LIST_RESOURCES', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PROVIDE_RESOURCES', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RELEASE_RESOURCES', index=2, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=859,
  serialized_end=933,
)
_sym_db.RegisterEnumDescriptor(_METHOD)

Method = enum_type_wrapper.EnumTypeWrapper(_METHOD)
_TESTBED = _descriptor.EnumDescriptor(
  name='Testbed',
  full_name='Testbed',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SURREY', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FOKUS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ADS', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ERICSSON', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SURREY_DEV', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='FOKUS_DEV', index=6, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_DEV', index=7, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ADS_DEV', index=8, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ERICSSON_DEV', index=9, number=9,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=936,
  serialized_end=1073,
)
_sym_db.RegisterEnumDescriptor(_TESTBED)

Testbed = enum_type_wrapper.EnumTypeWrapper(_TESTBED)
LIST_RESOURCES = 0
PROVIDE_RESOURCES = 1
RELEASE_RESOURCES = 2
SURREY = 0
FOKUS = 1
DT = 2
ADS = 3
ERICSSON = 4
SURREY_DEV = 5
FOKUS_DEV = 6
DT_DEV = 7
ADS_DEV = 8
ERICSSON_DEV = 9



_REGISTERMESSAGE = _descriptor.Descriptor(
  name='RegisterMessage',
  full_name='RegisterMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='RegisterMessage.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='endpoint', full_name='RegisterMessage.endpoint', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='RegisterMessage.description', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=88,
)


_UNREGISTERMESSAGE = _descriptor.Descriptor(
  name='UnregisterMessage',
  full_name='UnregisterMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='UnregisterMessage.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='endpoint', full_name='UnregisterMessage.endpoint', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=90,
  serialized_end=141,
)


_REQUESTMESSAGE = _descriptor.Descriptor(
  name='RequestMessage',
  full_name='RequestMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='method', full_name='RequestMessage.method', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload', full_name='RequestMessage.payload', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='user_info', full_name='RequestMessage.user_info', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=143,
  serialized_end=231,
)


_RESPONSEMESSAGE = _descriptor.Descriptor(
  name='ResponseMessage',
  full_name='ResponseMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='ResponseMessage.result', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='list_resource', full_name='ResponseMessage.list_resource', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='provide_resource', full_name='ResponseMessage.provide_resource', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='error_message', full_name='ResponseMessage.error_message', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message', full_name='ResponseMessage.message',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=234,
  serialized_end=403,
)


_LISTRESOURCERESPONSE = _descriptor.Descriptor(
  name='ListResourceResponse',
  full_name='ListResourceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='resources', full_name='ListResourceResponse.resources', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=405,
  serialized_end=465,
)


_PROVIDERESOURCERESPONSE = _descriptor.Descriptor(
  name='ProvideResourceResponse',
  full_name='ProvideResourceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='resources', full_name='ProvideResourceResponse.resources', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=467,
  serialized_end=522,
)


_RESOURCEMETADATA = _descriptor.Descriptor(
  name='ResourceMetadata',
  full_name='ResourceMetadata',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='ResourceMetadata.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='description', full_name='ResourceMetadata.description', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cardinality', full_name='ResourceMetadata.cardinality', index=2,
      number=3, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='testbed', full_name='ResourceMetadata.testbed', index=3,
      number=4, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=524,
  serialized_end=625,
)


_USERINFO_TESTBEDTENANTSENTRY = _descriptor.Descriptor(
  name='TestbedTenantsEntry',
  full_name='UserInfo.TestbedTenantsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='UserInfo.TestbedTenantsEntry.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='UserInfo.TestbedTenantsEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=763,
  serialized_end=816,
)

_USERINFO = _descriptor.Descriptor(
  name='UserInfo',
  full_name='UserInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='UserInfo.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='name', full_name='UserInfo.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='password', full_name='UserInfo.password', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ob_project_id', full_name='UserInfo.ob_project_id', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='testbed_tenants', full_name='UserInfo.testbed_tenants', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_USERINFO_TESTBEDTENANTSENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=628,
  serialized_end=816,
)


_RESOURCE = _descriptor.Descriptor(
  name='Resource',
  full_name='Resource',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='Resource.id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='content', full_name='Resource.content', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=818,
  serialized_end=857,
)

_REQUESTMESSAGE.fields_by_name['method'].enum_type = _METHOD
_REQUESTMESSAGE.fields_by_name['user_info'].message_type = _USERINFO
_RESPONSEMESSAGE.fields_by_name['list_resource'].message_type = _LISTRESOURCERESPONSE
_RESPONSEMESSAGE.fields_by_name['provide_resource'].message_type = _PROVIDERESOURCERESPONSE
_RESPONSEMESSAGE.oneofs_by_name['message'].fields.append(
  _RESPONSEMESSAGE.fields_by_name['list_resource'])
_RESPONSEMESSAGE.fields_by_name['list_resource'].containing_oneof = _RESPONSEMESSAGE.oneofs_by_name['message']
_RESPONSEMESSAGE.oneofs_by_name['message'].fields.append(
  _RESPONSEMESSAGE.fields_by_name['provide_resource'])
_RESPONSEMESSAGE.fields_by_name['provide_resource'].containing_oneof = _RESPONSEMESSAGE.oneofs_by_name['message']
_LISTRESOURCERESPONSE.fields_by_name['resources'].message_type = _RESOURCEMETADATA
_PROVIDERESOURCERESPONSE.fields_by_name['resources'].message_type = _RESOURCE
_RESOURCEMETADATA.fields_by_name['testbed'].enum_type = _TESTBED
_USERINFO_TESTBEDTENANTSENTRY.containing_type = _USERINFO
_USERINFO.fields_by_name['testbed_tenants'].message_type = _USERINFO_TESTBEDTENANTSENTRY
DESCRIPTOR.message_types_by_name['RegisterMessage'] = _REGISTERMESSAGE
DESCRIPTOR.message_types_by_name['UnregisterMessage'] = _UNREGISTERMESSAGE
DESCRIPTOR.message_types_by_name['RequestMessage'] = _REQUESTMESSAGE
DESCRIPTOR.message_types_by_name['ResponseMessage'] = _RESPONSEMESSAGE
DESCRIPTOR.message_types_by_name['ListResourceResponse'] = _LISTRESOURCERESPONSE
DESCRIPTOR.message_types_by_name['ProvideResourceResponse'] = _PROVIDERESOURCERESPONSE
DESCRIPTOR.message_types_by_name['ResourceMetadata'] = _RESOURCEMETADATA
DESCRIPTOR.message_types_by_name['UserInfo'] = _USERINFO
DESCRIPTOR.message_types_by_name['Resource'] = _RESOURCE
DESCRIPTOR.enum_types_by_name['Method'] = _METHOD
DESCRIPTOR.enum_types_by_name['Testbed'] = _TESTBED

RegisterMessage = _reflection.GeneratedProtocolMessageType('RegisterMessage', (_message.Message,), dict(
  DESCRIPTOR = _REGISTERMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:RegisterMessage)
  ))
_sym_db.RegisterMessage(RegisterMessage)

UnregisterMessage = _reflection.GeneratedProtocolMessageType('UnregisterMessage', (_message.Message,), dict(
  DESCRIPTOR = _UNREGISTERMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:UnregisterMessage)
  ))
_sym_db.RegisterMessage(UnregisterMessage)

RequestMessage = _reflection.GeneratedProtocolMessageType('RequestMessage', (_message.Message,), dict(
  DESCRIPTOR = _REQUESTMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:RequestMessage)
  ))
_sym_db.RegisterMessage(RequestMessage)

ResponseMessage = _reflection.GeneratedProtocolMessageType('ResponseMessage', (_message.Message,), dict(
  DESCRIPTOR = _RESPONSEMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ResponseMessage)
  ))
_sym_db.RegisterMessage(ResponseMessage)

ListResourceResponse = _reflection.GeneratedProtocolMessageType('ListResourceResponse', (_message.Message,), dict(
  DESCRIPTOR = _LISTRESOURCERESPONSE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ListResourceResponse)
  ))
_sym_db.RegisterMessage(ListResourceResponse)

ProvideResourceResponse = _reflection.GeneratedProtocolMessageType('ProvideResourceResponse', (_message.Message,), dict(
  DESCRIPTOR = _PROVIDERESOURCERESPONSE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ProvideResourceResponse)
  ))
_sym_db.RegisterMessage(ProvideResourceResponse)

ResourceMetadata = _reflection.GeneratedProtocolMessageType('ResourceMetadata', (_message.Message,), dict(
  DESCRIPTOR = _RESOURCEMETADATA,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:ResourceMetadata)
  ))
_sym_db.RegisterMessage(ResourceMetadata)

UserInfo = _reflection.GeneratedProtocolMessageType('UserInfo', (_message.Message,), dict(

  TestbedTenantsEntry = _reflection.GeneratedProtocolMessageType('TestbedTenantsEntry', (_message.Message,), dict(
    DESCRIPTOR = _USERINFO_TESTBEDTENANTSENTRY,
    __module__ = 'messages_pb2'
    # @@protoc_insertion_point(class_scope:UserInfo.TestbedTenantsEntry)
    ))
  ,
  DESCRIPTOR = _USERINFO,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:UserInfo)
  ))
_sym_db.RegisterMessage(UserInfo)
_sym_db.RegisterMessage(UserInfo.TestbedTenantsEntry)

Resource = _reflection.GeneratedProtocolMessageType('Resource', (_message.Message,), dict(
  DESCRIPTOR = _RESOURCE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:Resource)
  ))
_sym_db.RegisterMessage(Resource)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('H\003'))
_USERINFO_TESTBEDTENANTSENTRY.has_options = True
_USERINFO_TESTBEDTENANTSENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
try:
  # THESE ELEMENTS WILL BE DEPRECATED.
  # Please use the generated *_pb2_grpc.py files instead.
  import grpc
  from grpc.framework.common import cardinality
  from grpc.framework.interfaces.face import utilities as face_utilities
  from grpc.beta import implementations as beta_implementations
  from grpc.beta import interfaces as beta_interfaces


  class RegistrationServiceStub(object):

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.register = channel.unary_unary(
          '/RegistrationService/register',
          request_serializer=RegisterMessage.SerializeToString,
          response_deserializer=ResponseMessage.FromString,
          )
      self.unregister = channel.unary_unary(
          '/RegistrationService/unregister',
          request_serializer=UnregisterMessage.SerializeToString,
          response_deserializer=ResponseMessage.FromString,
          )


  class RegistrationServiceServicer(object):

    def register(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def unregister(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_RegistrationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'register': grpc.unary_unary_rpc_method_handler(
            servicer.register,
            request_deserializer=RegisterMessage.FromString,
            response_serializer=ResponseMessage.SerializeToString,
        ),
        'unregister': grpc.unary_unary_rpc_method_handler(
            servicer.unregister,
            request_deserializer=UnregisterMessage.FromString,
            response_serializer=ResponseMessage.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'RegistrationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class ManagerAgentStub(object):

    def __init__(self, channel):
      """Constructor.

      Args:
        channel: A grpc.Channel.
      """
      self.execute = channel.unary_unary(
          '/ManagerAgent/execute',
          request_serializer=RequestMessage.SerializeToString,
          response_deserializer=ResponseMessage.FromString,
          )
      self.create_user = channel.unary_unary(
          '/ManagerAgent/create_user',
          request_serializer=UserInfo.SerializeToString,
          response_deserializer=UserInfo.FromString,
          )


  class ManagerAgentServicer(object):

    def execute(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')

    def create_user(self, request, context):
      context.set_code(grpc.StatusCode.UNIMPLEMENTED)
      context.set_details('Method not implemented!')
      raise NotImplementedError('Method not implemented!')


  def add_ManagerAgentServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'execute': grpc.unary_unary_rpc_method_handler(
            servicer.execute,
            request_deserializer=RequestMessage.FromString,
            response_serializer=ResponseMessage.SerializeToString,
        ),
        'create_user': grpc.unary_unary_rpc_method_handler(
            servicer.create_user,
            request_deserializer=UserInfo.FromString,
            response_serializer=UserInfo.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'ManagerAgent', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


  class BetaRegistrationServiceServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def register(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def unregister(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaRegistrationServiceStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def register(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    register.future = None
    def unregister(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    unregister.future = None


  def beta_create_RegistrationService_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('RegistrationService', 'register'): RegisterMessage.FromString,
      ('RegistrationService', 'unregister'): UnregisterMessage.FromString,
    }
    response_serializers = {
      ('RegistrationService', 'register'): ResponseMessage.SerializeToString,
      ('RegistrationService', 'unregister'): ResponseMessage.SerializeToString,
    }
    method_implementations = {
      ('RegistrationService', 'register'): face_utilities.unary_unary_inline(servicer.register),
      ('RegistrationService', 'unregister'): face_utilities.unary_unary_inline(servicer.unregister),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_RegistrationService_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('RegistrationService', 'register'): RegisterMessage.SerializeToString,
      ('RegistrationService', 'unregister'): UnregisterMessage.SerializeToString,
    }
    response_deserializers = {
      ('RegistrationService', 'register'): ResponseMessage.FromString,
      ('RegistrationService', 'unregister'): ResponseMessage.FromString,
    }
    cardinalities = {
      'register': cardinality.Cardinality.UNARY_UNARY,
      'unregister': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'RegistrationService', cardinalities, options=stub_options)


  class BetaManagerAgentServicer(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def execute(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)
    def create_user(self, request, context):
      context.code(beta_interfaces.StatusCode.UNIMPLEMENTED)


  class BetaManagerAgentStub(object):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This class was generated
    only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0."""
    def execute(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    execute.future = None
    def create_user(self, request, timeout, metadata=None, with_call=False, protocol_options=None):
      raise NotImplementedError()
    create_user.future = None


  def beta_create_ManagerAgent_server(servicer, pool=None, pool_size=None, default_timeout=None, maximum_timeout=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_deserializers = {
      ('ManagerAgent', 'create_user'): UserInfo.FromString,
      ('ManagerAgent', 'execute'): RequestMessage.FromString,
    }
    response_serializers = {
      ('ManagerAgent', 'create_user'): UserInfo.SerializeToString,
      ('ManagerAgent', 'execute'): ResponseMessage.SerializeToString,
    }
    method_implementations = {
      ('ManagerAgent', 'create_user'): face_utilities.unary_unary_inline(servicer.create_user),
      ('ManagerAgent', 'execute'): face_utilities.unary_unary_inline(servicer.execute),
    }
    server_options = beta_implementations.server_options(request_deserializers=request_deserializers, response_serializers=response_serializers, thread_pool=pool, thread_pool_size=pool_size, default_timeout=default_timeout, maximum_timeout=maximum_timeout)
    return beta_implementations.server(method_implementations, options=server_options)


  def beta_create_ManagerAgent_stub(channel, host=None, metadata_transformer=None, pool=None, pool_size=None):
    """The Beta API is deprecated for 0.15.0 and later.

    It is recommended to use the GA API (classes and functions in this
    file not marked beta) for all further purposes. This function was
    generated only to ease transition from grpcio<0.15.0 to grpcio>=0.15.0"""
    request_serializers = {
      ('ManagerAgent', 'create_user'): UserInfo.SerializeToString,
      ('ManagerAgent', 'execute'): RequestMessage.SerializeToString,
    }
    response_deserializers = {
      ('ManagerAgent', 'create_user'): UserInfo.FromString,
      ('ManagerAgent', 'execute'): ResponseMessage.FromString,
    }
    cardinalities = {
      'create_user': cardinality.Cardinality.UNARY_UNARY,
      'execute': cardinality.Cardinality.UNARY_UNARY,
    }
    stub_options = beta_implementations.stub_options(host=host, metadata_transformer=metadata_transformer, request_serializers=request_serializers, response_deserializers=response_deserializers, thread_pool=pool, thread_pool_size=pool_size)
    return beta_implementations.dynamic_stub(channel, 'ManagerAgent', cardinalities, options=stub_options)
except ImportError:
  pass
# @@protoc_insertion_point(module_scope)