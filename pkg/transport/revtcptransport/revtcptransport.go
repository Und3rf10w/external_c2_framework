package revtcptransport

import (
	"log"
)

type TransportInfo struct {
	Name        string
	Author      string
	Description string
	Version     string
}

type Transport interface {
	Info() TransportInfo
}

func connectToCs() string {
	// TODO
	log.Println("Something went wrong")
	return "ok"
}

func Send(CmdChannel chan []byte) error {
	// TODO
	return nil
}

func Recv(CmdChannel chan []byte) ([]byte, error) {
	// TODO
	return nil, nil
}
