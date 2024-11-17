package internal

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"github.com/xixiwang12138/exermon/db"
	"github.com/xixiwang12138/exermon/db/op"
	"gorm.io/gorm"
	"io/ioutil"
	"log"
	"net/http"
	"time"
)

const AIServiceURL = "http://localhost:8001"

type AITrigger struct {
	betRepo *db.BaseDao[Bet]
}

func NewAITrigger(g *gorm.DB) *AITrigger {
	return &AITrigger{
		betRepo: db.NewBaseDao[Bet](g),
	}
}

func (t *AITrigger) scanBet() ([]*Bet, error) {
	sec := time.Now().Unix()
	ctx := context.Background()
	return t.betRepo.Instance(ctx).List(op.Filter(op.Lt("end_time", sec), op.Eq("judged", false)))
}

type BetRequest struct {
    Address     string   `json:"address"`
	Description string   `json:"description"`
	Urls        []string `json:"urls"`
}

type BetResponse struct {
	Verdict bool `json:"verdict"`
}

func (t *AITrigger) triggerAI(bet *Bet) error {

	println("Trigger AI for bet: ", bet.Address)

	requestData := BetRequest{
	    Address: bet.Address,
		Description: bet.Message,
		Urls:        []string{},
	}

	requestBody, err := json.Marshal(requestData)
	if err != nil {
		fmt.Printf("Error marshaling request data: %v\n", err)
		return err
	}

	url := fmt.Sprintf("%s/judge_bet", AIServiceURL)
	resp, err := http.Post(url, "application/json", bytes.NewBuffer(requestBody))
	if err != nil {
		fmt.Printf("Error making POST request: %v\n", err)
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Error: received status code %d\n", resp.StatusCode)
		body, _ := ioutil.ReadAll(resp.Body)
		fmt.Printf("Response body: %s\n", string(body))
		return err
	}

	responseData := &BetResponse{}
	if err := json.NewDecoder(resp.Body).Decode(responseData); err != nil {
		fmt.Printf("Error decoding response: %v\n", err)
		return err
	}

	bet.Judged = true

	return t.betRepo.Instance(context.Background()).Save(bet, op.Eq("id", bet.ID))
}

func (t *AITrigger) ScanAndTriggerAI() {
	bets, err := t.scanBet()
	if err != nil {
		log.Printf("Failed to scan bets: %v", err)
	}

	for _, bet := range bets {
		err := t.triggerAI(bet)
		if err != nil {
			log.Printf("Failed to trigger AI: %v", err)
		}
	}
}

func (t *AITrigger) StartTriggerLoop() {
	for {
		t.ScanAndTriggerAI()
		time.Sleep(10 * time.Second)
	}
}
