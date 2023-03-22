package component

import (
	// "bytes"
	// "encoding/json"
	"externalc2/pkg/config"
)

type ComponentManifest struct {
	Os       string
	Hostname string
	Arch     string
}

type Component struct {
	ComponentId string
	SendQueue   []byte
	RecvQueue   []byte
	// ConfigKey []byte  //TODO: Crypto
	TransportChannel *chan []byte
	Config           config.ExternalConfig
	Manifest         ComponentManifest
}

type Command struct {
	Type string
	Args string
}
