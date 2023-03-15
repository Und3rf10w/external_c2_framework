package logging

import (
	"log"
	"time"
)

func GetLogPrefix() string {
	log.SetFlags(log.Lmsgprefix)
	// pc, _, _, _ := runtime.Caller(1)
	// return "[" + time.Now().UTC().Format(time.RFC3339) + "] " + "<" + runtime.FuncForPC(pc).Name() + "> "
	//   TODO: There HAS to be a way to do this right, but that's a problem for future me
	return "[" + time.Now().UTC().Format(time.RFC3339) + "] "
}
