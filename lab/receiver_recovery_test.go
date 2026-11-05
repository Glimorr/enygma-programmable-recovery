package handler_test

// Synthetic receiver-level retry test against unmodified official Go source.
// Fake receipts and mock persistence only. NOT actual NATS, CTS, or EVM evidence.
import (
    "context"
    "errors"
    "math/big"
    "testing"

    "github.com/ethereum/go-ethereum/common"
    "github.com/raylsnetwork/rayls-sovereign-relayer/types"
    "github.com/stretchr/testify/require"
)

func TestEnygmaReceiverPendingResubmitsAfterConfirmationFailure(t *testing.T) {
    deps := setupReceiverDeps()
    deps.EndpointClient.GetResourceAddressFunc = func(_ context.Context,_ string)(common.Address,error) {
        return common.HexToAddress("0x6666666666666666666666666666666666666666"),nil
    }
    deps.HistoryRepository.InsertEnygmaHistoryFunc = func(context.Context,types.EnygmaHistory)error {
        return nil
    }
    state := types.HistoryStatusPending
    deps.TxRecoveryRepository.GetByPrivateHubTxHashFunc =
        func(_ context.Context,_ string)(*types.TxRecoveryData,error) {
            return &types.TxRecoveryData{Status:state},nil
        }
    deps.TxRecoveryRepository.MarkConfirmedFunc = func(_ context.Context,_ string)error {
        state=types.HistoryStatusConfirmed
        return nil
    }
    deps.HandlerClient.ReceiveDestTransferBatchFunc=makeSuccessfulMint()
    notifications:=0
    deps.TeleportClient.SendTransferCompletedFunc =
        func(_ context.Context,_ []types.EnygmaTransferCompleted)error {
            notifications++
            if notifications==1 {return errors.New("LAB_SIMULATED_COMPLETION_TRANSPORT_FAILURE")}
            return nil
        }
    batch:=createBatch(big.NewInt(2),big.NewInt(1),1)
    batch.PrivateHubTxHash="0x9999999999999999999999999999999999999999999999999999999999999999"
    originalMsgID:=batch.Transactions[0].MessageId
    receiver:=setupReceiver(deps)
    err:=receiver.HandleEnygmaCrossTransfer(context.Background(),batch)
    require.ErrorContains(t,err,"LAB_SIMULATED_COMPLETION_TRANSPORT_FAILURE")
    require.Equal(t,types.HistoryStatusPending,state)
    require.Len(t,deps.HandlerClient.ReceiveDestTransferBatchCalls(),1)
    require.Equal(t,originalMsgID,deps.HandlerClient.ReceiveDestTransferBatchCalls()[0].Transfers[0].MessageId)

    // Retry same batch after a mock transport failure. This is test code
    // invoking the handler twice, not demonstrated NATS redelivery.
    require.NoError(t,receiver.HandleEnygmaCrossTransfer(context.Background(),batch))
    require.Equal(t,types.HistoryStatusConfirmed,state)
    require.Len(t,deps.HandlerClient.ReceiveDestTransferBatchCalls(),2,
        "Pending receiver recovery calls batch executor a second time")
    require.Equal(t,originalMsgID,deps.HandlerClient.ReceiveDestTransferBatchCalls()[1].Transfers[0].MessageId)
    require.Len(t,deps.TeleportClient.SendTransferCompletedCalls(),2)

    require.NoError(t,receiver.HandleEnygmaCrossTransfer(context.Background(),batch))
    require.Len(t,deps.HandlerClient.ReceiveDestTransferBatchCalls(),2,
        "Confirmed receiver recovery correctly skips further dispatch")
}
