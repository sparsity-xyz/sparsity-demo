import grpc
from concurrent import futures
import cometbft.abci.v1.service_pb2_grpc as service_pb2_grpc
import cometbft.abci.v1.types_pb2 as types_pb2


class BaseABCIService(service_pb2_grpc.ABCIServiceServicer):
    CodeTypeOK = 0
    EncodingError = 1
    InvalidTxFormat = 2
    Banned = 3

    def __init__(self, port=26658):
        self.port = port

    def Echo(self, request, context):
        return types_pb2.EchoResponse(message=request.message)

    def Flush(self, request, context):
        return types_pb2.FlushResponse()

    def Info(self, request, context):
        return types_pb2.InfoResponse()

    def CheckTx(self, request, context):
        return types_pb2.CheckTxResponse(code=self.CodeTypeOK)

    def Query(self, request, context):
        return types_pb2.QueryResponse(code=self.CodeTypeOK)

    def Commit(self, request, context):
        return types_pb2.CommitResponse()

    def InitChain(self, request, context):
        return types_pb2.InitChainResponse()

    def ListSnapshots(self, request, context):
        return types_pb2.ListSnapshotsResponse()

    def OfferSnapshot(self, request, context):
        return types_pb2.OfferSnapshotResponse()

    def LoadSnapshotChunk(self, request, context):
        return types_pb2.LoadSnapshotChunkResponse()

    def ApplySnapshotChunk(self, request, context):
        return types_pb2.ApplySnapshotChunkResponse()

    def PrepareProposal(self, request, context):
        txs = []
        total_bytes = 0
        for tx in request.txs:
            total_bytes += len(tx)
            if total_bytes > request.max_tx_bytes:
                break
            txs.append(tx)
        return types_pb2.PrepareProposalResponse(txs=txs)

    def ProcessProposal(self, request, context):
        return types_pb2.ProcessProposalResponse(status=types_pb2.ProcessProposalStatus.PROCESS_PROPOSAL_STATUS_ACCEPT)

    def ExtendVote(self, request, context):
        return types_pb2.ExtendVoteResponse()

    def VerifyVoteExtension(self, request, context):
        return types_pb2.VerifyVoteExtensionResponse(
            status=types_pb2.VerifyVoteExtensionStatus.VERIFY_VOTE_EXTENSION_STATUS_ACCEPT)

    def FinalizeBlock(self, request, context):
        txs = []
        for _ in request.txs:
            txs.append(types_pb2.ExecTxResult(code=self.CodeTypeOK))
        return types_pb2.FinalizeBlockResponse(tx_results=txs)

    def start(self):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_ABCIServiceServicer_to_server(self, server)
        server.add_insecure_port(f"[::]:{self.port}")
        server.start()
        print(f"gRPC Server running on port {self.port}...")
        server.wait_for_termination()


if __name__ == "__main__":
    BaseABCIService().start()
