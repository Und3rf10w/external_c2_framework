//go:build client && !server

package ipc

// This is basically https://github.com/davidelorenzoli/named-pipe-ipc/

import (
	"bytes"
	"io"
	"log"
	"os"

	"externalc2/pkg/utils/logging"
)

// Open a named pipe for reading
func Read(namedPipe string) (string, error) {
	log.SetPrefix(logging.GetLogPrefix())
	stdout, _ := os.OpenFile(namedPipe, os.O_RDONLY, 0600)
	var buff bytes.Buffer

	if _, err := io.Copy(&buff, stdout); err != nil {
		log.Printf("failed to read pipe. Error: %s", err)
		return "", err
	}

	if err := stdout.Close(); err != nil {
		log.Printf("failed to close stream. Error: %s", err)
	}

	return buff.String(), nil
}

// Write to the named pipe
func Write(namedPipe string, content chan []byte) error {
	log.SetPrefix(logging.GetLogPrefix())
	stdout, _ := os.OpenFile(namedPipe, os.O_RDWR, 0600)
	data := <-content
	if _, err := stdout.Write(data); err != nil {
		log.Printf("error writing bytes %s", err.Error())
		return err
	}
	if err := stdout.Close(); err != nil {
		log.Printf("error closing writer: %s", err.Error())
		return err
	}
	return nil
}
