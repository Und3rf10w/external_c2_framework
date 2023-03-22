//go:build client

package clientconfig

import (
	"externalc2/pkg/config"
	"log"
	"strconv"

	"gopkg.in/ini.v1"
)

func ParseConfig(configToParse []byte) config.ExternalConfig {
	// TODO: Config Crypto
	var ParsedConfig config.ExternalConfig
	cfg, err := ini.Load(configToParse)
	if err != nil {
		log.Fatalln("failed to load config: ", err)
	}
	clientSec, err := cfg.GetSection("client")
	if err != nil {
		log.Fatalln("failed to read config section: ", err)
	}

	ParsedConfig.Id = clientSec.Key("id").String()
	ParsedConfig.TransportName = clientSec.Key("transport_name").String()
	ParsedConfig.TskChkTimer, err = strconv.Atoi(clientSec.Key("task_check_time").Value())
	ParsedConfig.Destination = clientSec.Key("pipe_name").String()
	if err != nil {
		log.Fatalln("failed to parse config value timer: ", err)
	}

	return ParsedConfig
}
