package httpquic

import (
	"crypto"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"fmt"
	"io"
	"log"
	"math/big"
	"net/http"
	"os"
	"strings"
	"time"

	// External C2
	"externalc2/pkg/transport"
	"externalc2/pkg/utils/logging"

	// 3rd Party
	"github.com/quic-go/quic-go"
	"github.com/quic-go/quic-go/http3"
	"golang.org/x/sync/errgroup"
)

type quicServer struct {
	Transport interface{}
	Interface string
	Port      int
	Protocol  int
	State     int
}

type Context struct {
}

type HTTPContext struct {
	Context
}

type Server struct {
	quicServer
	x509Cert string
	x509Key  string
	urls     []string
	ctx      *Context
}

// Begin shameless Merlin TLS utils rip
/*
GenerateTLSCert will generate a new certificate. Nil values in the parameters are replaced with random or blank values.
If makeRsa is set to true, the key generated is an RSA key (EC by default).
If a nil date is passed in for notBefore and notAfter, a random date is picked in the last year.
If a nil date is passed in for notAfter, the date is set to be 2 years after the date provided (or generated) in the notBefore parameter.
Please ensure privkey is a proper private key. The go implementation of this value is challenging, so no type assertion can be made in the function definition.
*/
func GenerateTLSCert(serial *big.Int, subject *pkix.Name, dnsNames []string, notBefore, notAfter *time.Time, privKey crypto.PrivateKey, makeRsa bool) (*tls.Certificate, error) {
	//https://golang.org/src/crypto/tls/generate_cert.go taken from here mostly
	var err error

	if serial == nil {
		serialNumberLimit := new(big.Int).Lsh(big.NewInt(1), 128) //128 bits tops
		serial, err = rand.Int(rand.Reader, serialNumberLimit)
		if err != nil {
			return nil, err
		}
	}

	if subject == nil { //pointers make it easier to compare to nils
		subject = &pkix.Name{} //todo: generate random subject attributes?
	}

	//todo: generate random names?

	if notBefore == nil {

		randDay, err := rand.Int(rand.Reader, big.NewInt(360)) //not 365, playing it safe... time and computers are hard
		if err != nil {
			return nil, err
		}

		b4 := time.Now().AddDate(0, 0, -1*int(randDay.Int64())) //random date sometime in the last year
		notBefore = &b4
	}

	if notAfter == nil {
		aft := notBefore.AddDate(2, 0, 0) //2 years after the notbefore date
		notAfter = &aft
	}

	tpl := x509.Certificate{
		SerialNumber:          serial,
		Subject:               *subject,
		DNSNames:              dnsNames,
		NotBefore:             *notBefore,
		NotAfter:              *notAfter,
		KeyUsage:              x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature | x509.KeyUsageCertSign,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
	}
	if privKey == nil {
		if makeRsa {
			privKey, err = rsa.GenerateKey(rand.Reader, 4096)
			if err != nil {
				return nil, err
			}
		} else {
			privKey, err = ecdsa.GenerateKey(elliptic.P384(), rand.Reader) //maybe check to see if P384 is the right choice (would want to be the most common choice for ec curves)
			if err != nil {
				return nil, err
			}
		}
	}

	crtBytes, err := x509.CreateCertificate(rand.Reader, &tpl, &tpl, getPublicKey(privKey), privKey)
	if err != nil {
		return nil, err
	}

	return &tls.Certificate{
		Certificate: [][]byte{crtBytes},
		PrivateKey:  privKey,
	}, nil
}

// GetTLSCertificates parses PEM encoded input x.509 certificate and key file paths as a string and returns a tls object
func GetTLSCertificates(certificate string, key string) (*tls.Certificate, error) {
	var cer tls.Certificate
	var err error

	// Check if x.509 certificate file exists on disk
	_, errCrt := os.Stat(certificate)
	if errCrt != nil {
		return &cer, fmt.Errorf("there was an error importing the SSL/TLS x509 certificate:\r\n%s", errCrt.Error())
	}

	// Check if x.509 key file exists on disk
	_, errKey := os.Stat(key)
	if errKey != nil {
		return &cer, fmt.Errorf("there was an error importing the SSL/TLS x509 key:: %s", errKey.Error())
	}

	cer, err = tls.LoadX509KeyPair(certificate, key)
	if err != nil {
		return &cer, fmt.Errorf("there was an error importing the SSL/TLS x509 key pair\r\n%s", err.Error())
	}

	if len(cer.Certificate) < 1 || cer.PrivateKey == nil {
		return &cer, fmt.Errorf("unable to import certificate because the certificate structure was empty")
	}
	return &cer, nil
}

