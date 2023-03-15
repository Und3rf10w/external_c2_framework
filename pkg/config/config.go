package config

import (
// "log"
)

type ExternalConfig struct {
	Id            string
	TransportName string
	TskChkTimer   int
}

// func ReadConfig(config []byte, xKey int, symKey []byte) symmetric.SymmetricMessage {
// 	config = xor.XorMessage(config, xKey)
// 	rdyConfig := symmetric.Decrypt(config, symKey)
// 	if rdyConfig.IsEncrypted {
// 		log.Fatalln("failed to decode config")
// 	}
// 	return rdyConfig
// }
