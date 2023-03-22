//go:build server && !client

package external

import (
	"externalc2/pkg/component"
	"externalc2/pkg/instructions"
	"externalc2/pkg/transport"
	"log"
)

type clientInitFrameArgs struct {
	manifest component.Component // TODO: componentmanifest most likely
}

type registerClientstruct struct {
	InitArgs  clientInitFrameArgs
	Interface transport.TransportMethod
	Id        string
}

func writeToChannel(channel chan []byte, data []byte) {
	channel <- data
}

func readFromChannel(channel chan []byte) []byte {
	data := <-channel
	return data
}

func readFromTransport(server transport.RegisteredComponent, Component *component.Component) ([]byte, bool, error) {
	data, boolSuccess, err := server.Transport.Recv(server.CmdChannel)
	if !boolSuccess {
		log.Println("failed to receive from channel: ", err)
		return data, false, err
	}
	return data, true, nil
}
