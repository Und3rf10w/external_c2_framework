package serverconfig

import (
	"externalc2/pkg/config"
	"log"
	"strconv"

	"gopkg.in/ini.v1"
)

func ParseConfig(configToParse []byte) config.ExternalConfig {
	var ParsedConfig config.ExternalConfig
	cfg, err := ini.LoadconfigToParse(configToParse)
	if err != nil {
		log.Fatalln("failed to load config: ", err)
	}
	serverSec, err := cfg.GetSection("server")
	if err != nil {
		log.Fatalln("failed to read config section: ", err)
	}

	ParsedConfig.Id = serverSec.Key("id").String()
	ParsedConfig.TransportName = serverSec.Key("transport_name").String()
	ParsedConfig.TskChkTimer, err = strconv.Atoi(serverSec.Key("task_check_time").Value())
	if err != nil {
		log.Fatalln("failed to parse config value timer: ", err)
	}

	return ParsedConfig
}
