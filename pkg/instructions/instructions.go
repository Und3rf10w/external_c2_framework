package instructions

type ServerInstruction struct {
	Cmd       string
	FrameData []byte
}

type BeaconPipeMessage struct {
	PipeName    string
	MessageData []byte
}
