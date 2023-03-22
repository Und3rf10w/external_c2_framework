package exec

import (
	"encoding/json"
	"log"

	"externalc2/pkg/component"
	"externalc2/pkg/instructions"
	"externalc2/pkg/ipc"
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"
)

type cmdArgs struct {
	Cmd  int // 1=ii
	Args component.Command
}

func RouteCmd(client *transport.RegisteredComponent, instruction instructions.ServerInstruction) {
	log.SetPrefix(logging.GetLogPrefix())
	var parsedCmd cmdArgs
	err := json.Unmarshal([]byte(instruction.FrameData), &parsedCmd)
	if err != nil {
		log.Println("unable to unmarshal parsed cmd: ", err)
	}

	switch cmd := parsedCmd.Cmd; cmd {
	// TODO: Do the injection
	case 1: //inject the implant
		// injection.Injection
	}
}
