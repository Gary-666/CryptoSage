package internal

import (
	"gorm.io/gorm"
)

type BetState uint8 // None, Open, Closed, Cancelled

const (
	BetStateNone BetState = iota
	BetStateOpen
	BetStateClosed    // AI judged
	BetStateCancelled // initiator cancelled
)

type Bet struct {
	gorm.Model

	Initiator string `gorm:"type:VARCHAR(96)"`

	Message string

	Address string `gorm:"type:VARCHAR(96)"`
	Judge   string `gorm:"type:VARCHAR(96)"`

	Judged bool

	EndTime int64
}
