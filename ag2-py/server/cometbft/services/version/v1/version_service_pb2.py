# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: cometbft/services/version/v1/version_service.proto
# Protobuf Python Version: 5.29.2
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
    2,
    '',
    'cometbft/services/version/v1/version_service.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cometbft.services.version.v1 import version_pb2 as cometbft_dot_services_dot_version_dot_v1_dot_version__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n2cometbft/services/version/v1/version_service.proto\x12\x1c\x63ometbft.services.version.v1\x1a*cometbft/services/version/v1/version.proto2\x81\x01\n\x0eVersionService\x12o\n\nGetVersion\x12/.cometbft.services.version.v1.GetVersionRequest\x1a\x30.cometbft.services.version.v1.GetVersionResponseB?Z=github.com/cometbft/cometbft/api/cometbft/services/version/v1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cometbft.services.version.v1.version_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z=github.com/cometbft/cometbft/api/cometbft/services/version/v1'
  _globals['_VERSIONSERVICE']._serialized_start=129
  _globals['_VERSIONSERVICE']._serialized_end=258
# @@protoc_insertion_point(module_scope)
