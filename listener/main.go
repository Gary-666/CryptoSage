package main

import (
	"github.com/xixiwang12138/exermon/db"
	"github.com/xixiwang12138/exermon/elog"
	"cryptosage-listener/internal"
	"os"
)

func main() {
	cf := internal.LoadConfig()
	db.Setup(cf.Mysql)
	elog.Setup(cf.LogConfig)

	if os.Getenv("SYNC") == "true" {
		db.Component.SyncRdsStruct(&internal.Bet{})
	} else {
		g := db.Component.Gorm()

		indexer := internal.NewBetIndexer(g)
		go indexer.StartIndexLoop()

		trigger := internal.NewAITrigger(g)
		trigger.StartTriggerLoop()
	}

}
