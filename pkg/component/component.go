package component

import (
	// "bytes"
	// "encoding/json"
	"externalc2/pkg/config"
)

type Component struct {
	ComponentId      string
	SendQueue        []byte
	RecvQueue        []byte
	TransportChannel chan []byte
	Config           config.ExternalConfig
}
