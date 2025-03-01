# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# NO CHECKED-IN PROTOBUF GENCODE
# source: cometbft/abci/v1beta1/types.proto
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
    'cometbft/abci/v1beta1/types.proto'
)
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from cometbft.crypto.v1 import keys_pb2 as cometbft_dot_crypto_dot_v1_dot_keys__pb2
from cometbft.crypto.v1 import proof_pb2 as cometbft_dot_crypto_dot_v1_dot_proof__pb2
from cometbft.types.v1beta1 import params_pb2 as cometbft_dot_types_dot_v1beta1_dot_params__pb2
from cometbft.types.v1beta1 import types_pb2 as cometbft_dot_types_dot_v1beta1_dot_types__pb2
from gogoproto import gogo_pb2 as gogoproto_dot_gogo__pb2
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n!cometbft/abci/v1beta1/types.proto\x12\x15\x63ometbft.abci.v1beta1\x1a\x1d\x63ometbft/crypto/v1/keys.proto\x1a\x1e\x63ometbft/crypto/v1/proof.proto\x1a#cometbft/types/v1beta1/params.proto\x1a\"cometbft/types/v1beta1/types.proto\x1a\x14gogoproto/gogo.proto\x1a\x1fgoogle/protobuf/timestamp.proto\"\xeb\x08\n\x07Request\x12\x38\n\x04\x65\x63ho\x18\x01 \x01(\x0b\x32\".cometbft.abci.v1beta1.RequestEchoH\x00R\x04\x65\x63ho\x12;\n\x05\x66lush\x18\x02 \x01(\x0b\x32#.cometbft.abci.v1beta1.RequestFlushH\x00R\x05\x66lush\x12\x38\n\x04info\x18\x03 \x01(\x0b\x32\".cometbft.abci.v1beta1.RequestInfoH\x00R\x04info\x12H\n\nset_option\x18\x04 \x01(\x0b\x32\'.cometbft.abci.v1beta1.RequestSetOptionH\x00R\tsetOption\x12H\n\ninit_chain\x18\x05 \x01(\x0b\x32\'.cometbft.abci.v1beta1.RequestInitChainH\x00R\tinitChain\x12;\n\x05query\x18\x06 \x01(\x0b\x32#.cometbft.abci.v1beta1.RequestQueryH\x00R\x05query\x12K\n\x0b\x62\x65gin_block\x18\x07 \x01(\x0b\x32(.cometbft.abci.v1beta1.RequestBeginBlockH\x00R\nbeginBlock\x12\x42\n\x08\x63heck_tx\x18\x08 \x01(\x0b\x32%.cometbft.abci.v1beta1.RequestCheckTxH\x00R\x07\x63heckTx\x12H\n\ndeliver_tx\x18\t \x01(\x0b\x32\'.cometbft.abci.v1beta1.RequestDeliverTxH\x00R\tdeliverTx\x12\x45\n\tend_block\x18\n \x01(\x0b\x32&.cometbft.abci.v1beta1.RequestEndBlockH\x00R\x08\x65ndBlock\x12>\n\x06\x63ommit\x18\x0b \x01(\x0b\x32$.cometbft.abci.v1beta1.RequestCommitH\x00R\x06\x63ommit\x12T\n\x0elist_snapshots\x18\x0c \x01(\x0b\x32+.cometbft.abci.v1beta1.RequestListSnapshotsH\x00R\rlistSnapshots\x12T\n\x0eoffer_snapshot\x18\r \x01(\x0b\x32+.cometbft.abci.v1beta1.RequestOfferSnapshotH\x00R\rofferSnapshot\x12\x61\n\x13load_snapshot_chunk\x18\x0e \x01(\x0b\x32/.cometbft.abci.v1beta1.RequestLoadSnapshotChunkH\x00R\x11loadSnapshotChunk\x12\x64\n\x14\x61pply_snapshot_chunk\x18\x0f \x01(\x0b\x32\x30.cometbft.abci.v1beta1.RequestApplySnapshotChunkH\x00R\x12\x61pplySnapshotChunkB\x07\n\x05value\"\'\n\x0bRequestEcho\x12\x18\n\x07message\x18\x01 \x01(\tR\x07message\"\x0e\n\x0cRequestFlush\"m\n\x0bRequestInfo\x12\x18\n\x07version\x18\x01 \x01(\tR\x07version\x12#\n\rblock_version\x18\x02 \x01(\x04R\x0c\x62lockVersion\x12\x1f\n\x0bp2p_version\x18\x03 \x01(\x04R\np2pVersion\":\n\x10RequestSetOption\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value\"\xd7\x02\n\x10RequestInitChain\x12\x38\n\x04time\x18\x01 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x08\xc8\xde\x1f\x00\x90\xdf\x1f\x01R\x04time\x12\x19\n\x08\x63hain_id\x18\x02 \x01(\tR\x07\x63hainId\x12Q\n\x10\x63onsensus_params\x18\x03 \x01(\x0b\x32&.cometbft.abci.v1beta1.ConsensusParamsR\x0f\x63onsensusParams\x12L\n\nvalidators\x18\x04 \x03(\x0b\x32&.cometbft.abci.v1beta1.ValidatorUpdateB\x04\xc8\xde\x1f\x00R\nvalidators\x12&\n\x0f\x61pp_state_bytes\x18\x05 \x01(\x0cR\rappStateBytes\x12%\n\x0einitial_height\x18\x06 \x01(\x03R\rinitialHeight\"d\n\x0cRequestQuery\x12\x12\n\x04\x64\x61ta\x18\x01 \x01(\x0cR\x04\x64\x61ta\x12\x12\n\x04path\x18\x02 \x01(\tR\x04path\x12\x16\n\x06height\x18\x03 \x01(\x03R\x06height\x12\x14\n\x05prove\x18\x04 \x01(\x08R\x05prove\"\x96\x02\n\x11RequestBeginBlock\x12\x12\n\x04hash\x18\x01 \x01(\x0cR\x04hash\x12<\n\x06header\x18\x02 \x01(\x0b\x32\x1e.cometbft.types.v1beta1.HeaderB\x04\xc8\xde\x1f\x00R\x06header\x12U\n\x10last_commit_info\x18\x03 \x01(\x0b\x32%.cometbft.abci.v1beta1.LastCommitInfoB\x04\xc8\xde\x1f\x00R\x0elastCommitInfo\x12X\n\x14\x62yzantine_validators\x18\x04 \x03(\x0b\x32\x1f.cometbft.abci.v1beta1.EvidenceB\x04\xc8\xde\x1f\x00R\x13\x62yzantineValidators\"X\n\x0eRequestCheckTx\x12\x0e\n\x02tx\x18\x01 \x01(\x0cR\x02tx\x12\x36\n\x04type\x18\x02 \x01(\x0e\x32\".cometbft.abci.v1beta1.CheckTxTypeR\x04type\"\"\n\x10RequestDeliverTx\x12\x0e\n\x02tx\x18\x01 \x01(\x0cR\x02tx\")\n\x0fRequestEndBlock\x12\x16\n\x06height\x18\x01 \x01(\x03R\x06height\"\x0f\n\rRequestCommit\"\x16\n\x14RequestListSnapshots\"n\n\x14RequestOfferSnapshot\x12;\n\x08snapshot\x18\x01 \x01(\x0b\x32\x1f.cometbft.abci.v1beta1.SnapshotR\x08snapshot\x12\x19\n\x08\x61pp_hash\x18\x02 \x01(\x0cR\x07\x61ppHash\"`\n\x18RequestLoadSnapshotChunk\x12\x16\n\x06height\x18\x01 \x01(\x04R\x06height\x12\x16\n\x06\x66ormat\x18\x02 \x01(\rR\x06\x66ormat\x12\x14\n\x05\x63hunk\x18\x03 \x01(\rR\x05\x63hunk\"_\n\x19RequestApplySnapshotChunk\x12\x14\n\x05index\x18\x01 \x01(\rR\x05index\x12\x14\n\x05\x63hunk\x18\x02 \x01(\x0cR\x05\x63hunk\x12\x16\n\x06sender\x18\x03 \x01(\tR\x06sender\"\xc5\t\n\x08Response\x12H\n\texception\x18\x01 \x01(\x0b\x32(.cometbft.abci.v1beta1.ResponseExceptionH\x00R\texception\x12\x39\n\x04\x65\x63ho\x18\x02 \x01(\x0b\x32#.cometbft.abci.v1beta1.ResponseEchoH\x00R\x04\x65\x63ho\x12<\n\x05\x66lush\x18\x03 \x01(\x0b\x32$.cometbft.abci.v1beta1.ResponseFlushH\x00R\x05\x66lush\x12\x39\n\x04info\x18\x04 \x01(\x0b\x32#.cometbft.abci.v1beta1.ResponseInfoH\x00R\x04info\x12I\n\nset_option\x18\x05 \x01(\x0b\x32(.cometbft.abci.v1beta1.ResponseSetOptionH\x00R\tsetOption\x12I\n\ninit_chain\x18\x06 \x01(\x0b\x32(.cometbft.abci.v1beta1.ResponseInitChainH\x00R\tinitChain\x12<\n\x05query\x18\x07 \x01(\x0b\x32$.cometbft.abci.v1beta1.ResponseQueryH\x00R\x05query\x12L\n\x0b\x62\x65gin_block\x18\x08 \x01(\x0b\x32).cometbft.abci.v1beta1.ResponseBeginBlockH\x00R\nbeginBlock\x12\x43\n\x08\x63heck_tx\x18\t \x01(\x0b\x32&.cometbft.abci.v1beta1.ResponseCheckTxH\x00R\x07\x63heckTx\x12I\n\ndeliver_tx\x18\n \x01(\x0b\x32(.cometbft.abci.v1beta1.ResponseDeliverTxH\x00R\tdeliverTx\x12\x46\n\tend_block\x18\x0b \x01(\x0b\x32\'.cometbft.abci.v1beta1.ResponseEndBlockH\x00R\x08\x65ndBlock\x12?\n\x06\x63ommit\x18\x0c \x01(\x0b\x32%.cometbft.abci.v1beta1.ResponseCommitH\x00R\x06\x63ommit\x12U\n\x0elist_snapshots\x18\r \x01(\x0b\x32,.cometbft.abci.v1beta1.ResponseListSnapshotsH\x00R\rlistSnapshots\x12U\n\x0eoffer_snapshot\x18\x0e \x01(\x0b\x32,.cometbft.abci.v1beta1.ResponseOfferSnapshotH\x00R\rofferSnapshot\x12\x62\n\x13load_snapshot_chunk\x18\x0f \x01(\x0b\x32\x30.cometbft.abci.v1beta1.ResponseLoadSnapshotChunkH\x00R\x11loadSnapshotChunk\x12\x65\n\x14\x61pply_snapshot_chunk\x18\x10 \x01(\x0b\x32\x31.cometbft.abci.v1beta1.ResponseApplySnapshotChunkH\x00R\x12\x61pplySnapshotChunkB\x07\n\x05value\")\n\x11ResponseException\x12\x14\n\x05\x65rror\x18\x01 \x01(\tR\x05\x65rror\"(\n\x0cResponseEcho\x12\x18\n\x07message\x18\x01 \x01(\tR\x07message\"\x0f\n\rResponseFlush\"\xb8\x01\n\x0cResponseInfo\x12\x12\n\x04\x64\x61ta\x18\x01 \x01(\tR\x04\x64\x61ta\x12\x18\n\x07version\x18\x02 \x01(\tR\x07version\x12\x1f\n\x0b\x61pp_version\x18\x03 \x01(\x04R\nappVersion\x12*\n\x11last_block_height\x18\x04 \x01(\x03R\x0flastBlockHeight\x12-\n\x13last_block_app_hash\x18\x05 \x01(\x0cR\x10lastBlockAppHash\"M\n\x11ResponseSetOption\x12\x12\n\x04\x63ode\x18\x01 \x01(\rR\x04\x63ode\x12\x10\n\x03log\x18\x03 \x01(\tR\x03log\x12\x12\n\x04info\x18\x04 \x01(\tR\x04info\"\xcf\x01\n\x11ResponseInitChain\x12Q\n\x10\x63onsensus_params\x18\x01 \x01(\x0b\x32&.cometbft.abci.v1beta1.ConsensusParamsR\x0f\x63onsensusParams\x12L\n\nvalidators\x18\x02 \x03(\x0b\x32&.cometbft.abci.v1beta1.ValidatorUpdateB\x04\xc8\xde\x1f\x00R\nvalidators\x12\x19\n\x08\x61pp_hash\x18\x03 \x01(\x0cR\x07\x61ppHash\"\xf8\x01\n\rResponseQuery\x12\x12\n\x04\x63ode\x18\x01 \x01(\rR\x04\x63ode\x12\x10\n\x03log\x18\x03 \x01(\tR\x03log\x12\x12\n\x04info\x18\x04 \x01(\tR\x04info\x12\x14\n\x05index\x18\x05 \x01(\x03R\x05index\x12\x10\n\x03key\x18\x06 \x01(\x0cR\x03key\x12\x14\n\x05value\x18\x07 \x01(\x0cR\x05value\x12\x39\n\tproof_ops\x18\x08 \x01(\x0b\x32\x1c.cometbft.crypto.v1.ProofOpsR\x08proofOps\x12\x16\n\x06height\x18\t \x01(\x03R\x06height\x12\x1c\n\tcodespace\x18\n \x01(\tR\tcodespace\"d\n\x12ResponseBeginBlock\x12N\n\x06\x65vents\x18\x01 \x03(\x0b\x32\x1c.cometbft.abci.v1beta1.EventB\x18\xc8\xde\x1f\x00\xea\xde\x1f\x10\x65vents,omitemptyR\x06\x65vents\"\xe2\x02\n\x0fResponseCheckTx\x12\x12\n\x04\x63ode\x18\x01 \x01(\rR\x04\x63ode\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0cR\x04\x64\x61ta\x12\x10\n\x03log\x18\x03 \x01(\tR\x03log\x12\x12\n\x04info\x18\x04 \x01(\tR\x04info\x12\x1e\n\ngas_wanted\x18\x05 \x01(\x03R\ngas_wanted\x12\x1a\n\x08gas_used\x18\x06 \x01(\x03R\x08gas_used\x12N\n\x06\x65vents\x18\x07 \x03(\x0b\x32\x1c.cometbft.abci.v1beta1.EventB\x18\xc8\xde\x1f\x00\xea\xde\x1f\x10\x65vents,omitemptyR\x06\x65vents\x12\x1c\n\tcodespace\x18\x08 \x01(\tR\tcodespace\x12\x16\n\x06sender\x18\t \x01(\tR\x06sender\x12\x1a\n\x08priority\x18\n \x01(\x03R\x08priority\x12#\n\rmempool_error\x18\x0b \x01(\tR\x0cmempoolError\"\x8b\x02\n\x11ResponseDeliverTx\x12\x12\n\x04\x63ode\x18\x01 \x01(\rR\x04\x63ode\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0cR\x04\x64\x61ta\x12\x10\n\x03log\x18\x03 \x01(\tR\x03log\x12\x12\n\x04info\x18\x04 \x01(\tR\x04info\x12\x1e\n\ngas_wanted\x18\x05 \x01(\x03R\ngas_wanted\x12\x1a\n\x08gas_used\x18\x06 \x01(\x03R\x08gas_used\x12N\n\x06\x65vents\x18\x07 \x03(\x0b\x32\x1c.cometbft.abci.v1beta1.EventB\x18\xc8\xde\x1f\x00\xea\xde\x1f\x10\x65vents,omitemptyR\x06\x65vents\x12\x1c\n\tcodespace\x18\x08 \x01(\tR\tcodespace\"\x9d\x02\n\x10ResponseEndBlock\x12Y\n\x11validator_updates\x18\x01 \x03(\x0b\x32&.cometbft.abci.v1beta1.ValidatorUpdateB\x04\xc8\xde\x1f\x00R\x10validatorUpdates\x12^\n\x17\x63onsensus_param_updates\x18\x02 \x01(\x0b\x32&.cometbft.abci.v1beta1.ConsensusParamsR\x15\x63onsensusParamUpdates\x12N\n\x06\x65vents\x18\x03 \x03(\x0b\x32\x1c.cometbft.abci.v1beta1.EventB\x18\xc8\xde\x1f\x00\xea\xde\x1f\x10\x65vents,omitemptyR\x06\x65vents\"I\n\x0eResponseCommit\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0cR\x04\x64\x61ta\x12#\n\rretain_height\x18\x03 \x01(\x03R\x0cretainHeight\"V\n\x15ResponseListSnapshots\x12=\n\tsnapshots\x18\x01 \x03(\x0b\x32\x1f.cometbft.abci.v1beta1.SnapshotR\tsnapshots\"\xc4\x01\n\x15ResponseOfferSnapshot\x12K\n\x06result\x18\x01 \x01(\x0e\x32\x33.cometbft.abci.v1beta1.ResponseOfferSnapshot.ResultR\x06result\"^\n\x06Result\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06\x41\x43\x43\x45PT\x10\x01\x12\t\n\x05\x41\x42ORT\x10\x02\x12\n\n\x06REJECT\x10\x03\x12\x11\n\rREJECT_FORMAT\x10\x04\x12\x11\n\rREJECT_SENDER\x10\x05\"1\n\x19ResponseLoadSnapshotChunk\x12\x14\n\x05\x63hunk\x18\x01 \x01(\x0cR\x05\x63hunk\"\x9e\x02\n\x1aResponseApplySnapshotChunk\x12P\n\x06result\x18\x01 \x01(\x0e\x32\x38.cometbft.abci.v1beta1.ResponseApplySnapshotChunk.ResultR\x06result\x12%\n\x0erefetch_chunks\x18\x02 \x03(\rR\rrefetchChunks\x12%\n\x0ereject_senders\x18\x03 \x03(\tR\rrejectSenders\"`\n\x06Result\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06\x41\x43\x43\x45PT\x10\x01\x12\t\n\x05\x41\x42ORT\x10\x02\x12\t\n\x05RETRY\x10\x03\x12\x12\n\x0eRETRY_SNAPSHOT\x10\x04\x12\x13\n\x0fREJECT_SNAPSHOT\x10\x05\"\x97\x02\n\x0f\x43onsensusParams\x12\x38\n\x05\x62lock\x18\x01 \x01(\x0b\x32\".cometbft.abci.v1beta1.BlockParamsR\x05\x62lock\x12\x42\n\x08\x65vidence\x18\x02 \x01(\x0b\x32&.cometbft.types.v1beta1.EvidenceParamsR\x08\x65vidence\x12\x45\n\tvalidator\x18\x03 \x01(\x0b\x32\'.cometbft.types.v1beta1.ValidatorParamsR\tvalidator\x12?\n\x07version\x18\x04 \x01(\x0b\x32%.cometbft.types.v1beta1.VersionParamsR\x07version\"C\n\x0b\x42lockParams\x12\x1b\n\tmax_bytes\x18\x01 \x01(\x03R\x08maxBytes\x12\x17\n\x07max_gas\x18\x02 \x01(\x03R\x06maxGas\"c\n\x0eLastCommitInfo\x12\x14\n\x05round\x18\x01 \x01(\x05R\x05round\x12;\n\x05votes\x18\x02 \x03(\x0b\x32\x1f.cometbft.abci.v1beta1.VoteInfoB\x04\xc8\xde\x1f\x00R\x05votes\"\x80\x01\n\x05\x45vent\x12\x12\n\x04type\x18\x01 \x01(\tR\x04type\x12\x63\n\nattributes\x18\x02 \x03(\x0b\x32%.cometbft.abci.v1beta1.EventAttributeB\x1c\xc8\xde\x1f\x00\xea\xde\x1f\x14\x61ttributes,omitemptyR\nattributes\"N\n\x0e\x45ventAttribute\x12\x10\n\x03key\x18\x01 \x01(\x0cR\x03key\x12\x14\n\x05value\x18\x02 \x01(\x0cR\x05value\x12\x14\n\x05index\x18\x03 \x01(\x08R\x05index\"\x90\x01\n\x08TxResult\x12\x16\n\x06height\x18\x01 \x01(\x03R\x06height\x12\x14\n\x05index\x18\x02 \x01(\rR\x05index\x12\x0e\n\x02tx\x18\x03 \x01(\x0cR\x02tx\x12\x46\n\x06result\x18\x04 \x01(\x0b\x32(.cometbft.abci.v1beta1.ResponseDeliverTxB\x04\xc8\xde\x1f\x00R\x06result\";\n\tValidator\x12\x18\n\x07\x61\x64\x64ress\x18\x01 \x01(\x0cR\x07\x61\x64\x64ress\x12\x14\n\x05power\x18\x03 \x01(\x03R\x05power\"e\n\x0fValidatorUpdate\x12<\n\x07pub_key\x18\x01 \x01(\x0b\x32\x1d.cometbft.crypto.v1.PublicKeyB\x04\xc8\xde\x1f\x00R\x06pubKey\x12\x14\n\x05power\x18\x02 \x01(\x03R\x05power\"|\n\x08VoteInfo\x12\x44\n\tvalidator\x18\x01 \x01(\x0b\x32 .cometbft.abci.v1beta1.ValidatorB\x04\xc8\xde\x1f\x00R\tvalidator\x12*\n\x11signed_last_block\x18\x02 \x01(\x08R\x0fsignedLastBlock\"\x89\x02\n\x08\x45vidence\x12\x37\n\x04type\x18\x01 \x01(\x0e\x32#.cometbft.abci.v1beta1.EvidenceTypeR\x04type\x12\x44\n\tvalidator\x18\x02 \x01(\x0b\x32 .cometbft.abci.v1beta1.ValidatorB\x04\xc8\xde\x1f\x00R\tvalidator\x12\x16\n\x06height\x18\x03 \x01(\x03R\x06height\x12\x38\n\x04time\x18\x04 \x01(\x0b\x32\x1a.google.protobuf.TimestampB\x08\xc8\xde\x1f\x00\x90\xdf\x1f\x01R\x04time\x12,\n\x12total_voting_power\x18\x05 \x01(\x03R\x10totalVotingPower\"\x82\x01\n\x08Snapshot\x12\x16\n\x06height\x18\x01 \x01(\x04R\x06height\x12\x16\n\x06\x66ormat\x18\x02 \x01(\rR\x06\x66ormat\x12\x16\n\x06\x63hunks\x18\x03 \x01(\rR\x06\x63hunks\x12\x12\n\x04hash\x18\x04 \x01(\x0cR\x04hash\x12\x1a\n\x08metadata\x18\x05 \x01(\x0cR\x08metadata*9\n\x0b\x43heckTxType\x12\x10\n\x03NEW\x10\x00\x1a\x07\x8a\x9d \x03New\x12\x18\n\x07RECHECK\x10\x01\x1a\x0b\x8a\x9d \x07Recheck*H\n\x0c\x45videnceType\x12\x0b\n\x07UNKNOWN\x10\x00\x12\x12\n\x0e\x44UPLICATE_VOTE\x10\x01\x12\x17\n\x13LIGHT_CLIENT_ATTACK\x10\x02\x32\xb7\x0b\n\x0f\x41\x42\x43IApplication\x12O\n\x04\x45\x63ho\x12\".cometbft.abci.v1beta1.RequestEcho\x1a#.cometbft.abci.v1beta1.ResponseEcho\x12R\n\x05\x46lush\x12#.cometbft.abci.v1beta1.RequestFlush\x1a$.cometbft.abci.v1beta1.ResponseFlush\x12O\n\x04Info\x12\".cometbft.abci.v1beta1.RequestInfo\x1a#.cometbft.abci.v1beta1.ResponseInfo\x12^\n\tSetOption\x12\'.cometbft.abci.v1beta1.RequestSetOption\x1a(.cometbft.abci.v1beta1.ResponseSetOption\x12^\n\tDeliverTx\x12\'.cometbft.abci.v1beta1.RequestDeliverTx\x1a(.cometbft.abci.v1beta1.ResponseDeliverTx\x12X\n\x07\x43heckTx\x12%.cometbft.abci.v1beta1.RequestCheckTx\x1a&.cometbft.abci.v1beta1.ResponseCheckTx\x12R\n\x05Query\x12#.cometbft.abci.v1beta1.RequestQuery\x1a$.cometbft.abci.v1beta1.ResponseQuery\x12U\n\x06\x43ommit\x12$.cometbft.abci.v1beta1.RequestCommit\x1a%.cometbft.abci.v1beta1.ResponseCommit\x12^\n\tInitChain\x12\'.cometbft.abci.v1beta1.RequestInitChain\x1a(.cometbft.abci.v1beta1.ResponseInitChain\x12\x61\n\nBeginBlock\x12(.cometbft.abci.v1beta1.RequestBeginBlock\x1a).cometbft.abci.v1beta1.ResponseBeginBlock\x12[\n\x08\x45ndBlock\x12&.cometbft.abci.v1beta1.RequestEndBlock\x1a\'.cometbft.abci.v1beta1.ResponseEndBlock\x12j\n\rListSnapshots\x12+.cometbft.abci.v1beta1.RequestListSnapshots\x1a,.cometbft.abci.v1beta1.ResponseListSnapshots\x12j\n\rOfferSnapshot\x12+.cometbft.abci.v1beta1.RequestOfferSnapshot\x1a,.cometbft.abci.v1beta1.ResponseOfferSnapshot\x12v\n\x11LoadSnapshotChunk\x12/.cometbft.abci.v1beta1.RequestLoadSnapshotChunk\x1a\x30.cometbft.abci.v1beta1.ResponseLoadSnapshotChunk\x12y\n\x12\x41pplySnapshotChunk\x12\x30.cometbft.abci.v1beta1.RequestApplySnapshotChunk\x1a\x31.cometbft.abci.v1beta1.ResponseApplySnapshotChunkB8Z6github.com/cometbft/cometbft/api/cometbft/abci/v1beta1b\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'cometbft.abci.v1beta1.types_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
  _globals['DESCRIPTOR']._loaded_options = None
  _globals['DESCRIPTOR']._serialized_options = b'Z6github.com/cometbft/cometbft/api/cometbft/abci/v1beta1'
  _globals['_CHECKTXTYPE'].values_by_name["NEW"]._loaded_options = None
  _globals['_CHECKTXTYPE'].values_by_name["NEW"]._serialized_options = b'\212\235 \003New'
  _globals['_CHECKTXTYPE'].values_by_name["RECHECK"]._loaded_options = None
  _globals['_CHECKTXTYPE'].values_by_name["RECHECK"]._serialized_options = b'\212\235 \007Recheck'
  _globals['_REQUESTINITCHAIN'].fields_by_name['time']._loaded_options = None
  _globals['_REQUESTINITCHAIN'].fields_by_name['time']._serialized_options = b'\310\336\037\000\220\337\037\001'
  _globals['_REQUESTINITCHAIN'].fields_by_name['validators']._loaded_options = None
  _globals['_REQUESTINITCHAIN'].fields_by_name['validators']._serialized_options = b'\310\336\037\000'
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['header']._loaded_options = None
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['header']._serialized_options = b'\310\336\037\000'
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['last_commit_info']._loaded_options = None
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['last_commit_info']._serialized_options = b'\310\336\037\000'
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['byzantine_validators']._loaded_options = None
  _globals['_REQUESTBEGINBLOCK'].fields_by_name['byzantine_validators']._serialized_options = b'\310\336\037\000'
  _globals['_RESPONSEINITCHAIN'].fields_by_name['validators']._loaded_options = None
  _globals['_RESPONSEINITCHAIN'].fields_by_name['validators']._serialized_options = b'\310\336\037\000'
  _globals['_RESPONSEBEGINBLOCK'].fields_by_name['events']._loaded_options = None
  _globals['_RESPONSEBEGINBLOCK'].fields_by_name['events']._serialized_options = b'\310\336\037\000\352\336\037\020events,omitempty'
  _globals['_RESPONSECHECKTX'].fields_by_name['events']._loaded_options = None
  _globals['_RESPONSECHECKTX'].fields_by_name['events']._serialized_options = b'\310\336\037\000\352\336\037\020events,omitempty'
  _globals['_RESPONSEDELIVERTX'].fields_by_name['events']._loaded_options = None
  _globals['_RESPONSEDELIVERTX'].fields_by_name['events']._serialized_options = b'\310\336\037\000\352\336\037\020events,omitempty'
  _globals['_RESPONSEENDBLOCK'].fields_by_name['validator_updates']._loaded_options = None
  _globals['_RESPONSEENDBLOCK'].fields_by_name['validator_updates']._serialized_options = b'\310\336\037\000'
  _globals['_RESPONSEENDBLOCK'].fields_by_name['events']._loaded_options = None
  _globals['_RESPONSEENDBLOCK'].fields_by_name['events']._serialized_options = b'\310\336\037\000\352\336\037\020events,omitempty'
  _globals['_LASTCOMMITINFO'].fields_by_name['votes']._loaded_options = None
  _globals['_LASTCOMMITINFO'].fields_by_name['votes']._serialized_options = b'\310\336\037\000'
  _globals['_EVENT'].fields_by_name['attributes']._loaded_options = None
  _globals['_EVENT'].fields_by_name['attributes']._serialized_options = b'\310\336\037\000\352\336\037\024attributes,omitempty'
  _globals['_TXRESULT'].fields_by_name['result']._loaded_options = None
  _globals['_TXRESULT'].fields_by_name['result']._serialized_options = b'\310\336\037\000'
  _globals['_VALIDATORUPDATE'].fields_by_name['pub_key']._loaded_options = None
  _globals['_VALIDATORUPDATE'].fields_by_name['pub_key']._serialized_options = b'\310\336\037\000'
  _globals['_VOTEINFO'].fields_by_name['validator']._loaded_options = None
  _globals['_VOTEINFO'].fields_by_name['validator']._serialized_options = b'\310\336\037\000'
  _globals['_EVIDENCE'].fields_by_name['validator']._loaded_options = None
  _globals['_EVIDENCE'].fields_by_name['validator']._serialized_options = b'\310\336\037\000'
  _globals['_EVIDENCE'].fields_by_name['time']._loaded_options = None
  _globals['_EVIDENCE'].fields_by_name['time']._serialized_options = b'\310\336\037\000\220\337\037\001'
  _globals['_CHECKTXTYPE']._serialized_start=8132
  _globals['_CHECKTXTYPE']._serialized_end=8189
  _globals['_EVIDENCETYPE']._serialized_start=8191
  _globals['_EVIDENCETYPE']._serialized_end=8263
  _globals['_REQUEST']._serialized_start=252
  _globals['_REQUEST']._serialized_end=1383
  _globals['_REQUESTECHO']._serialized_start=1385
  _globals['_REQUESTECHO']._serialized_end=1424
  _globals['_REQUESTFLUSH']._serialized_start=1426
  _globals['_REQUESTFLUSH']._serialized_end=1440
  _globals['_REQUESTINFO']._serialized_start=1442
  _globals['_REQUESTINFO']._serialized_end=1551
  _globals['_REQUESTSETOPTION']._serialized_start=1553
  _globals['_REQUESTSETOPTION']._serialized_end=1611
  _globals['_REQUESTINITCHAIN']._serialized_start=1614
  _globals['_REQUESTINITCHAIN']._serialized_end=1957
  _globals['_REQUESTQUERY']._serialized_start=1959
  _globals['_REQUESTQUERY']._serialized_end=2059
  _globals['_REQUESTBEGINBLOCK']._serialized_start=2062
  _globals['_REQUESTBEGINBLOCK']._serialized_end=2340
  _globals['_REQUESTCHECKTX']._serialized_start=2342
  _globals['_REQUESTCHECKTX']._serialized_end=2430
  _globals['_REQUESTDELIVERTX']._serialized_start=2432
  _globals['_REQUESTDELIVERTX']._serialized_end=2466
  _globals['_REQUESTENDBLOCK']._serialized_start=2468
  _globals['_REQUESTENDBLOCK']._serialized_end=2509
  _globals['_REQUESTCOMMIT']._serialized_start=2511
  _globals['_REQUESTCOMMIT']._serialized_end=2526
  _globals['_REQUESTLISTSNAPSHOTS']._serialized_start=2528
  _globals['_REQUESTLISTSNAPSHOTS']._serialized_end=2550
  _globals['_REQUESTOFFERSNAPSHOT']._serialized_start=2552
  _globals['_REQUESTOFFERSNAPSHOT']._serialized_end=2662
  _globals['_REQUESTLOADSNAPSHOTCHUNK']._serialized_start=2664
  _globals['_REQUESTLOADSNAPSHOTCHUNK']._serialized_end=2760
  _globals['_REQUESTAPPLYSNAPSHOTCHUNK']._serialized_start=2762
  _globals['_REQUESTAPPLYSNAPSHOTCHUNK']._serialized_end=2857
  _globals['_RESPONSE']._serialized_start=2860
  _globals['_RESPONSE']._serialized_end=4081
  _globals['_RESPONSEEXCEPTION']._serialized_start=4083
  _globals['_RESPONSEEXCEPTION']._serialized_end=4124
  _globals['_RESPONSEECHO']._serialized_start=4126
  _globals['_RESPONSEECHO']._serialized_end=4166
  _globals['_RESPONSEFLUSH']._serialized_start=4168
  _globals['_RESPONSEFLUSH']._serialized_end=4183
  _globals['_RESPONSEINFO']._serialized_start=4186
  _globals['_RESPONSEINFO']._serialized_end=4370
  _globals['_RESPONSESETOPTION']._serialized_start=4372
  _globals['_RESPONSESETOPTION']._serialized_end=4449
  _globals['_RESPONSEINITCHAIN']._serialized_start=4452
  _globals['_RESPONSEINITCHAIN']._serialized_end=4659
  _globals['_RESPONSEQUERY']._serialized_start=4662
  _globals['_RESPONSEQUERY']._serialized_end=4910
  _globals['_RESPONSEBEGINBLOCK']._serialized_start=4912
  _globals['_RESPONSEBEGINBLOCK']._serialized_end=5012
  _globals['_RESPONSECHECKTX']._serialized_start=5015
  _globals['_RESPONSECHECKTX']._serialized_end=5369
  _globals['_RESPONSEDELIVERTX']._serialized_start=5372
  _globals['_RESPONSEDELIVERTX']._serialized_end=5639
  _globals['_RESPONSEENDBLOCK']._serialized_start=5642
  _globals['_RESPONSEENDBLOCK']._serialized_end=5927
  _globals['_RESPONSECOMMIT']._serialized_start=5929
  _globals['_RESPONSECOMMIT']._serialized_end=6002
  _globals['_RESPONSELISTSNAPSHOTS']._serialized_start=6004
  _globals['_RESPONSELISTSNAPSHOTS']._serialized_end=6090
  _globals['_RESPONSEOFFERSNAPSHOT']._serialized_start=6093
  _globals['_RESPONSEOFFERSNAPSHOT']._serialized_end=6289
  _globals['_RESPONSEOFFERSNAPSHOT_RESULT']._serialized_start=6195
  _globals['_RESPONSEOFFERSNAPSHOT_RESULT']._serialized_end=6289
  _globals['_RESPONSELOADSNAPSHOTCHUNK']._serialized_start=6291
  _globals['_RESPONSELOADSNAPSHOTCHUNK']._serialized_end=6340
  _globals['_RESPONSEAPPLYSNAPSHOTCHUNK']._serialized_start=6343
  _globals['_RESPONSEAPPLYSNAPSHOTCHUNK']._serialized_end=6629
  _globals['_RESPONSEAPPLYSNAPSHOTCHUNK_RESULT']._serialized_start=6533
  _globals['_RESPONSEAPPLYSNAPSHOTCHUNK_RESULT']._serialized_end=6629
  _globals['_CONSENSUSPARAMS']._serialized_start=6632
  _globals['_CONSENSUSPARAMS']._serialized_end=6911
  _globals['_BLOCKPARAMS']._serialized_start=6913
  _globals['_BLOCKPARAMS']._serialized_end=6980
  _globals['_LASTCOMMITINFO']._serialized_start=6982
  _globals['_LASTCOMMITINFO']._serialized_end=7081
  _globals['_EVENT']._serialized_start=7084
  _globals['_EVENT']._serialized_end=7212
  _globals['_EVENTATTRIBUTE']._serialized_start=7214
  _globals['_EVENTATTRIBUTE']._serialized_end=7292
  _globals['_TXRESULT']._serialized_start=7295
  _globals['_TXRESULT']._serialized_end=7439
  _globals['_VALIDATOR']._serialized_start=7441
  _globals['_VALIDATOR']._serialized_end=7500
  _globals['_VALIDATORUPDATE']._serialized_start=7502
  _globals['_VALIDATORUPDATE']._serialized_end=7603
  _globals['_VOTEINFO']._serialized_start=7605
  _globals['_VOTEINFO']._serialized_end=7729
  _globals['_EVIDENCE']._serialized_start=7732
  _globals['_EVIDENCE']._serialized_end=7997
  _globals['_SNAPSHOT']._serialized_start=8000
  _globals['_SNAPSHOT']._serialized_end=8130
  _globals['_ABCIAPPLICATION']._serialized_start=8266
  _globals['_ABCIAPPLICATION']._serialized_end=9729
# @@protoc_insertion_point(module_scope)
