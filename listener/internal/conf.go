package internal

import (
	"github.com/xixiwang12138/exermon/conf"
	"os"
)

type Config struct {
	conf.Config
}

func LoadConfig() *Config {
	env := os.Getenv("ENV")
	if env == "" {
		env = string(conf.DEV)
	}
	token := os.Getenv("CONSUL_TOKEN")
	source := conf.NewConsulSource[Config]("lazybet", "https://consul.circuit.money", token)
	return source.ReadConf(conf.ENVType(env))
}
