package config

// "log"

type ExternalConfig struct {
	Id            string
	TransportName string
	TskChkTimer   int
	Destination   string // basically used for pipename so I can stay with one type of config
}

// TODO: config crypto
// func ReadConfig(config []byte, xKey int, symKey []byte) symmetric.SymmetricMessage {
// 	config = xor.XorMessage(config, xKey)
// 	rdyConfig := symmetric.Decrypt(config, symKey)
// 	if rdyConfig.IsEncrypted {
// 		log.Fatalln("failed to decode config")
// 	}
// 	return rdyConfig
// }
