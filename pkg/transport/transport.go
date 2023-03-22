package transport

import (
	"fmt"
	"log"

	"externalc2/pkg/component"
	"externalc2/pkg/transport/revtcptransport"
	"externalc2/pkg/utils/idgen"
	"externalc2/pkg/utils/logging"
)

type RegisteredComponent struct {
	Transport        TransportMethod
	Id               string
	SelfComponentId  string
	CmdChannel       chan []byte
	TskChkTimer      int
	TransportChannel chan []byte
	Type             string
}

type TransportMethod interface {
	Initalize(Component *RegisteredComponent) (bool, error)
	Send(CmdChannel chan []byte) (bool, error)
	Recv(CmdChannel chan []byte) ([]byte, bool, error)
}

var transportMethods map[string]func([]string) (TransportMethod, bool, error)

func NewError(text string) error {
	return &UnsupportedTransportError{text}
}

type UnsupportedTransportError struct {
	s string
}

func (e *UnsupportedTransportError) Error() string {
	return e.s
}

type UnsupportedTransportMethod struct {
	Method    string
	Arguments []string
}

func (t *UnsupportedTransportMethod) Initalize(Component *RegisteredComponent) (bool, error) {
	err := &UnsupportedTransportError{}
	return false, err
}

func (t *UnsupportedTransportMethod) Send(CmdChannel chan []byte) (bool, error) {
	return false, nil
}

func (t *UnsupportedTransportMethod) Recv(CmdChannel chan []byte) ([]byte, bool, error) {
	return nil, false, nil
}

func newUnsupportedTransportMethod(arguments []string) (TransportMethod, bool, error) {
	return &UnsupportedTransportMethod{"UNSUPPORTED", []string{}}, false, &UnsupportedTransportError{}
}

func (t *RevTCPTransportMethod) Initalize(Component *RegisteredComponent) (bool, error) {
	// Do you initalization stuff here for your transport
	//  for example:
	// RevTCPTransportMethod.Initalize(Transport)
	return true, nil
}

func (t *RevTCPTransportMethod) Send(CmdChannel chan []byte) (bool, error) {
	err := revtcptransport.Send(CmdChannel)
	if err != nil {
		return false, err
	}
	return true, nil
}

func (t *RevTCPTransportMethod) Recv(CmdChannel chan []byte) ([]byte, bool, error) {
	data, err := revtcptransport.Recv(CmdChannel)
	if err != nil {
		return nil, false, err
	}
	return data, true, nil
}

func newRevTCPTransportMethod(arugments []string) (TransportMethod, bool, error) {
	return &RevTCPTransportMethod{"rev_tcp", idgen.GenerateTxId(), "127.0.0.1:30000"}, true, nil
}

type RevTCPTransportMethod struct {
	Method      string
	TransportId string
	BindAddress string
}

// Add Transport Structs, Initalize(), Send(), Recv(), and new*Transport functions here

func init() {
	transportMethods = make(map[string]func([]string) (TransportMethod, bool, error))
	// add new methods here
	transportMethods["UNSUPPORTED"] = newUnsupportedTransportMethod
	transportMethods["rev_tcp"] = newRevTCPTransportMethod
	// methods["new_transport"] = newXTransportMethod  // example
}

func getTransport(method string, arguments []string, Component *component.Component) (TransportMethod, bool, error) {
	factory, ok := transportMethods[method]
	if !ok {
		return nil, false, fmt.Errorf("transport '%s' not found", method)
	}
	return factory(arguments)
}

func PrepareTransport(Component *component.Component, methodArgs []string) (TransportMethod, bool, error) {
	log.SetPrefix(logging.GetLogPrefix())
	transport, _, err := getTransport(Component.Config.TransportName, methodArgs, Component)
	if err != nil {
		log.Println("invalid arguments for PrepareTransport: ", err)
	}
	// boolSuccess, err := TransportMethod.Initalize(transport, Component)
	return transport, true, err
}
