# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: protos/example.proto
# Protobuf Python Version: 5.29.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(
    _runtime_version.Domain.PUBLIC,
    5,
    29,
    0,
    '',
    'protos/example.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14protos/example.proto\x12\tmyservice\"!\n\x0eMessageRequest\x12\x0f\n\x07message\x18\x01 \x01(\t\" \n\x0fMessageResponse\x12\r\n\x05reply\x18\x01 \x01(\t2S\n\tMyService\x12\x46\n\x0bSendMessage\x12\x19.myservice.MessageRequest\x1a\x1a.myservice.MessageResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'protos.example_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  DESCRIPTOR._loaded_options = None
  _globals['_MESSAGEREQUEST']._serialized_start=35
  _globals['_MESSAGEREQUEST']._serialized_end=68
  _globals['_MESSAGERESPONSE']._serialized_start=70
  _globals['_MESSAGERESPONSE']._serialized_end=102
  _globals['_MYSERVICE']._serialized_start=104
  _globals['_MYSERVICE']._serialized_end=187
# @@protoc_insertion_point(module_scope)
