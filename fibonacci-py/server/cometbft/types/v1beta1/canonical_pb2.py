# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: cometbft/types/v1beta1/canonical.proto
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
    'cometbft/types/v1beta1/canonical.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from cometbft.types.v1beta1 import types_pb2 as cometbft_dot_types_dot_v1beta1_dot_types__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n&cometbft/types/v1beta1/canonical.proto\x12\x16\x63ometbft.types.v1beta1\x1a\x14gogoproto/gogo.proto\x1a\"cometbft/types/v1beta1/types.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\x84\x01\n\x10\x43\x61nonicalBlockID\x12\x12\n\x04hash\x18\x01 \x01(\x0cR\x04hash\x12\\\n\x0fpart_set_header\x18\x02 \x01(\x0b\x32..cometbft.types.v1beta1.CanonicalPartSetHeaderB\x04\xc8\xde\x1f\x00R\rpartSetHeader\"B\n\x16\x43\x61nonicalPartSetHeader\x12\x14\n\x05total\x18\x01 \x01(\rR\x05total\x12\x12\n\x04hash\x18\x02 \x01(\x0cR\x04hash\"\xe5\x02\n\x11\x43\x61nonicalProposal\x12\x39\n\x04type\x18\x01 \x01(\x0e\x32%.cometbft.types.v1beta1.SignedMsgTypeR\x04type\x12\x16\n\x06height\x18\x02 \x01(\x10R\x06height\x12\x14\n\x05round\x18\x03 \x01(\x10R\x05round\x12)\n\tpol_round\x18\x04 \x01(\x03\x42\x0c\xe2\xde\x1f\x08POLRoundR\x08polRound\x12P\n\x08\x62lock_id\x18\x05 \x01(\x0b\x32(.cometbft.types.v1beta1.CanonicalBlockIDB\x0b\xe2\xde\x1f\x07\x42lockIDR\x07\x62lockId\x12\x42\n\ttimestamp\x18\x06 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x08\xc8\xde\x1f\x00\x90\xdf\x1f\x01R\ttimestamp\x12&\n\x08\x63hain_id\x18\x07 \x01(\tB\x0b\xe2\xde\x1f\x07\x43hainIDR\x07\x63hainId\"\xb6\x02\n\rCanonicalVote\x12\x39\n\x04type\x18\x01 \x01(\x0e\x32%.cometbft.types.v1beta1.SignedMsgTypeR\x04type\x12\x16\n\x06height\x18\x02 \x01(\x10R\x06height\x12\x14\n\x05round\x18\x03 \x01(\x10R\x05round\x12P\n\x08\x62lock_id\x18\x04 \x01(\x0b\x32(.cometbft.types.v1beta1.CanonicalBlockIDB\x0b\xe2\xde\x1f\x07\x42lockIDR\x07\x62lockId\x12\x42\n\ttimestamp\x18\x05 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x08\xc8\xde\x1f\x00\x90\xdf\x1f\x01R\ttimestamp\x12&\n\x08\x63hain_id\x18\x06 \x01(\tB\x0b\xe2\xde\x1f\x07\x43hainIDR\x07\x63hainIdB9Z7github.com/cometbft/cometbft/api/cometbft/types/v1beta1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cometbft.types.v1beta1.canonical_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z7github.com/cometbft/cometbft/api/cometbft/types/v1beta1'
  _globals['_CANONICALBLOCKID'].fields_by_name['part_set_header']._loaded_options = None
  _globals['_CANONICALBLOCKID'].fields_by_name['part_set_header']._serialized_options = b'\310\336\037\000'
  _globals['_CANONICALPROPOSAL'].fields_by_name['pol_round']._loaded_options = None
  _globals['_CANONICALPROPOSAL'].fields_by_name['pol_round']._serialized_options = b'\342\336\037\010POLRound'
  _globals['_CANONICALPROPOSAL'].fields_by_name['block_id']._loaded_options = None
  _globals['_CANONICALPROPOSAL'].fields_by_name['block_id']._serialized_options = b'\342\336\037\007BlockID'
  _globals['_CANONICALPROPOSAL'].fields_by_name['timestamp']._loaded_options = None
  _globals['_CANONICALPROPOSAL'].fields_by_name['timestamp']._serialized_options = b'\310\336\037\000\220\337\037\001'
  _globals['_CANONICALPROPOSAL'].fields_by_name['chain_id']._loaded_options = None
  _globals['_CANONICALPROPOSAL'].fields_by_name['chain_id']._serialized_options = b'\342\336\037\007ChainID'
  _globals['_CANONICALVOTE'].fields_by_name['block_id']._loaded_options = None
  _globals['_CANONICALVOTE'].fields_by_name['block_id']._serialized_options = b'\342\336\037\007BlockID'
  _globals['_CANONICALVOTE'].fields_by_name['timestamp']._loaded_options = None
  _globals['_CANONICALVOTE'].fields_by_name['timestamp']._serialized_options = b'\310\336\037\000\220\337\037\001'
  _globals['_CANONICALVOTE'].fields_by_name['chain_id']._loaded_options = None
  _globals['_CANONICALVOTE'].fields_by_name['chain_id']._serialized_options = b'\342\336\037\007ChainID'
  _globals['_CANONICALBLOCKID']._serialized_start=158
  _globals['_CANONICALBLOCKID']._serialized_end=290
  _globals['_CANONICALPARTSETHEADER']._serialized_start=292
  _globals['_CANONICALPARTSETHEADER']._serialized_end=358
  _globals['_CANONICALPROPOSAL']._serialized_start=361
  _globals['_CANONICALPROPOSAL']._serialized_end=718
  _globals['_CANONICALVOTE']._serialized_start=721
  _globals['_CANONICALVOTE']._serialized_end=1031
# @@protoc_insertion_point(module_scope)