// getPublicKey takes in a private key, and provides the public key from it.
// https://golang.org/src/crypto/tls/generate_cert.go
func getPublicKey(priv interface{}) interface{} {
	switch k := priv.(type) {
	case *rsa.PrivateKey:
		return &k.PublicKey
	case *ecdsa.PrivateKey:
		return &k.PublicKey
	default:
		return nil
	}
}

func newServer() (*Server, error) {
	var s Server
	var certificates *tls.Certificate
	var err error

	s.Protocol = 3
	// s.Port, err = strconv.Atoi() // TODO: Take in options
	s.Port = 6666

	certificates, err = GetTLSCertificates("server.pem", "key.pem") // TODO: Take in options
	if err != nil {
		return nil, err
	}

	mux := http.NewServeMux()

	s.urls = []string{"/"}

	// s.ctx = &HTTPContext{} // TODO: Look at merlin handlers.HTTPContext

	mux.HandleFunc("/", getRoot)
	// Add your additional function handlers here
	mux.HandleFunc("/reg", getRegister)

	s.Transport = &http3.Server{
		Addr:           "0.0.0.0:6666",
		Port:           s.Port,
		Handler:        mux,
		MaxHeaderBytes: 1 << 20,
		TLSConfig:      &tls.Config{Certificates: []tls.Certificate{*certificates}, MinVersion: tls.VersionTLS12},
		QuicConfig: &quic.Config{
			// Long timeout to prevent the client from sending a HTTP/2 PING frame
			MaxIdleTimeout:  time.Until(time.Now().AddDate(0, 69, 0)),
			KeepAlivePeriod: time.Second * 0,
		},
	}
	return &s, nil
}

// End shameless Merlin Rip

func getRoot(w http.ResponseWriter, r *http.Request) {
	log.Println("[httpquic]: /")
	io.WriteString(w, "It works!\n")
}

func getRegister(w http.ResponseWriter, r *http.Request) {
	log.Println("[httpquic]: /reg")
}

func (s *Server) serve(Component *transport.RegisteredComponent) (bool, error) {
	// mux := http.NewServeMux()
	// mux.HandleFunc("/", getRoot)

	// // err := http.ListenAndServe(":6666", mux)
	// // TODO: Resolve cert and privkey paths
	// err := http3.ListenAndServeQUIC(":6666", "cert.pem", "privkey.pem", mux)
	// if err != nil {
	// 	return false, err
	// }
	// return true, err

	// var s *Server
	var g errgroup.Group

	// TODO: Setup s *Server here

	// Catch Panic
	// TODO: FIXME
	defer func() {
		if r := recover(); r != nil {
			log.Fatalln("The server panicked")
		}
	}()

	g.Go(func() error {
		if s.x509Key != "" && s.x509Cert != "" {
			return s.Transport.(*http3.Server).ListenAndServeTLS(s.x509Cert, s.x509Key)
		}
		return s.Transport.(*http3.Server).ListenAndServe()
	})

	if err := g.Wait(); err != nil {
		if !strings.Contains(strings.ToLower(err.Error()), "server closed") {
			return false, fmt.Errorf("The server panicked")
		}
	}
	return true, nil
}

func (s *Server) Stop() error {
	err := s.Transport.(*http3.Server).Close()
	if err != nil {
		return fmt.Errorf("")
	}
	return nil
}

func connect(Component *transport.RegisteredComponent) (bool, error) {
	// TODO: Connection logic
	return true, nil
}

func Initalize(Component *transport.RegisteredComponent) (bool, error) {
	log.SetPrefix(logging.GetLogPrefix())
	if Component.Type == "server" {
		server := new(Server)
		// This is a server
		boolSuccess, err := server.serve(Component)
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
