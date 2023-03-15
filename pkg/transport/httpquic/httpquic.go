package httpquic

import (
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"
	"io"
	"log"
	"net/http"

	"github.com/quic-go/quic-go/http3"
)

type quicServer struct {
	Interface string
	Port      int
	Protocol  int
	State     int
}

type Context struct {
}

type Server struct {
	quicServer
	x509Cert string
	x509Key  string
	urls     []string
	ctx      *Context
}

func getRoot(w http.ResponseWriter, r *http.Request) {
	log.Println("[httpquic]: /")
	io.WriteString(w, "It works!\n")
}

func getRegister(w http.ResponseWriter, r *http.Request) {
	log.Println("[httpquic]: ")
}

func serve(Component *transport.RegisteredComponent) (bool, error) {
	mux := http.NewServeMux()
	mux.HandleFunc("/", getRoot)

	// err := http.ListenAndServe(":6666", mux)
	// TODO: Resolve cert and privkey paths
	err := http3.ListenAndServeQUIC(":6666", "cert.pem", "privkey.pem", mux)
	if err != nil {
		return false, err
	}
	return true, err
}

func connect(Component *transport.RegisteredComponent) (bool, error) {
	// TODO: Connection logic
	return true, nil
}

func newServer() (*Server, error) {
	var s Server
}

func Initalize(Component *transport.RegisteredComponent) (bool, error) {
	log.SetPrefix(logging.GetLogPrefix())
	if Component.Type == "server" {
		// This is a server
		boolSuccess, err := serve(Component)
		if err != nil {
			log.Println("failed to setup httpquic server: ", err)
			return boolSuccess, err
		}
	} else {
		// This is a client
		boolSuccess, err := connect(Component)
		if err != nil {
			log.Println("failed to connect to httpquic server: ", err)
			return boolSuccess, err
		}
	}

	return true, nil
}
