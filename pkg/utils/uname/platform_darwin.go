package uname

import (
	"golang.org/x/sys/unix"
)

type Uname struct {
	Sysname  string
	Version  string
	Nodename string
	Release  string
	Machine  string
}

// Contains information about the platform Shlyuz is running on
type PlatformInfo struct {
	Uname Uname
}

func byte256ToStr(arr [256]byte) string {
	b := make([]byte, 0, len(arr))
	for _, v := range arr {
		if v == 0 {
			break
		}
		b = append(b, byte(v))
	}
	return string(b)
}

// Converts system information to PlatformInfo struct via unix.Utsname
func platinfo() Uname {
	var uname unix.Utsname
	platUname := new(Uname)
	if err := unix.Uname(&uname); err == nil {
		// darwin doesn't have a Utsname.Domainname
		//  variant of: https://stackoverflow.com/a/53197771
		// type Utsname struct {
		//  Sysname    [256]byte
		//  Nodename   [265]byte
		//  Release    [265]byte
		//  Version    [265]byte
		//  Machine    [265]byte
		//  Domainname [265]byte
		// }
		platUname.Sysname = byte256ToStr(uname.Sysname)
		platUname.Version = byte256ToStr(uname.Version)
		platUname.Nodename = byte256ToStr(uname.Nodename)
		platUname.Release = byte256ToStr(uname.Release)
		platUname.Machine = byte256ToStr(uname.Machine)
	}
	return *platUname
}

// Returns operating system version information
func GetUname() *PlatformInfo {
	uname := new(PlatformInfo)
	uname.Uname = platinfo()
	return uname
}
