package internal

import (
	"context"
	"fmt"
	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"log"
	"math/big"
	"strings"
)

const (
	lazyBetABI = `[
		{"constant":true,"inputs":[],"name":"initiator","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},
		{"constant":true,"inputs":[],"name":"judge","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},
		{"constant":true,"inputs":[],"name":"token","outputs":[{"name":"","type":"address"}],"stateMutability":"view","type":"function"},
		{"constant":true,"inputs":[],"name":"message","outputs":[{"name":"","type":"string"}],"stateMutability":"view","type":"function"},
		{"constant":true,"inputs":[],"name":"endTime","outputs":[{"name":"","type":"uint256"}],"stateMutability":"view","type":"function"},
		{"constant":true,"inputs":[],"name":"state","outputs":[{"name":"","type":"uint8"}],"stateMutability":"view","type":"function"}
	]`
)

type BetQuery struct {
	client *ethclient.Client
	abi    abi.ABI
	//contractAddr common.Address
}

func NewBetQuery() *BetQuery {
	client, err := ethclient.Dial(rpcURL)
	if err != nil {
		log.Fatalf("Failed to connect to the Ethereum client: %v", err)
	}

	// Parse the ABI
	parsedABI, err := abi.JSON(strings.NewReader(lazyBetABI))
	if err != nil {
		log.Fatalf("Failed to parse ABI: %v", err)
	}

	return &BetQuery{
		client: client,
		abi:    parsedABI,
	}
}

func (q *BetQuery) GetBetByAddress(address common.Address) (*Bet, error) {
	ret := &Bet{
		Address: address.Hex(),
	}

	judgeItf, err := q.callContract(address, "judge")
	if err != nil {
		return nil, err
	}
	ret.Judge = judgeItf.(common.Address).Hex()

	endTimeItf, err := q.callContract(address, "endTime")
	if err != nil {
		return nil, err
	}
	ret.EndTime = endTimeItf.(*big.Int).Int64()

	messageItf, err := q.callContract(address, "message")
	if err != nil {
		return nil, err
	}
	ret.Message = messageItf.(string)

	return ret, nil
}

func (q *BetQuery) callContract(addr common.Address, method string) (interface{}, error) {
	callData, err := q.abi.Pack(method)
	if err != nil {
		return nil, fmt.Errorf("failed to pack method: %v", err)
	}

	msg := ethereum.CallMsg{
		To:   &addr,
		Data: callData,
	}

	output, err := q.client.CallContract(context.Background(), msg, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to call contract: %v", err)
	}

	var result interface{}
	err = q.abi.UnpackIntoInterface(&result, method, output)
	if err != nil {
		return nil, fmt.Errorf("failed to unpack result: %v", err)
	}

	return result, nil
}
