package internal

import (
	"context"
	"github.com/ethereum/go-ethereum"
	"github.com/xixiwang12138/exermon/db"
	"gorm.io/gorm"
	"log"
	"strings"

	"github.com/ethereum/go-ethereum/accounts/abi"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
)

const (
	// Sepolia RPC URL

	lazyBetFactoryABI = `[
		{"anonymous":false,"inputs":[
			{"indexed":true,"internalType":"address","name":"betAddress","type":"address"},
			{"indexed":true,"internalType":"address","name":"initiator","type":"address"}
		],"name":"BetCreated","type":"event"}
	]`

	contractAddress = "0x11165e9afa37d76c6d032961c63d14ee8efd68c7"
)

type BetIndexer struct {
	betRepo *db.BaseDao[Bet]
	query   *BetQuery
}

func NewBetIndexer(g *gorm.DB) *BetIndexer {
	return &BetIndexer{
		betRepo: db.NewBaseDao[Bet](g),
		query:   NewBetQuery(),
	}
}

func (i *BetIndexer) StartIndexLoop() {
	for {
		err := i.IndexBet()
		log.Printf("Indexer exited: %v", err)
	}
}

func (i *BetIndexer) IndexBet() error {
	// Connect to Sepolia
	client, err := ethclient.Dial(wsRpcURL)
	if err != nil {
		log.Fatalf("Failed to connect to the Ethereum client: %v", err)
	}

	// Parse the ABI
	parsedABI, err := abi.JSON(strings.NewReader(lazyBetFactoryABI))
	if err != nil {
		log.Fatalf("Failed to parse ABI: %v", err)
	}

	// Create a filter query
	query := ethereum.FilterQuery{
		Addresses: []common.Address{common.HexToAddress(contractAddress)},
	}

	// Subscribe to logs

	logs := make(chan types.Log)
	sub, err := client.SubscribeFilterLogs(context.Background(), query, logs)
	if err != nil {
		log.Fatalf("Failed to subscribe to logs: %v", err)
	}

	log.Println("Listening for BetCreated events...")
	for {
		select {
		case err := <-sub.Err():
			log.Printf("Subscription error: %v", err) // possible EOF
			return err
		case vLog := <-logs:
			// Parse the event
			event := struct {
				BetAddress common.Address
				Initiator  common.Address
			}{}
			err := parsedABI.UnpackIntoInterface(&event, "BetCreated", vLog.Data)
			if err != nil {
				log.Printf("Failed to unpack log: %v", err)
				continue
			}

			// Access indexed fields
			event.BetAddress = common.BytesToAddress(vLog.Topics[1].Bytes())
			event.Initiator = common.BytesToAddress(vLog.Topics[2].Bytes())

			log.Printf("New BetCreated Event:\n")

			bet, err := i.query.GetBetByAddress(event.BetAddress)
			if err != nil {
				log.Printf("Failed to get bet by address: %v", err)
				continue
			}

			err = i.betRepo.Instance(context.Background()).Insert(bet)
			if err != nil {
				log.Printf("Failed to insert bet: %v", err)
				continue
			}

			log.Printf("Bet inserted: %v", bet.Address)
		}
	}

}

func (i *BetIndexer) notifyBet(bet *Bet) {

}
